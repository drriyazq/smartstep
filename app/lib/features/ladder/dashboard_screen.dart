import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/ladder.dart';
import '../../domain/models.dart';

final _catalogProvider = FutureProvider<List<Task>>((ref) async {
  final child = HiveSetup.childBox.values.first;
  return ref.read(taskRepositoryProvider).fetchAll(
        environment: child.environment.name,
      );
});

// Per-category visual metadata
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
    final asyncCatalog = ref.watch(_catalogProvider);
    final child = HiveSetup.childBox.values.first;

    return Scaffold(
      appBar: AppBar(
        title: Text("${child.name}'s Ladder"),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: "Profile",
            onPressed: () => context.push("/profile"),
          ),
        ],
      ),
      body: asyncCatalog.when(
        data: (tasks) => _LadderList(tasks: tasks, childId: child.id),
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
}

class _LadderList extends StatelessWidget {
  const _LadderList({required this.tasks, required this.childId});
  final List<Task> tasks;
  final String childId;

  @override
  Widget build(BuildContext context) {
    final progress = {
      for (final p in HiveSetup.progressBox.values.where((p) => p.childId == childId))
        p.taskSlug: p,
    };
    final taskBySlug = {for (final t in tasks) t.slug: t};

    // Build grouped task rows
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

    // Overall progress stats
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
        // ── Progress summary card ──────────────────────────────────
        _ProgressCard(
          done: doneCount,
          completed: completedCount,
          total: total,
        ),
        const SizedBox(height: 20),

        // ── Category sections ──────────────────────────────────────
        for (final c in categories) ...[
          _CategoryHeader(
            category: c,
            rows: grouped[c]!,
          ),
          const SizedBox(height: 8),
          ...grouped[c]!.map((row) => _buildTile(context, row, c)),
          const SizedBox(height: 20),
        ],
      ],
    );
  }

  Widget _buildTile(BuildContext context, _TaskRow row, String category) {
    final meta = _categoryMeta(category);
    final enabled = row.state == LadderState.unlocked ||
        row.state == LadderState.lockedWithWarning ||
        row.state == LadderState.completed;

    final (icon, color) = switch (row.state) {
      LadderState.completed => (Icons.check_circle, Colors.green.shade600),
      LadderState.satisfied => (Icons.check_circle_outline, Colors.green.shade400),
      LadderState.unlocked => (Icons.play_circle_outline, meta.color),
      LadderState.lockedWithWarning => (Icons.warning_amber_outlined, Colors.orange),
      LadderState.locked => (Icons.lock_outline, Colors.grey.shade400),
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: ListTile(
        leading: Icon(icon, color: color, size: 26),
        title: Text(
          row.task.title,
          style: TextStyle(
            fontWeight: enabled ? FontWeight.w500 : FontWeight.normal,
            color: enabled ? null : Colors.grey.shade500,
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
        trailing: enabled
            ? Icon(Icons.chevron_right, color: Colors.grey.shade400, size: 20)
            : null,
        onTap: enabled ? () => context.push("/task/${row.task.slug}") : null,
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
        LadderState.locked => "Complete prerequisites first",
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
                backgroundColor: cs.onPrimaryContainer.withOpacity(0.15),
                valueColor:
                    AlwaysStoppedAnimation<Color>(cs.onPrimaryContainer),
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
    final total = rows.length;

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
          "$doneInCat / $total",
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
