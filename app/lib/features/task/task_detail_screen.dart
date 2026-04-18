import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';

import '../../data/api/reward_repository.dart';
import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/models.dart';
import '../../providers.dart';
import 'reward_picker_sheet.dart';

String _sexParam(Sex sex) => switch (sex) {
      Sex.boy => "male",
      Sex.girl => "female",
      Sex.other => "any",
    };

({IconData icon, String label, Color color}) _categoryMeta(String cat) =>
    switch (cat) {
      'financial' => (
          icon: Icons.payments_outlined,
          label: 'Financial',
          color: const Color(0xFF1565C0),
        ),
      'household' => (
          icon: Icons.home_outlined,
          label: 'Household',
          color: const Color(0xFF2E7D32),
        ),
      'digital' => (
          icon: Icons.devices_outlined,
          label: 'Digital',
          color: const Color(0xFF6A1B9A),
        ),
      'navigation' => (
          icon: Icons.explore_outlined,
          label: 'Navigation',
          color: const Color(0xFFE65100),
        ),
      'cognitive' => (
          icon: Icons.lightbulb_outlined,
          label: 'Thinking',
          color: const Color(0xFF00695C),
        ),
      'social' => (
          icon: Icons.people_outlined,
          label: 'Social',
          color: const Color(0xFFC62828),
        ),
      _ => (
          icon: Icons.category_outlined,
          label: cat.isEmpty ? 'Skill' : cat[0].toUpperCase() + cat.substring(1),
          color: const Color(0xFF546E7A),
        ),
    };

// FutureProvider that looks up a task by slug, falling back to a fresh fetch
// if the cache is cold (e.g. after app restart or deep-link into detail).
final _taskDetailProvider =
    FutureProvider.family<Task?, String>((ref, slug) async {
  final repo = ref.read(taskRepositoryProvider);
  final cached = repo.cached;
  if (cached != null) {
    for (final t in cached) {
      if (t.slug == slug) return t;
    }
  }
  final activeId = ref.read(activeChildIdProvider);
  final child = HiveSetup.childBox.get(activeId);
  if (child == null) return null;
  final tasks = await repo.fetchAll(
    environment: child.environment.name,
    sex: _sexParam(child.sex),
  );
  for (final t in tasks) {
    if (t.slug == slug) return t;
  }
  return null;
});

class TaskDetailScreen extends ConsumerStatefulWidget {
  const TaskDetailScreen({super.key, required this.taskSlug});
  final String taskSlug;

  @override
  ConsumerState<TaskDetailScreen> createState() => _TaskDetailState();
}

