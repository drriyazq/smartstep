import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/active_child.dart';
import '../../data/local/custom_task.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../providers.dart';
import 'reward_picker_sheet.dart';

class CustomTaskDetailScreen extends ConsumerWidget {
  const CustomTaskDetailScreen({super.key, required this.taskId});
  final String taskId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch so undo/complete triggers rebuild.
    ref.watch(progressVersionProvider);

    final task = HiveSetup.customTaskBox.get(taskId);

    if (task == null) {
      return Scaffold(
        appBar: AppBar(title: const Text("Task")),
        body: const Center(child: Text("Task not found.")),
      );
    }

    final childId = ref.read(activeChildIdProvider);
    final progressKey = TaskProgress.key(childId, task.progressSlug);
    final existing = HiveSetup.progressBox.get(progressKey);

    final rewardKey = 'reward::$childId::${task.progressSlug}';
    final savedReward = HiveSetup.sessionBox.get(rewardKey) as String?;

    return Scaffold(
      appBar: AppBar(title: Text(task.title)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          if (task.howToMd.isNotEmpty) ...[
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text("How to",
                  style: Theme.of(context).textTheme.titleLarge),
            ),
            MarkdownBody(data: task.howToMd, shrinkWrap: true),
          ],
          if (task.parentNoteMd.isNotEmpty) ...[
            const SizedBox(height: 24),
            _ParentNoteCard(content: task.parentNoteMd),
          ],
          const SizedBox(height: 32),
          if (existing?.status == ProgressStatus.completed)
            Card(
              child: ListTile(
                leading: const Icon(Icons.check_circle, color: Colors.green),
                title: const Text("Already completed"),
                subtitle: savedReward != null && savedReward.isNotEmpty
                    ? Text("Reward: $savedReward",
                        style: TextStyle(color: Colors.green.shade700))
                    : null,
                trailing: TextButton(
                  onPressed: () => _uncomplete(ref, task, childId),
                  child: const Text("Undo"),
                ),
              ),
            )
          else
            FilledButton.icon(
              icon: const Icon(Icons.check),
              label: const Text("Mark complete"),
              onPressed: () => _markComplete(context, ref, task, childId),
            ),
        ],
      ),
    );
  }

  Future<void> _markComplete(
    BuildContext context,
    WidgetRef ref,
    CustomTask task,
    String childId,
  ) async {
    final reward = await showModalBottomSheet<String?>(
      context: context,
      isScrollControlled: true,
      builder: (_) => RewardPickerSheet(childId: childId),
    );
    if (reward == null) return;

    final key = TaskProgress.key(childId, task.progressSlug);
    await HiveSetup.progressBox.put(
      key,
      TaskProgress(
        taskSlug: task.progressSlug,
        childId: childId,
        status: ProgressStatus.completed,
        completedAt: DateTime.now(),
      ),
    );

    final rewardKey = 'reward::$childId::${task.progressSlug}';
    await HiveSetup.sessionBox.put(rewardKey, reward);

    ref.read(progressVersionProvider.notifier).state++;

    if (context.mounted) {
      context.pop();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.white),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  reward.isEmpty
                      ? '"${task.title}" marked complete!'
                      : '"${task.title}" completed! Reward: $reward',
                  maxLines: 2,
                ),
              ),
            ],
          ),
          backgroundColor: Colors.green.shade700,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  Future<void> _uncomplete(
    WidgetRef ref,
    CustomTask task,
    String childId,
  ) async {
    final key = TaskProgress.key(childId, task.progressSlug);
    await HiveSetup.progressBox.delete(key);
    await HiveSetup.sessionBox.delete('reward::$childId::${task.progressSlug}');
    ref.read(progressVersionProvider.notifier).state++;
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
                  Icon(Icons.family_restroom,
                      color: Colors.teal.shade700, size: 20),
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
