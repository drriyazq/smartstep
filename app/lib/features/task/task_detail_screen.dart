import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/reward_repository.dart';
import '../../data/api/task_repository.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/models.dart';
import 'reward_picker_sheet.dart';

class TaskDetailScreen extends ConsumerWidget {
  const TaskDetailScreen({super.key, required this.taskSlug});
  final String taskSlug;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cached = ref.read(taskRepositoryProvider).cached ?? const <Task>[];
    Task? taskNullable;
    for (final t in cached) {
      if (t.slug == taskSlug) {
        taskNullable = t;
        break;
      }
    }

    if (taskNullable == null) {
      return Scaffold(
        appBar: AppBar(title: const Text("Task")),
        body: const Center(child: Text("Task not found in cache.")),
      );
    }
    final task = taskNullable;
    final child = HiveSetup.childBox.values.first;
    final progressKey = TaskProgress.key(child.id, task.slug);
    final existing = HiveSetup.progressBox.get(progressKey);

    return Scaffold(
      appBar: AppBar(title: Text(task.title)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _sectionHeader(context, "How to"),
          MarkdownBody(data: task.howToMd, shrinkWrap: true),
          if (task.safetyMd.isNotEmpty) ...[
            const SizedBox(height: 24),
            _sectionHeader(context, "Safety"),
            Card(
              color: Colors.amber.shade50,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: MarkdownBody(data: task.safetyMd, shrinkWrap: true),
              ),
            ),
          ],
          if (task.parentNoteMd.isNotEmpty) ...[
            const SizedBox(height: 24),
            _ParentNoteCard(content: task.parentNoteMd),
          ],
          const SizedBox(height: 32),
          if (existing?.status == ProgressStatus.completed)
            const Card(
              child: ListTile(
                leading: Icon(Icons.check_circle, color: Colors.green),
                title: Text("Already completed"),
              ),
            )
          else ...[
            FilledButton.icon(
              icon: const Icon(Icons.check),
              label: const Text("Mark complete"),
              onPressed: () => _markComplete(context, ref, task, child.id),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () =>
                        _skip(context, task, child.id, ProgressStatus.skippedKnown),
                    child: const Text("Already knows"),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () =>
                        _skip(context, task, child.id, ProgressStatus.skippedUnsuitable),
                    child: const Text("Not suitable"),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _sectionHeader(BuildContext context, String label) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Text(label, style: Theme.of(context).textTheme.titleLarge),
      );

  Future<void> _markComplete(
    BuildContext context,
    WidgetRef ref,
    Task task,
    String childId,
  ) async {
    final child = HiveSetup.childBox.get(childId)!;
    final reward = await showModalBottomSheet<String?>(
      context: context,
      isScrollControlled: true,
      builder: (_) => RewardPickerSheet(childId: childId),
    );
    if (reward == null) return;

    final key = TaskProgress.key(childId, task.slug);
    await HiveSetup.progressBox.put(
      key,
      TaskProgress(
        taskSlug: task.slug,
        childId: childId,
        status: ProgressStatus.completed,
        completedAt: DateTime.now(),
      ),
    );
    if (context.mounted) context.pop();

    // Fire-and-forget telemetry — anonymous.
    unawaited(ref.read(_postCompletionProvider((
      taskSlug: task.slug,
      ageBand: child.ageBand(DateTime.now()),
      environment: child.environment.name,
    )).future));
  }

  Future<void> _skip(
    BuildContext context,
    Task task,
    String childId,
    ProgressStatus status,
  ) async {
    final key = TaskProgress.key(childId, task.slug);
    await HiveSetup.progressBox.put(
      key,
      TaskProgress(taskSlug: task.slug, childId: childId, status: status),
    );
    if (context.mounted) context.pop();
  }
}

class _ParentNoteCard extends StatefulWidget {
  const _ParentNoteCard({required this.content});
  final String content;

  @override
  State<_ParentNoteCard> createState() => _ParentNoteCardState();
}

class _ParentNoteCardState extends State<_ParentNoteCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.teal.shade50,
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
                  Icon(Icons.family_restroom, color: Colors.teal.shade700, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      "For Parents — Why This Matters",
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: Colors.teal.shade800,
                            fontWeight: FontWeight.w600,
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

typedef _TelemetryArgs = ({String taskSlug, String ageBand, String environment});

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