class _TaskDetailState extends ConsumerState<TaskDetailScreen> {
  @override
  Widget build(BuildContext context) {
    final asyncTask = ref.watch(_taskDetailProvider(widget.taskSlug));
    // Trigger rebuilds when any progress changes
    ref.watch(progressVersionProvider);

    return asyncTask.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text("Loading…")),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (e, _) => _buildErrorScaffold("Couldn't load this skill: $e"),
      data: (task) {
        if (task == null) {
          return _buildErrorScaffold(
            "This skill isn't in the catalog anymore.",
          );
        }
        return _buildScaffold(task);
      },
    );
  }

  Widget _buildErrorScaffold(String message) {
    return Scaffold(
      appBar: AppBar(title: const Text("Skill")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline, size: 48, color: Colors.grey.shade500),
              const SizedBox(height: 12),
              Text(message, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () =>
                    ref.invalidate(_taskDetailProvider(widget.taskSlug)),
                child: const Text("Retry"),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => context.pop(),
                child: const Text("Go back"),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildScaffold(Task task) {
    final activeId = ref.read(activeChildIdProvider);
    final child = HiveSetup.childBox.get(activeId)!;
    final progressKey = TaskProgress.key(child.id, task.slug);
    final existing = HiveSetup.progressBox.get(progressKey);

    final rewardKey = 'reward::${child.id}::${task.slug}';
    final savedReward = HiveSetup.sessionBox.get(rewardKey) as String?;

    final countKey = 'count::${child.id}::${task.slug}';
    final practiceCount = (HiveSetup.sessionBox.get(countKey) as int?) ?? 0;

    final isCompleted = existing?.status == ProgressStatus.completed;
    final isBypassed = existing?.status == ProgressStatus.bypassed;
    final isSkippedKnown = existing?.status == ProgressStatus.skippedKnown;
    final isSkippedUnsuitable =
        existing?.status == ProgressStatus.skippedUnsuitable;
    final isSkipped = isSkippedKnown || isSkippedUnsuitable;
    final isMastered = isCompleted || isBypassed;
    final isActive = !isMastered && !isSkipped;

    final required = task.repetitionsRequired;
    final category =
        task.tags.isEmpty ? 'other' : task.tags.first.category;

    // Prereq titles (for "Builds on" display)
    final catalog = ref.read(taskRepositoryProvider).cached ?? const <Task>[];
    final titleBySlug = {for (final t in catalog) t.slug: t.title};
    final prereqTitles = <String>[];
    for (final p in task.prerequisites) {
      if (!p.isMandatory) continue;
      final title = titleBySlug[p.taskSlug];
      if (title != null) prereqTitles.add(title);
    }

    // Is there a softSkipped mandatory prereq? If so, show warning banner
    String? warningPrereqTitle;
    for (final p in task.prerequisites) {
      if (!p.isMandatory) continue;
      final prog = HiveSetup.progressBox.get(TaskProgress.key(child.id, p.taskSlug));
      if (prog?.status == ProgressStatus.skippedKnown) {
        warningPrereqTitle = titleBySlug[p.taskSlug];
        break;
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(task.title, overflow: TextOverflow.ellipsis),
        actions: [
          if (isActive)
            PopupMenuButton<String>(
              tooltip: "Skip options",
              icon: const Icon(Icons.more_vert),
              onSelected: (val) => _handleSkipOption(task, child.id, val),
              itemBuilder: (_) => const [
                PopupMenuItem(
                  value: 'known',
                  child: ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    leading: Icon(Icons.psychology_outlined, size: 20),
                    title: Text("My child already knows this"),
                  ),
                ),
                PopupMenuItem(
                  value: 'unsuitable',
                  child: ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    leading: Icon(Icons.not_interested, size: 20),
                    title: Text("Not right for my child"),
                  ),
                ),
              ],
            ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
        children: [
          // ── Skipped banner (when applicable) ────────────────────
          if (isSkipped) _SkippedBanner(status: existing!.status),
          if (isSkipped) const SizedBox(height: 16),

          // ── Warning banner for lockedWithWarning ────────────────
          if (isActive && warningPrereqTitle != null) ...[
            _WarningBanner(prereqTitle: warningPrereqTitle),
            const SizedBox(height: 16),
          ],

          // ── Context chips: category + age ───────────────────────
          _ContextChips(
            category: category,
            minAge: task.minAge,
            maxAge: task.maxAge,
          ),
          const SizedBox(height: 10),

          // ── Prereq chain (if any) ───────────────────────────────
          if (prereqTitles.isNotEmpty) ...[
            _BuildsOnRow(titles: prereqTitles),
            const SizedBox(height: 14),
          ],

          // ── Mastered card (if completed/bypassed) ───────────────
          if (isMastered) ...[
            _SkillMasteredCard(
              completedAt: existing?.completedAt,
              practiceCount: practiceCount,
              totalRequired: required,
              lastReward: savedReward ?? "",
              isBypassed: isBypassed,
              onReset: () => _confirmReset(task, child.id),
            ),
            const SizedBox(height: 20),
          ],

          // ── Practice progress (active tasks needing multiple sessions) ─
          if (isActive && required > 1) ...[
            _PracticeProgress(done: practiceCount, total: required),
            const SizedBox(height: 20),
          ],

          // ── How to ──────────────────────────────────────────────
          _SectionHeader(label: "How to"),
          MarkdownBody(
            data: task.howToMd,
            shrinkWrap: true,
            onTapLink: (text, href, title) => _handleLinkTap(href),
          ),

          // ── Safety ──────────────────────────────────────────────
          if (task.safetyMd.isNotEmpty) ...[
            const SizedBox(height: 24),
            _SectionHeader(label: "Safety"),
            Card(
              color: Colors.amber.shade50,
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(color: Colors.amber.shade200),
              ),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: MarkdownBody(
                  data: task.safetyMd,
                  shrinkWrap: true,
                  onTapLink: (text, href, title) => _handleLinkTap(href),
                ),
              ),
            ),
          ],

          // ── Parent note / "Why this matters" ────────────────────
          if (task.parentNoteMd.isNotEmpty) ...[
            const SizedBox(height: 24),
            _ParentNoteCard(
              content: task.parentNoteMd,
              onTapLink: _handleLinkTap,
              isAdult: child.isAdult,
            ),
          ],
        ],
      ),
      bottomNavigationBar: _buildBottomBar(
        isActive: isActive,
        isSkipped: isSkipped,
        isMastered: isMastered,
        practiceCount: practiceCount,
        task: task,
        childId: child.id,
      ),
    );
  }

  Widget? _buildBottomBar({
    required bool isActive,
    required bool isSkipped,
    required bool isMastered,
    required int practiceCount,
    required Task task,
    required String childId,
  }) {
    if (isMastered) return null;

    return SafeArea(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Theme.of(context).scaffoldBackgroundColor,
          border: Border(top: BorderSide(color: Colors.grey.shade200)),
        ),
        child: isSkipped
            ? FilledButton.icon(
                icon: const Icon(Icons.restore),
                label: const Text("Bring back to ladder"),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  minimumSize: const Size.fromHeight(48),
                ),
                onPressed: () => _bringBack(task, childId),
              )
            : FilledButton.icon(
                icon: const Icon(Icons.check_circle_outline),
                label: Text(
                    practiceCount == 0 ? "Mark as Practised" : "Practise Again"),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  minimumSize: const Size.fromHeight(48),
                ),
                onPressed: () => _markPractised(task, childId),
              ),
      ),
    );
  }

  // ── Actions ────────────────────────────────────────────────────────

  Future<void> _markPractised(Task task, String childId) async {
    final child = HiveSetup.childBox.get(childId)!;
    final reward = await showModalBottomSheet<String?>(
      context: context,
      isScrollControlled: true,
      builder: (_) => RewardPickerSheet(childId: childId),
    );
    if (reward == null) return;

    // Capture pre-change state for undo
    final countKey = 'count::$childId::${task.slug}';
    final rewardKey = 'reward::$childId::${task.slug}';
    final prevCount = (HiveSetup.sessionBox.get(countKey) as int?) ?? 0;
    final prevReward = HiveSetup.sessionBox.get(rewardKey) as String?;
    final progressKey = TaskProgress.key(childId, task.slug);
    final prevProgress = HiveSetup.progressBox.get(progressKey);

    final newCount = prevCount + 1;
    await HiveSetup.sessionBox.put(countKey, newCount);
    await HiveSetup.sessionBox.put(rewardKey, reward);

    final isFullyDone = newCount >= task.repetitionsRequired;
    if (isFullyDone) {
      await HiveSetup.progressBox.put(
        progressKey,
        TaskProgress(
          taskSlug: task.slug,
          childId: childId,
          status: ProgressStatus.completed,
          completedAt: DateTime.now(),
        ),
      );
    }

    ref.read(progressVersionProvider.notifier).state++;

    unawaited(ref.read(_postCompletionProvider((
      taskSlug: task.slug,
      ageBand: child.ageBand(DateTime.now()),
      environment: child.environment.name,
    )).future));

    if (!mounted) return;
    final shareMsg = isFullyDone
        ? _buildShareMessage(
            child.name,
            task.title,
            reward,
            isAdult: child.isAdult,
          )
        : "";
    await showModalBottomSheet(
      context: context,
      isDismissible: false,
      enableDrag: false,
      isScrollControlled: true,
      builder: (_) => _CelebrationSheet(
        childName: child.name,
        taskTitle: task.title,
        reward: reward,
        shareMessage: shareMsg,
        practiceNumber: newCount,
        totalRequired: task.repetitionsRequired,
        isFullyDone: isFullyDone,
        isAdult: child.isAdult,
      ),
    );

    if (!mounted) return;
    if (isFullyDone) {
      // When fully done we navigate back; no undo SnackBar since the user
      // now sees the dashboard. The Skill Mastered card on return to detail
      // offers a Reset option instead.
      context.pop();
    } else {
      _showUndoSnack(
        message: "Practise #$newCount saved.",
        onUndo: () async {
          await HiveSetup.sessionBox.put(countKey, prevCount);
          if (prevReward == null) {
            await HiveSetup.sessionBox.delete(rewardKey);
          } else {
            await HiveSetup.sessionBox.put(rewardKey, prevReward);
          }
          if (prevProgress == null) {
            await HiveSetup.progressBox.delete(progressKey);
          } else {
            await HiveSetup.progressBox.put(progressKey, prevProgress);
          }
          ref.read(progressVersionProvider.notifier).state++;
        },
      );
    }
  }

  Future<void> _handleSkipOption(
      Task task, String childId, String value) async {
    if (value == 'known') {
      await _skipKnown(task, childId);
    } else if (value == 'unsuitable') {
      await _skipUnsuitable(task, childId);
    }
  }

  Future<void> _skipKnown(Task task, String childId) async {
    final confirmed = await _confirmDialog(
      title: "Mark as already known?",
      body:
          "\"${task.title}\" will be treated as mastered. Future skills that build on it will still appear — with a small warning so you can double-check readiness. You can bring this skill back anytime.",
      confirmLabel: "Mark as known",
    );
    if (!confirmed || !mounted) return;
    await HiveSetup.progressBox.put(
      TaskProgress.key(childId, task.slug),
      TaskProgress(
        taskSlug: task.slug,
        childId: childId,
        status: ProgressStatus.skippedKnown,
      ),
    );
    ref.read(progressVersionProvider.notifier).state++;
    if (mounted) context.pop();
  }

  Future<void> _skipUnsuitable(Task task, String childId) async {
    final confirmed = await _confirmDialog(
      title: "Hide this skill?",
      body:
          "\"${task.title}\" will be hidden from the ladder, along with any future skill that requires it first. Use this if the skill isn't appropriate for your child. You can bring it back anytime from the Skipped section.",
      confirmLabel: "Hide",
      destructive: true,
    );
    if (!confirmed || !mounted) return;
    await HiveSetup.progressBox.put(
      TaskProgress.key(childId, task.slug),
      TaskProgress(
        taskSlug: task.slug,
        childId: childId,
        status: ProgressStatus.skippedUnsuitable,
      ),
    );
    ref.read(progressVersionProvider.notifier).state++;
    if (mounted) context.pop();
  }

  Future<void> _bringBack(Task task, String childId) async {
    await HiveSetup.progressBox.delete(TaskProgress.key(childId, task.slug));
    ref.read(progressVersionProvider.notifier).state++;
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Skill is back in the ladder.")),
    );
  }

  Future<void> _confirmReset(Task task, String childId) async {
    final confirmed = await _confirmDialog(
      title: "Reset this skill?",
      body:
          "Progress for \"${task.title}\" will be cleared so it can be practised again. Practice count and saved reward will also be reset.",
      confirmLabel: "Reset",
      destructive: true,
    );
    if (!confirmed || !mounted) return;
    await HiveSetup.progressBox.delete(TaskProgress.key(childId, task.slug));
    await HiveSetup.sessionBox.delete('count::$childId::${task.slug}');
    await HiveSetup.sessionBox.delete('reward::$childId::${task.slug}');
    ref.read(progressVersionProvider.notifier).state++;
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Skill reset — ready to practise again.")),
    );
  }

  Future<bool> _confirmDialog({
    required String title,
    required String body,
    required String confirmLabel,
    bool destructive = false,
  }) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(title),
        content: Text(body),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          FilledButton(
            style: destructive
                ? FilledButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.error,
                  )
                : null,
            onPressed: () => Navigator.pop(context, true),
            child: Text(confirmLabel),
          ),
        ],
      ),
    );
    return result == true;
  }

  void _showUndoSnack({
    required String message,
    required Future<void> Function() onUndo,
  }) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 6),
        action: SnackBarAction(
          label: "Undo",
          onPressed: () async {
            await onUndo();
            if (!mounted) return;
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text("Undone.")),
            );
          },
        ),
      ),
    );
  }

  void _handleLinkTap(String? href) {
    if (href == null || href.isEmpty) return;
    Clipboard.setData(ClipboardData(text: href));
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Link copied: $href")),
    );
  }

  String _buildShareMessage(
    String name,
    String taskTitle,
    String reward, {
    bool isAdult = false,
  }) {
    final rewardLine = reward.isNotEmpty ? "\n🎁 Reward: $reward" : "";
    if (isAdult) {
      return "🌟 Small win today!\n\n"
          "Just mastered \"$taskTitle\" — a real-world skill I'm glad to have checked off.$rewardLine\n\n"
          "Growing up one skill at a time with SmartStep 🚀\n\n"
          "#SmartStep #LifeSkills #GrowthMindset";
    }
    return "🌟 Proud parent moment!\n\n"
        "$name just learned \"$taskTitle\" — "
        "a real life skill that most kids never get taught!$rewardLine\n\n"
        "We are building life skills one step at a time with SmartStep 🚀\n\n"
        "#SmartStep #LifeSkills #ProudParent #GrowingUp";
  }
}

