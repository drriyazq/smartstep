import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/custom_reward.dart';
import '../../data/local/custom_task.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../providers.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  ChildProfile get _child =>
      HiveSetup.childBox.get(ref.read(activeChildIdProvider))!;

  Future<void> _editName() async {
    final controller = TextEditingController(text: _child.name);
    final result = await showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Edit name"),
        content: TextField(
          controller: controller,
          autofocus: true,
          textCapitalization: TextCapitalization.words,
          decoration: const InputDecoration(
            labelText: "Name or nickname",
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, controller.text.trim()),
            child: const Text("Save"),
          ),
        ],
      ),
    );
    if (result == null || result.isEmpty) return;
    final updated = ChildProfile(
      id: _child.id,
      name: result,
      dob: _child.dob,
      sex: _child.sex,
      environment: _child.environment,
    );
    await HiveSetup.childBox.put(_child.id, updated);
    if (mounted) setState(() {});
  }

  Future<void> _editEnvironment() async {
    Environment? selected = _child.environment;
    final result = await showDialog<Environment>(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (ctx, setDlg) => AlertDialog(
          title: const Text("Environment"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: Environment.values.map((e) {
              return RadioListTile<Environment>(
                value: e,
                groupValue: selected,
                title: Text(_envLabel(e)),
                subtitle: Text(_envDesc(e)),
                onChanged: (v) => setDlg(() => selected = v),
              );
            }).toList(),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel"),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, selected),
              child: const Text("Save"),
            ),
          ],
        ),
      ),
    );
    if (result == null) return;
    final updated = ChildProfile(
      id: _child.id,
      name: _child.name,
      dob: _child.dob,
      sex: _child.sex,
      environment: result,
    );
    await HiveSetup.childBox.put(_child.id, updated);
    if (mounted) setState(() {});
  }

  Future<void> _confirmResetProgress() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Reset all progress?"),
        content: const Text(
          "This will clear all completed tasks, bypasses, and skips. "
          "The ladder will return to its starting state.",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error),
            onPressed: () => Navigator.pop(context, true),
            child: const Text("Reset"),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    final childId = _child.id;
    final keysToDelete = HiveSetup.progressBox.keys
        .where((k) => (k as String).startsWith(childId))
        .toList();
    await HiveSetup.progressBox.deleteAll(keysToDelete);
    await HiveSetup.rewardUsageBox.clear();
    if (mounted) {
      ref.read(progressVersionProvider.notifier).state++;
      setState(() {});
    }
  }

  // ── Custom Rewards ────────────────────────────────────────────────────────

  Future<void> _addCustomReward() async {
    final titleCtrl = TextEditingController();
    final notesCtrl = TextEditingController();
    bool isFree = true;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (ctx, setDlg) => AlertDialog(
          title: const Text("Add custom reward"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleCtrl,
                autofocus: true,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: "Reward title",
                  hintText: "e.g. 30 min extra screen time",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: notesCtrl,
                decoration: const InputDecoration(
                  labelText: "Notes (optional)",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              CheckboxListTile(
                value: isFree,
                contentPadding: EdgeInsets.zero,
                title: const Text("No cost involved"),
                onChanged: (v) => setDlg(() => isFree = v ?? true),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text("Cancel"),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text("Add"),
            ),
          ],
        ),
      ),
    );

    if (confirmed != true) return;
    final title = titleCtrl.text.trim();
    if (title.isEmpty) return;

    final id = DateTime.now().millisecondsSinceEpoch.toString();
    final reward = CustomReward(
      id: id,
      childId: _child.id,
      title: title,
      notes: notesCtrl.text.trim(),
      isFree: isFree,
    );
    await HiveSetup.customRewardBox.put(id, reward);
    if (mounted) setState(() {});
  }

  Future<void> _deleteCustomReward(String id) async {
    await HiveSetup.customRewardBox.delete(id);
    if (mounted) setState(() {});
  }

  // ── Custom Tasks ──────────────────────────────────────────────────────────

  Future<void> _addCustomTask() async {
    final titleCtrl = TextEditingController();
    final howToCtrl = TextEditingController();
    final noteCtrl = TextEditingController();

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Add custom task"),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleCtrl,
                autofocus: true,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: "Task title",
                  hintText: "e.g. Pack school bag independently",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: howToCtrl,
                maxLines: 3,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: "How to (optional)",
                  hintText: "Steps or tips for the child",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: noteCtrl,
                maxLines: 2,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: "Parent note (optional)",
                  hintText: "Why this matters",
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text("Add"),
          ),
        ],
      ),
    );

    if (confirmed != true) return;
    final title = titleCtrl.text.trim();
    if (title.isEmpty) return;

    final id = DateTime.now().millisecondsSinceEpoch.toString();
    final task = CustomTask(
      id: id,
      childId: _child.id,
      title: title,
      howToMd: howToCtrl.text.trim(),
      parentNoteMd: noteCtrl.text.trim(),
    );
    await HiveSetup.customTaskBox.put(id, task);
    ref.read(progressVersionProvider.notifier).state++;
    if (mounted) setState(() {});
  }

  Future<void> _editCustomTask(CustomTask task) async {
    final titleCtrl = TextEditingController(text: task.title);
    final howToCtrl = TextEditingController(text: task.howToMd);
    final noteCtrl = TextEditingController(text: task.parentNoteMd);

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Edit task"),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleCtrl,
                autofocus: true,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: "Task title",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: howToCtrl,
                maxLines: 3,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: "How to",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: noteCtrl,
                maxLines: 2,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: "Parent note",
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text("Save"),
          ),
        ],
      ),
    );

    if (confirmed != true) return;
    final title = titleCtrl.text.trim();
    if (title.isEmpty) return;

    final updated = CustomTask(
      id: task.id,
      childId: task.childId,
      title: title,
      howToMd: howToCtrl.text.trim(),
      parentNoteMd: noteCtrl.text.trim(),
    );
    await HiveSetup.customTaskBox.put(task.id, updated);
    ref.read(progressVersionProvider.notifier).state++;
    if (mounted) setState(() {});
  }

  Future<void> _deleteCustomTask(CustomTask task) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Delete task?"),
        content: Text('"${task.title}" will be removed, including any progress.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error),
            onPressed: () => Navigator.pop(context, true),
            child: const Text("Delete"),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    await HiveSetup.customTaskBox.delete(task.id);
    // Remove associated progress
    final progressKey = TaskProgress.key(task.childId, task.progressSlug);
    await HiveSetup.progressBox.delete(progressKey);
    await HiveSetup.sessionBox.delete('reward::${task.childId}::${task.progressSlug}');
    ref.read(progressVersionProvider.notifier).state++;
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final child = _child;
    final now = DateTime.now();
    final age = child.ageOn(now);
    final cs = Theme.of(context).colorScheme;

    final allProgress =
        HiveSetup.progressBox.values.where((p) => p.childId == child.id);
    final completedCount =
        allProgress.where((p) => p.status == ProgressStatus.completed).length;
    final masteredCount = allProgress
        .where((p) =>
            p.status == ProgressStatus.bypassed ||
            p.status == ProgressStatus.skippedKnown)
        .length;
    final skippedCount = allProgress
        .where((p) => p.status == ProgressStatus.skippedUnsuitable)
        .length;

    final totalTasks =
        ref.read(taskRepositoryProvider).cached?.length ?? 0;

    final initials = child.name.trim().split(RegExp(r'\s+')).take(2).map((w) => w[0].toUpperCase()).join();

    // Custom data for this child
    final customRewards = HiveSetup.customRewardBox.values
        .where((r) => r.childId == child.id)
        .toList();
    final customTasks = HiveSetup.customTaskBox.values
        .where((t) => t.childId == child.id)
        .toList();

    return Scaffold(
      appBar: AppBar(title: const Text("Profile")),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ── Avatar + name ────────────────────────────────────────
          Center(
            child: Column(
              children: [
                const SizedBox(height: 8),
                CircleAvatar(
                  radius: 40,
                  backgroundColor: cs.primaryContainer,
                  child: Text(
                    initials,
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: cs.onPrimaryContainer,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  child.name,
                  style: Theme.of(context)
                      .textTheme
                      .headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  "Age $age · ${_envLabel(child.environment)}",
                  style: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.copyWith(color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // ── Edit buttons ─────────────────────────────────────────
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.edit, size: 16),
                  label: const Text("Edit name"),
                  onPressed: _editName,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.location_on_outlined, size: 16),
                  label: const Text("Environment"),
                  onPressed: _editEnvironment,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // ── Progress stats ────────────────────────────────────────
          Text(
            "Progress",
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 10),
          if (totalTasks > 0) ...[
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: (completedCount + masteredCount) / totalTasks,
                minHeight: 10,
                backgroundColor: Colors.grey.shade200,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              "${completedCount + masteredCount} of $totalTasks skills done",
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 12),
          ],
          Row(
            children: [
              _StatChip(
                label: "Completed",
                count: completedCount,
                color: Colors.green,
                icon: Icons.check_circle,
              ),
              const SizedBox(width: 8),
              _StatChip(
                label: "Mastered",
                count: masteredCount,
                color: Colors.blue,
                icon: Icons.check_circle_outline,
              ),
              const SizedBox(width: 8),
              _StatChip(
                label: "Skipped",
                count: skippedCount,
                color: Colors.orange,
                icon: Icons.cancel_outlined,
              ),
            ],
          ),
          const SizedBox(height: 32),

          // ── Customise ─────────────────────────────────────────────
          const Divider(),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.card_giftcard_outlined,
                  label: "Custom Rewards",
                  color: Colors.deepPurple,
                  onTap: _addCustomReward,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.add_task,
                  label: "Custom Tasks",
                  color: const Color(0xFF880E4F),
                  onTap: _addCustomTask,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Custom rewards list
          if (customRewards.isNotEmpty) ...[
            for (final r in customRewards)
              Card(
                margin: const EdgeInsets.only(bottom: 6),
                child: ListTile(
                  leading: const Icon(Icons.card_giftcard_outlined,
                      color: Colors.deepPurple, size: 20),
                  title: Text(r.title),
                  subtitle: r.notes.isNotEmpty ? Text(r.notes) : null,
                  trailing: IconButton(
                    icon: Icon(Icons.delete_outline, color: cs.error, size: 20),
                    onPressed: () => _deleteCustomReward(r.id),
                  ),
                ),
              ),
            const SizedBox(height: 8),
          ],

          // Custom tasks list
          if (customTasks.isNotEmpty) ...[
            for (final t in customTasks)
              Card(
                margin: const EdgeInsets.only(bottom: 6),
                child: ListTile(
                  leading: const Icon(Icons.star_outline,
                      color: Color(0xFF880E4F), size: 20),
                  title: Text(t.title),
                  subtitle: t.howToMd.isNotEmpty
                      ? Text(
                          t.howToMd,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12),
                        )
                      : null,
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.edit_outlined,
                            size: 20, color: Colors.grey),
                        onPressed: () => _editCustomTask(t),
                      ),
                      IconButton(
                        icon: Icon(Icons.delete_outline,
                            color: cs.error, size: 20),
                        onPressed: () => _deleteCustomTask(t),
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 8),
          ],
          const Divider(),
          const SizedBox(height: 16),

          // ── All children ──────────────────────────────────────────
          Text(
            "Children on this device",
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 10),
          for (final c in HiveSetup.childBox.values) ...[
            Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: c.id == child.id
                      ? cs.primaryContainer
                      : Colors.grey.shade200,
                  child: Text(
                    c.name[0].toUpperCase(),
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: c.id == child.id
                          ? cs.onPrimaryContainer
                          : Colors.grey.shade700,
                    ),
                  ),
                ),
                title: Text(c.name),
                subtitle: Text(
                    "Age ${c.ageOn(DateTime.now())} · ${_envLabel(c.environment)}"),
                trailing: c.id == child.id
                    ? Icon(Icons.check_circle, color: cs.primary)
                    : TextButton(
                        onPressed: () {
                          setActiveChild(
                              ref.read(activeChildIdProvider.notifier),
                              c.id);
                          setState(() {});
                        },
                        child: const Text("Switch"),
                      ),
              ),
            ),
          ],
          const SizedBox(height: 8),
          OutlinedButton.icon(
            icon: const Icon(Icons.add),
            label: const Text("Add another child"),
            onPressed: () => context.push('/onboarding/child?adding=true'),
          ),
          const SizedBox(height: 16),

          // ── Danger zone ───────────────────────────────────────────
          const Divider(),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            icon: Icon(Icons.refresh,
                color: Theme.of(context).colorScheme.error),
            label: Text(
              "Reset all progress",
              style: TextStyle(
                  color: Theme.of(context).colorScheme.error),
            ),
            style: OutlinedButton.styleFrom(
              side: BorderSide(
                  color: Theme.of(context).colorScheme.error),
            ),
            onPressed: _confirmResetProgress,
          ),
        ],
      ),
    );
  }

  String _envLabel(Environment e) => switch (e) {
        Environment.urban => "Urban",
        Environment.suburban => "Suburban",
        Environment.rural => "Rural",
      };

  String _envDesc(Environment e) => switch (e) {
        Environment.urban => "City with public transit, shops close by",
        Environment.suburban => "Quieter streets, mostly walkable",
        Environment.rural => "Countryside or small village",
      };
}

class _QuickActionCard extends StatelessWidget {
  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.25)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
            ),
            const SizedBox(width: 4),
            Icon(Icons.add_circle_outline, color: color, size: 16),
          ],
        ),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  const _StatChip({
    required this.label,
    required this.count,
    required this.color,
    required this.icon,
  });
  final String label;
  final int count;
  final Color color;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(
              "$count",
              style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: color),
            ),
            Text(
              label,
              style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
            ),
          ],
        ),
      ),
    );
  }
}
