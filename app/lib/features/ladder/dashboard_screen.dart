import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/custom_task.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/ladder.dart';
import '../../domain/models.dart';
import '../../providers.dart';

String _sexParam(Sex sex) => switch (sex) {
      Sex.boy => "male",
      Sex.girl => "female",
      Sex.other => "any",
    };

// Auto-refreshes when the active child changes (different child = new fetch).
final _catalogProvider = FutureProvider<List<Task>>((ref) async {
  final activeId = ref.watch(activeChildIdProvider);
  final child = HiveSetup.childBox.get(activeId)!;
  final age = child.ageOn(DateTime.now());
  return ref.read(taskRepositoryProvider).fetchAll(
        environment: child.environment.name,
        minAge: age,
        maxAge: age,
        sex: _sexParam(child.sex),
      );
});

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
      'custom' => (
          icon: Icons.star_outline,
          label: 'My Tasks',
          color: const Color(0xFF880E4F),
        ),
      _ => (
          icon: Icons.category_outlined,
          label: cat[0].toUpperCase() + cat.substring(1),
          color: const Color(0xFF546E7A),
        ),
    };

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeId = ref.watch(activeChildIdProvider);
    ref.watch(progressVersionProvider); // rebuild when any progress changes
    final child = HiveSetup.childBox.get(activeId)!;
    final asyncCatalog = ref.watch(_catalogProvider);
    final hasMultiple = HiveSetup.childBox.length > 1;

    return Scaffold(
      appBar: AppBar(
        title: GestureDetector(
          onTap: () => _showChildSwitcher(context, ref, activeId),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Flexible(
                child: Text(
                  "${child.name}'s Ladder",
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (hasMultiple) ...[
                const SizedBox(width: 4),
                const Icon(Icons.keyboard_arrow_down, size: 20),
              ],
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: "Profile",
            onPressed: () => context.push("/profile"),
          ),
        ],
      ),
      body: asyncCatalog.when(
        data: (tasks) => _LadderList(tasks: tasks, childId: activeId),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.wifi_off, size: 48),
                const SizedBox(height: 12),
                Text("Could not fetch ladder: $e",
                    textAlign: TextAlign.center),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => ref.invalidate(_catalogProvider),
                  child: const Text("Retry"),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showChildSwitcher(
      BuildContext context, WidgetRef ref, String activeId) {
    showModalBottomSheet(
      context: context,
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
              child: Text(
                "Switch child",
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
            ),
            for (final c in HiveSetup.childBox.values) ...[
              ListTile(
                leading: CircleAvatar(
                  backgroundColor:
                      Theme.of(context).colorScheme.primaryContainer,
                  child: Text(
                    c.name[0].toUpperCase(),
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                title: Text(c.name),
                subtitle: Text(
                    "Age ${c.ageOn(DateTime.now())} · ${c.environment.name[0].toUpperCase()}${c.environment.name.substring(1)}"),
                trailing: c.id == activeId
                    ? Icon(Icons.check_circle,
                        color: Theme.of(context).colorScheme.primary)
                    : null,
                onTap: () {
                  if (c.id != activeId) {
                    setActiveChild(
                        ref.read(activeChildIdProvider.notifier), c.id);
                  }
                  Navigator.pop(context);
                },
              ),
            ],
            const Divider(height: 1),
            ListTile(
              leading: const CircleAvatar(
                child: Icon(Icons.add),
              ),
              title: const Text("Add another child"),
              onTap: () {
                Navigator.pop(context);
                context.push('/onboarding/child?adding=true');
              },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}

class _LadderList extends StatefulWidget {
  const _LadderList({required this.tasks, required this.childId});
  final List<Task> tasks;
  final String childId;

  @override
  State<_LadderList> createState() => _LadderListState();
}

class _LadderListState extends State<_LadderList> {
  static const _nextUpLimit = 5;
  bool _showAllNextUp = false;

  @override
  Widget build(BuildContext context) {
    final childId = widget.childId;
    final tasks = widget.tasks;

    final progress = {
      for (final p in HiveSetup.progressBox.values
          .where((p) => p.childId == childId))
        p.taskSlug: p,
    };
    // Used for warning prereq title lookup in lockedWithWarning classification
    final taskBySlug = {for (final t in tasks) t.slug: t};

    // Classify every task into one of four buckets
    final nextUpRows = <_TaskRow>[];       // unlocked / lockedWithWarning
    final doneByCategory = <String, List<_TaskRow>>{};  // completed / satisfied
    final skippedRows = <_TaskRow>[];      // skippedUnsuitable

    for (final t in tasks) {
      final state = computeLadderState(task: t, progressBySlug: progress);
      final prog = progress[t.slug];
      final category = t.tags.isEmpty ? "other" : t.tags.first.category;

      // Explicitly unsuitable — show in skipped section
      if (prog?.status == ProgressStatus.skippedUnsuitable) {
        skippedRows.add(_TaskRow(t, state));
        continue;
      }

      if (state == LadderState.completed || state == LadderState.satisfied) {
        doneByCategory.putIfAbsent(category, () => []).add(_TaskRow(t, state));
        continue;
      }

      if (state == LadderState.unlocked || state == LadderState.lockedWithWarning) {
        String? warningTitle;
        if (state == LadderState.lockedWithWarning) {
          for (final p in t.prerequisites) {
            if (!p.isMandatory) continue;
            if (progress[p.taskSlug]?.softSkipped == true) {
              warningTitle = taskBySlug[p.taskSlug]?.title;
              break;
            }
          }
        }
        nextUpRows.add(_TaskRow(t, state, warningPrereqTitle: warningTitle));
        continue;
      }
      // LadderState.locked with no explicit skip → hide
    }

    // Sort next up: unlocked first, then lockedWithWarning
    nextUpRows.sort((a, b) => a.state.index.compareTo(b.state.index));

    final visibleNextUp = _showAllNextUp
        ? nextUpRows
        : nextUpRows.take(_nextUpLimit).toList();
    final hiddenCount = nextUpRows.length - visibleNextUp.length;

    // Sorted category keys for done section
    final doneCategories = doneByCategory.keys.toList()..sort();

    // Custom tasks
    final customTasks = HiveSetup.customTaskBox.values
        .where((t) => t.childId == childId)
        .toList();

    // Progress totals
    final completedCount = progress.values
        .where((p) => p.status == ProgressStatus.completed)
        .length;
    final satisfiedCount = progress.values
        .where((p) => p.satisfies && p.status != ProgressStatus.completed)
        .length;
    final doneCount = completedCount + satisfiedCount;
    final total = tasks.length + customTasks.length;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        _ProgressCard(
          done: doneCount,
          completed: completedCount,
          total: total,
        ),
        const SizedBox(height: 20),

        // ── Next Up ────────────────────────────────────────────
        if (nextUpRows.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.rocket_launch_outlined,
            label: "Next Up",
            color: Theme.of(context).colorScheme.primary,
            count: "${nextUpRows.length} available",
          ),
          const SizedBox(height: 8),
          ...visibleNextUp.map(
            (row) => _buildTile(context, row, row.task.tags.isEmpty ? "other" : row.task.tags.first.category),
          ),
          if (hiddenCount > 0)
            TextButton.icon(
              onPressed: () => setState(() => _showAllNextUp = true),
              icon: const Icon(Icons.expand_more, size: 18),
              label: Text("$hiddenCount more available"),
            )
          else if (_showAllNextUp && nextUpRows.length > _nextUpLimit)
            TextButton.icon(
              onPressed: () => setState(() => _showAllNextUp = false),
              icon: const Icon(Icons.expand_less, size: 18),
              label: const Text("Show fewer"),
            ),
          const SizedBox(height: 20),
        ],

        // ── Completed & Mastered (by category) ────────────────
        for (final c in doneCategories) ...[
          _CategoryHeader(category: c, rows: doneByCategory[c]!),
          const SizedBox(height: 8),
          ...doneByCategory[c]!.map(
            (row) => _buildTile(context, row, c),
          ),
          const SizedBox(height: 20),
        ],

        // ── Skipped / Unsuitable ───────────────────────────────
        if (skippedRows.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.block_outlined,
            label: "Skipped",
            color: Colors.grey.shade600,
            count: "${skippedRows.length}",
          ),
          const SizedBox(height: 8),
          ...skippedRows.map(
            (row) => _buildTile(context, row, row.task.tags.isEmpty ? "other" : row.task.tags.first.category),
          ),
          const SizedBox(height: 20),
        ],

        // ── My Tasks (custom) ──────────────────────────────────
        if (customTasks.isNotEmpty) ...[
          _CustomCategoryHeader(tasks: customTasks, childId: childId),
          const SizedBox(height: 8),
          for (final ct in customTasks)
            _buildCustomTile(context, ct, progress),
          const SizedBox(height: 20),
        ],
      ],
    );
  }

  Widget _buildTile(BuildContext context, _TaskRow row, String category) {
    final meta = _categoryMeta(category);
    final isSkipped = row.state == LadderState.locked; // only skipped tasks reach here as locked

    final (icon, color) = switch (row.state) {
      LadderState.completed => (Icons.check_circle, Colors.green.shade600),
      LadderState.satisfied =>
        (Icons.check_circle_outline, Colors.green.shade400),
      LadderState.unlocked => (Icons.play_circle_outline, meta.color),
      LadderState.lockedWithWarning =>
        (Icons.warning_amber_outlined, Colors.orange),
      LadderState.locked => (Icons.block_outlined, Colors.grey.shade400),
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: ListTile(
        leading: Icon(icon, color: color, size: 26),
        title: Text(
          row.task.title,
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: isSkipped ? Colors.grey.shade500 : null,
          ),
        ),
        subtitle: Text(
          _subtitle(row),
          style: TextStyle(
            fontSize: 12,
            color: row.state == LadderState.lockedWithWarning
                ? Colors.orange.shade700
                : null,
          ),
        ),
        trailing: Icon(Icons.chevron_right, color: Colors.grey.shade400, size: 20),
        onTap: () => context.push("/task/${row.task.slug}"),
      ),
    );
  }

  Widget _buildCustomTile(
    BuildContext context,
    CustomTask ct,
    Map<String, TaskProgress> progress,
  ) {
    final prog = progress[ct.progressSlug];
    final isDone = prog?.status == ProgressStatus.completed;

    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: ListTile(
        leading: Icon(
          isDone ? Icons.check_circle : Icons.play_circle_outline,
          color: isDone ? Colors.green.shade600 : const Color(0xFF880E4F),
          size: 26,
        ),
        title: Text(
          ct.title,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Text(
          isDone ? "Completed" : "Ready to try",
          style: const TextStyle(fontSize: 12),
        ),
        trailing: Icon(Icons.chevron_right,
            color: Colors.grey.shade400, size: 20),
        onTap: () => context.push("/custom-task/${ct.id}"),
      ),
    );
  }

  String _subtitle(_TaskRow row) => switch (row.state) {
        LadderState.completed => "Completed",
        LadderState.satisfied => "Already knows this",
        LadderState.unlocked => "Ready to try",
        LadderState.lockedWithWarning => row.warningPrereqTitle != null
            ? 'Needs: "${row.warningPrereqTitle}"'
            : "Requires a skipped skill",
        LadderState.locked => "Skipped",
      };
}


class _ProgressCard extends StatelessWidget {
  const _ProgressCard({
    required this.done,
    required this.completed,
    required this.total,
  });
  final int done;
  final int completed;
  final int total;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final pct = total == 0 ? 0.0 : done / total;
    return Card(
      color: cs.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.rocket_launch_outlined,
                    color: cs.onPrimaryContainer, size: 20),
                const SizedBox(width: 8),
                Text(
                  "$done of $total skills done",
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: cs.onPrimaryContainer,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: pct,
                minHeight: 8,
                backgroundColor:
                    cs.onPrimaryContainer.withOpacity(0.15),
                valueColor: AlwaysStoppedAnimation<Color>(
                    cs.onPrimaryContainer),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              completed > 0
                  ? "$completed completed · ${done - completed} already mastered"
                  : "Tap any unlocked skill to get started",
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: cs.onPrimaryContainer.withOpacity(0.8),
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.icon,
    required this.label,
    required this.color,
    required this.count,
  });
  final IconData icon;
  final String label;
  final Color color;
  final String count;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 18),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            label,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: color,
                ),
          ),
        ),
        Text(
          count,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }
}