// ─── Widgets ─────────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Text(
          label,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
      );
}

class _ContextChips extends StatelessWidget {
  const _ContextChips({
    required this.category,
    required this.minAge,
    required this.maxAge,
  });
  final String category;
  final int minAge;
  final int maxAge;

  @override
  Widget build(BuildContext context) {
    final meta = _categoryMeta(category);
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        _Chip(
          icon: meta.icon,
          label: meta.label,
          color: meta.color,
        ),
        _Chip(
          icon: Icons.cake_outlined,
          label: "Age $minAge–$maxAge",
          color: Colors.grey.shade700,
        ),
      ],
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.icon, required this.label, required this.color});
  final IconData icon;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.25)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 14),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              fontSize: 12.5,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _BuildsOnRow extends StatelessWidget {
  const _BuildsOnRow({required this.titles});
  final List<String> titles;

  @override
  Widget build(BuildContext context) {
    final shown = titles.take(3).toList();
    final extra = titles.length - shown.length;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(Icons.link, size: 14, color: Colors.grey.shade600),
        const SizedBox(width: 6),
        Expanded(
          child: RichText(
            text: TextSpan(
              style: TextStyle(
                fontSize: 12.5,
                color: Colors.grey.shade700,
                height: 1.4,
              ),
              children: [
                const TextSpan(
                  text: "Builds on: ",
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                TextSpan(text: shown.join("  ·  ")),
                if (extra > 0)
                  TextSpan(
                    text: "  +$extra more",
                    style: TextStyle(
                      fontStyle: FontStyle.italic,
                      color: Colors.grey.shade500,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _SkippedBanner extends StatelessWidget {
  const _SkippedBanner({required this.status});
  final ProgressStatus status;

  @override
  Widget build(BuildContext context) {
    final isUnsuitable = status == ProgressStatus.skippedUnsuitable;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Row(
        children: [
          Icon(
            isUnsuitable ? Icons.visibility_off_outlined : Icons.psychology_outlined,
            color: Colors.grey.shade700,
            size: 22,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isUnsuitable ? "Currently hidden" : "Marked as already known",
                  style: TextStyle(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                    color: Colors.grey.shade800,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  isUnsuitable
                      ? "This skill and future ones that depend on it won't appear in the ladder."
                      : "This skill won't appear. Future skills that build on it will show a warning.",
                  style: TextStyle(
                    fontSize: 12.5,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _WarningBanner extends StatelessWidget {
  const _WarningBanner({required this.prereqTitle});
  final String prereqTitle;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_outlined,
              color: Colors.orange.shade700, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              "You skipped \"$prereqTitle\" earlier — check your child is ready for this one.",
              style: TextStyle(
                fontSize: 12.5,
                color: Colors.orange.shade900,
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SkillMasteredCard extends StatelessWidget {
  const _SkillMasteredCard({
    required this.completedAt,
    required this.practiceCount,
    required this.totalRequired,
    required this.lastReward,
    required this.isBypassed,
    required this.onReset,
  });
  final DateTime? completedAt;
  final int practiceCount;
  final int totalRequired;
  final String lastReward;
  final bool isBypassed;
  final VoidCallback onReset;

  String _formatDate(DateTime d) {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December',
    ];
    return "${d.day} ${months[d.month - 1]} ${d.year}";
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 8, 14),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.verified, color: Colors.green.shade700, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isBypassed ? "Already Mastered" : "Skill Mastered",
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: Colors.green.shade900,
                  ),
                ),
                const SizedBox(height: 4),
                if (isBypassed)
                  Text(
                    "Marked as known during the baseline check-in.",
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.green.shade800,
                    ),
                  )
                else ...[
                  if (completedAt != null)
                    Text(
                      "Mastered on ${_formatDate(completedAt!)}",
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.green.shade800,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  if (practiceCount > 0)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        practiceCount == 1
                            ? "Took 1 practice session"
                            : "Took $practiceCount practice sessions",
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.green.shade800,
                        ),
                      ),
                    ),
                ],
                if (lastReward.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    "🎁 Reward: $lastReward",
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.green.shade800,
                    ),
                  ),
                ],
              ],
            ),
          ),
          PopupMenuButton<String>(
            icon: Icon(Icons.more_vert, color: Colors.green.shade700),
            onSelected: (val) {
              if (val == 'reset') onReset();
            },
            itemBuilder: (_) => const [
              PopupMenuItem(
                value: 'reset',
                child: ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(Icons.refresh, size: 20),
                  title: Text("Reset this skill"),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _PracticeProgress extends StatelessWidget {
  const _PracticeProgress({required this.done, required this.total});
  final int done;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.repeat_outlined, size: 16, color: Colors.blue.shade700),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  done == 0
                      ? "Needs $total practice sessions to master"
                      : "Practised $done of $total times",
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Colors.blue.shade800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: List.generate(total, (i) {
              final filled = i < done;
              return Expanded(
                child: Container(
                  margin: EdgeInsets.only(right: i < total - 1 ? 4 : 0),
                  height: 8,
                  decoration: BoxDecoration(
                    color: filled ? Colors.blue.shade500 : Colors.blue.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }
}

class _ParentNoteCard extends StatefulWidget {
  const _ParentNoteCard({
    required this.content,
    required this.onTapLink,
    this.isAdult = false,
  });
  final String content;
  final void Function(String? href) onTapLink;
  final bool isAdult;

  @override
  State<_ParentNoteCard> createState() => _ParentNoteCardState();
}

class _ParentNoteCardState extends State<_ParentNoteCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.teal.shade50,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.teal.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => setState(() => _expanded = !_expanded),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  Icon(
                    widget.isAdult
                        ? Icons.lightbulb_outline
                        : Icons.family_restroom,
                    color: Colors.teal.shade700,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      widget.isAdult
                          ? "Why This Matters"
                          : "For Parents — Why This Matters",
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: Colors.teal.shade800,
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                  Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    color: Colors.teal.shade700,
                  ),
                ],
              ),
            ),
          ),
          if (_expanded)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: MarkdownBody(
                data: widget.content,
                shrinkWrap: true,
                onTapLink: (text, href, title) => widget.onTapLink(href),
                styleSheet: MarkdownStyleSheet(
                  p: TextStyle(color: Colors.teal.shade900),
                  listBullet: TextStyle(color: Colors.teal.shade900),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _CelebrationSheet extends StatelessWidget {
  const _CelebrationSheet({
    required this.childName,
    required this.taskTitle,
    required this.reward,
    required this.shareMessage,
    required this.practiceNumber,
    required this.totalRequired,
    required this.isFullyDone,
    this.isAdult = false,
  });
  final String childName;
  final String taskTitle;
  final String reward;
  final String shareMessage;
  final int practiceNumber;
  final int totalRequired;
  final bool isFullyDone;
  final bool isAdult;

  @override
  Widget build(BuildContext context) {
    final remaining = totalRequired - practiceNumber;

    return SafeArea(
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 28, 20, 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                isFullyDone ? "🎉" : "✅",
                style: const TextStyle(fontSize: 48),
              ),
              const SizedBox(height: 12),
              Text(
                isFullyDone
                    ? (isAdult
                        ? "You mastered a skill!"
                        : "$childName mastered a skill!")
                    : "Practice #$practiceNumber done!",
                style: Theme.of(context)
                    .textTheme
                    .titleLarge
                    ?.copyWith(fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 6),
              Text(
                taskTitle,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey.shade600,
                    ),
                textAlign: TextAlign.center,
              ),
              if (reward.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  "🎁 Reward: $reward",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.green.shade700,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
              if (!isFullyDone) ...[
                const SizedBox(height: 16),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                      vertical: 12, horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    "$remaining more ${remaining == 1 ? 'session' : 'sessions'} to master this skill.",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.blue.shade800,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
              if (isFullyDone) ...[
                const SizedBox(height: 24),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    shareMessage,
                    style: const TextStyle(fontSize: 13),
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    icon: const Icon(Icons.share_outlined),
                    label: const Text("Share this win"),
                    onPressed: () => Share.share(shareMessage),
                  ),
                ),
              ],
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text("Close"),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

typedef _TelemetryArgs = ({
  String taskSlug,
  String ageBand,
  String environment,
});

final _postCompletionProvider = FutureProvider.family<void, _TelemetryArgs>(
  (ref, args) async {
    final repo = ref.read(rewardRepositoryProvider);
    await repo.postCompletion(
      taskSlug: args.taskSlug,
      ageBand: args.ageBand,
      environment: args.environment,
    );
  },
);
