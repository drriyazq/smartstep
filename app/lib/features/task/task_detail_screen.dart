import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';

import '../../data/api/reward_repository.dart';
import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/models.dart';
import '../../providers.dart';
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

    final activeId = ref.read(activeChildIdProvider);
    final child = HiveSetup.childBox.get(activeId)!;
    final progressKey = TaskProgress.key(child.id, task.slug);
    final existing = HiveSetup.progressBox.get(progressKey);

    // Retrieve stored reward title if the task was completed.
    final rewardKey = 'reward::${child.id}::${task.slug}';
    final savedReward = HiveSetup.sessionBox.get(rewardKey) as String?;

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
            Card(
              child: ListTile(
                leading: const Icon(Icons.check_circle, color: Colors.green),
                title: const Text("Already Completed"),
                subtitle: savedReward != null && savedReward.isNotEmpty
                    ? Text("Reward: $savedReward",
                        style: TextStyle(color: Colors.green.shade700))
                    : null,
              ),
            )
          else ...[
            FilledButton.icon(
              icon: const Icon(Icons.check),
              label: const Text("Mark Complete"),
              onPressed: () => _markComplete(context, ref, task, child.id),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _skip(
                        context, ref, task, child.id, ProgressStatus.skippedKnown),
                    child: const Text("Already Knows"),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _skip(
                        context, ref, task, child.id, ProgressStatus.skippedUnsuitable),
                    child: const Text("Not Suitable"),
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
    // null = sheet dismissed without choosing; empty string = "skip reward"
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

    // Store the reward title so the detail screen can show it later.
    final rewardKey = 'reward::$childId::${task.slug}';
    await HiveSetup.sessionBox.put(rewardKey, reward);

    // Signal the dashboard to rebuild.
    ref.read(progressVersionProvider.notifier).state++;

    // Fire-and-forget telemetry — anonymous.
    unawaited(ref.read(_postCompletionProvider((
      taskSlug: task.slug,
      ageBand: child.ageBand(DateTime.now()),
      environment: child.environment.name,
    )).future));

    if (context.mounted) {
      // Show celebration & share sheet
      final shareMsg = _buildShareMessage(child.name, task.title, reward);
      await showModalBottomSheet(
        context: context,
        isDismissible: false,
        enableDrag: false,
        builder: (_) => _CelebrationSheet(
          childName: child.name,
          taskTitle: task.title,
          reward: reward,
          shareMessage: shareMsg,
        ),
      );
      if (context.mounted) context.pop();
    }
  }

  String _buildShareMessage(String childName, String taskTitle, String reward) {
    final rewardLine = reward.isNotEmpty ? "\n🎁 Reward: $reward" : "";
    return "🌟 Proud parent moment!\n\n"
        "$childName just learned \"$taskTitle\" — "
        "a real life skill that most kids never get taught!$rewardLine\n\n"
        "We are building life skills one step at a time with SmartStep 🚀\n\n"
        "#SmartStep #LifeSkills #ProudParent #GrowingUp";
  }

  Future<void> _skip(
    BuildContext context,
    WidgetRef ref,
    Task task,
    String childId,
    ProgressStatus status,
  ) async {
    final key = TaskProgress.key(childId, task.slug);
    await HiveSetup.progressBox.put(
      key,
      TaskProgress(taskSlug: task.slug, childId: childId, status: status),
    );

    // Signal the dashboard to rebuild.
    ref.read(progressVersionProvider.notifier).state++;

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

class _CelebrationSheet extends StatelessWidget {
  const _CelebrationSheet({
    required this.childName,
    required this.taskTitle,
    required this.reward,
    required this.shareMessage,
  });
  final String childName;
  final String taskTitle;
  final String reward;
  final String shareMessage;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 28, 20, 20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text("🎉", style: TextStyle(fontSize: 48)),
            const SizedBox(height: 12),
            Text(
              "$childName completed a skill!",
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
                style: TextStyle(
                  color: Colors.green.shade700,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
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
                label: const Text("Share on WhatsApp / Social Media"),
                onPressed: () => Share.share(shareMessage),
              ),
            ),
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
