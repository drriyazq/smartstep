import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/ladder.dart';
import '../../domain/models.dart';
import '../../providers.dart';

// Auto-refreshes when the active child changes (different environment = new fetch).
final _catalogProvider = FutureProvider<List<Task>>((ref) async {
  final activeId = ref.watch(activeChildIdProvider);
  final child = HiveSetup.childBox.get(activeId)!;
  return ref.read(taskRepositoryProvider).fetchAll(
        environment: child.environment.name,
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
              Text("${child.name}'s Ladder"),
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

class _LadderList extends StatelessWidget {
  const _LadderList({required this.tasks, required this.childId});
  final List<Task> tasks;
  final String childId;

  @override
  Widget build(BuildContext context) {
    final progress = {
      for (final p in HiveSetup.progressBox.values
          .where((p) => p.childId == childId))
        p.taskSlug: p,
    };
    final taskBySlug = {for (final t in tasks) t.slug: t};

    final grouped = <String, List<_TaskRow>>{};
    for (final t in tasks) {
      final state = computeLadderState(task: t, progressBySlug: progress);
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
      final category = t.tags.isEmpty ? "other" : t.tags.first.category;
      grouped
          .putIfAbsent(category, () => [])
          .add(_TaskRow(t, state, warningPrereqTitle: warningTitle));
    }
    for (final rows in grouped.values) {
      rows.sort((a, b) => a.state.index.compareTo(b.state.index));
    }
    final categories = grouped.keys.toList()..sort();

    final completedCount = progress.values
        .where((p) => p.status == ProgressStatus.completed)
        .length;
    final satisfiedCount = progress.values
        .where((p) => p.satisfies && p.status != ProgressStatus.completed)
        .length;
    final doneCount = completedCount + satisfiedCount;
    final total = tasks.length;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        _ProgressCard(
          done: doneCount,
          completed: completedCount,
          total: total,
        ),
        const SizedBox(height: 20),
        for (final c in categories) ...[
          _CategoryHeader(category: c, rows: grouped[c]!),
          const SizedBox(height: 8),
          ...grouped[c]!.map(
            (row) => _buildTile(context, row, c, taskBySlug, progress),
          ),
          const SizedBox(height: 20),
        ],
      ],
    );
  }

  Widget _buildTile(
    BuildContext context,
    _TaskRow row,
    String category,
    Map<String, Task> taskBySlug,
    Map<String, TaskProgress> progress,
  ) {
    final meta = _categoryMeta(category);
    final isLocked = row.state == LadderState.locked;
    final isInteractive = row.state == LadderState.unlocked ||
        row.state == LadderState.lockedWithWarning ||
        row.state == LadderState.completed ||
        isLocked;

    final (icon, color) = switch (row.state) {
      LadderState.completed => (Icons.check_circle, Colors.green.shade600),
      LadderState.satisfied =>
        (Icons.check_circle_outline, Colors.green.shade400),
      LadderState.unlocked => (Icons.play_circle_outline, meta.color),
      LadderState.lockedWithWarning =>
        (Icons.warning_amber_outlined, Colors.orange),
      LadderState.locked => (Icons.lock_outline, Colors.grey.shade400),
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: ListTile(
        leading: Icon(icon, color: color, size: 26),
        title: Text(
          row.task.title,
          style: TextStyle(
            fontWeight: isLocked ? FontWeight.normal : FontWeight.w500,
            color: isLocked ? Colors.grey.shade500 : null,
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
        trailing: isInteractive
            ? Icon(
                isLocked ? Icons.info_outline : Icons.chevron_right,
                color: Colors.grey.shade400,
                size: 20,
              )
            : null,
        onTap: isInteractive
            ? () {
                if (isLocked) {
                  _showLockedInfo(
                      context, row.task, taskBySlug, progress);
                } else {
                  context.push("/task/${row.task.slug}");
                }
              }
            : null,
      ),
    );
  }

  void _showLockedInfo(
    BuildContext context,
    Task task,
    Map<String, Task> taskBySlug,
    Map<String, TaskProgress> progress,
  ) {
    final mandatory = task.prerequisites.where((p) => p.isMandatory).toList();

    showModalBottomSheet(
      context: context,
      builder: (_) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.lock_outline, color: Colors.grey.shade600),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      task.title,
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                mandatory.isEmpty
                    ? "This skill has no prerequisites — it should be unlocked. Try refreshing."
                    : "Complete these skills first to unlock it:",
                style: Theme.of(context)
                    .textTheme
                    .bodySmall
                    ?.copyWith(color: Colors.grey.shade600),
              ),
              if (mandatory.isNotEmpty) ...[
                const SizedBox(height: 16),
                for (final p in mandatory) ...[
                  _PrereqRow(
                    prereqTask: taskBySlug[p.taskSlug],
                    slug: p.taskSlug,
                    progress: progress[p.taskSlug],
                  ),
                  const SizedBox(height: 10),
                ],
              ],
              const SizedBox(height: 8),
            ],
          ),
        ),
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
        LadderState.locked => "Tap to see what's needed",
      };
}

class _PrereqRow extends StatelessWidget {
  const _PrereqRow({
    required this.prereqTask,
    required this.slug,
    required this.progress,
  });
  final Task? prereqTask;
  final String slug;
  final TaskProgress? progress;

  @override
  Widget build(BuildContext context) {
    final isDone = progress?.satisfies == true;
    final title = prereqTask?.title ?? slug;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          isDone ? Icons.check_circle : Icons.radio_button_unchecked,
          color: isDone ? Colors.green.shade600 : Colors.grey.shade400,
          size: 22,
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: isDone ? Colors.grey.shade500 : null,
                  decoration:
                      isDone ? TextDecoration.lineThrough : null,
                ),
              ),
              Text(
                isDone ? "Done" : "Not yet completed",
                style: TextStyle(
                  fontSize: 11,
                  color: isDone
                      ? Colors.green.shade600
                      : Colors.orange.shade700,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
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

class _TaskRow {
  _TaskRow(this.task, this.state, {this.warningPrereqTitle});
  final Task task;
  final LadderState state;
  final String? warningPrereqTitle;
}