class _CategoryHeader extends StatelessWidget {
  const _CategoryHeader({required this.category, required this.rows});
  final String category;
  final List<_TaskRow> rows;

  @override
  Widget build(BuildContext context) {
    final meta = _categoryMeta(category);
    final doneInCat = rows
        .where((r) =>
            r.state == LadderState.completed ||
            r.state == LadderState.satisfied)
        .length;
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: meta.color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(meta.icon, color: meta.color, size: 18),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            meta.label,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: meta.color,
                ),
          ),
        ),
        Text(
          "$doneInCat / ${rows.length}",
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }
}

class _CustomCategoryHeader extends StatelessWidget {
  const _CustomCategoryHeader(
      {required this.tasks, required this.childId});
  final List<CustomTask> tasks;
  final String childId;

  @override
  Widget build(BuildContext context) {
    final meta = _categoryMeta('custom');
    final doneCount = tasks.where((t) {
      final prog = HiveSetup.progressBox
          .get(TaskProgress.key(childId, t.progressSlug));
      return prog?.status == ProgressStatus.completed;
    }).length;

    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: meta.color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(meta.icon, color: meta.color, size: 18),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            meta.label,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: meta.color,
                ),
          ),
        ),
        Text(
          "$doneCount / ${tasks.length}",
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }
}

class _TaskRow {
  _TaskRow(this.task, this.state, {this.warningPrereqTitle});
  final Task task;
  final LadderState state;
  final String? warningPrereqTitle;
}
