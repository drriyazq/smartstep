import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/ladder.dart';
import '../../domain/models.dart';

final _catalogProvider = FutureProvider<List<Task>>((ref) async {
  final child = HiveSetup.childBox.values.first;
  final age = child.ageOn(DateTime.now());
  return ref.read(taskRepositoryProvider).fetchAll(
        environment: child.environment.name,
        minAge: age,
        maxAge: age,
      );
});

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncCatalog = ref.watch(_catalogProvider);
    final child = HiveSetup.childBox.values.first;

    return Scaffold(
      appBar: AppBar(title: Text("${child.name}'s ladder")),
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
                Text("Could not fetch ladder: $e", textAlign: TextAlign.center),
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
    final grouped = <String, List<_TaskRow>>{};
    for (final t in tasks) {
      final state = computeLadderState(task: t, progressBySlug: progress);
      final category = t.tags.isEmpty ? "Other" : t.tags.first.category;
      grouped.putIfAbsent(category, () => []).add(_TaskRow(t, state));
    }
    for (final rows in grouped.values) {
      rows.sort((a, b) => a.state.index.compareTo(b.state.index));
    }
    final categories = grouped.keys.toList()..sort();

    return ListView(
      padding: const EdgeInsets.symmetric(vertical: 12),
      children: [
        for (final c in categories) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Text(
              _humanize(c),
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          for (final row in grouped[c]!) _buildTile(context, row),
        ],
      ],
    );
  }

  String _humanize(String s) =>
      s.isEmpty ? s : s[0].toUpperCase() + s.substring(1).replaceAll("_", " ");

  Widget _buildTile(BuildContext context, _TaskRow row) {
    final enabled = row.state == LadderState.unlocked ||
        row.state == LadderState.lockedWithWarning;
    final icon = switch (row.state) {
      LadderState.completed => Icons.check_circle,
      LadderState.satisfied => Icons.check_circle_outline,
      LadderState.unlocked => Icons.play_circle_outline,
      LadderState.lockedWithWarning => Icons.warning_amber_outlined,
      LadderState.locked => Icons.lock_outline,
    };
    final color = switch (row.state) {
      LadderState.completed => Colors.green,
      LadderState.satisfied => Colors.green.shade300,
      LadderState.unlocked => Theme.of(context).colorScheme.primary,
      LadderState.lockedWithWarning => Colors.orange,
      LadderState.locked => Colors.grey,
    };
    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(row.task.title),
      subtitle: Text(_subtitle(row.state)),
      enabled: enabled || row.state == LadderState.completed,
      onTap: () => context.push("/task/${row.task.slug}"),
    );
  }

  String _subtitle(LadderState s) => switch (s) {
        LadderState.completed => "Completed",
        LadderState.satisfied => "Already knows this",
        LadderState.unlocked => "Ready to try",
        LadderState.lockedWithWarning => "Requires a skipped skill",
        LadderState.locked => "Locked",
      };
}

class _TaskRow {
  _TaskRow(this.task, this.state);
  final Task task;
  final LadderState state;
}
