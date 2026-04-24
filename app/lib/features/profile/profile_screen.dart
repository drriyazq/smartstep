import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/custom_reward.dart';
import '../../data/local/custom_task.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../providers.dart';
import 'data_export.dart';

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
    await HiveSetup.childBox.put(_child.id, _child.copyWith(name: result));
    if (mounted) setState(() {});
  }

  static const _allCategories = [
    'cognitive', 'digital', 'financial', 'household', 'navigation', 'social'
  ];

  static const _categoryLabels = {
    'cognitive': 'Thinking & Problem Solving',
    'digital': 'Digital & Communication',
    'financial': 'Financial Literacy',
    'household': 'Household Independence',
    'navigation': 'Navigation & Safety',
    'social': 'Social & Communication',
  };

  Set<String> _loadEnabledCategories() {
    final saved = HiveSetup.sessionBox.get('cat_filter::${_child.id}') as String?;
    return (saved != null && saved.isNotEmpty)
        ? saved.split(',').toSet()
        : {};
  }

  Future<void> _editCategoryPreferences() async {
    final current = _loadEnabledCategories();
    // empty means all enabled — expand to full set for the dialog
    var selected = current.isEmpty ? Set<String>.from(_allCategories) : Set<String>.from(current);

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (ctx, setDlg) => AlertDialog(
          title: const Text("Category Preferences"),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  "Choose which skill categories to show on the ladder.",
                  style: TextStyle(fontSize: 13, color: Colors.grey),
                ),
                const SizedBox(height: 12),
                for (final cat in _allCategories)
                  CheckboxListTile(
                    value: selected.contains(cat),
                    title: Text(_categoryLabels[cat] ?? cat),
                    contentPadding: EdgeInsets.zero,
                    dense: true,
                    onChanged: (val) {
                      final next = Set<String>.from(selected);
                      if (val == true) {
                        next.add(cat);
                      } else if (next.length > 1) {
                        next.remove(cat);
                      }
                      setDlg(() => selected = next);
                    },
                  ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text("Cancel"),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text("Save"),
            ),
          ],
        ),
      ),
    );
    if (confirmed != true) return;
    // if all selected, store empty string (means "all")
    final toSave = selected.length == _allCategories.length ? '' : selected.join(',');
    await HiveSetup.sessionBox.put('cat_filter::${_child.id}', toSave);
    ref.read(progressVersionProvider.notifier).state++;
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
    await HiveSetup.childBox.put(_child.id, _child.copyWith(environment: result));
    ref.invalidate(catalogProvider);
    if (mounted) setState(() {});
  }

  void _shareApp() {
    Share.share(
      "Most kids finish school knowing complex maths but can't make a phone call, "
      "manage their pocket money, or say sorry properly.\n\n"
      "SmartStep is an Android app that teaches children aged 7–13 real life skills — "
      "how to greet adults, handle money, cook a simple meal, stay safe online, and so much more. "
      "Each skill they learn unlocks the next one, like a game. "
      "Parents choose the reward when a skill is done.\n\n"
      "500+ skills. Every child's journey is different. Built for Indian families. 🚀\n\n"
      "#SmartStep #LifeSkills #IndianParents",
    );
  }

  Future<void> _exportChildData(String childId) async {
    try {
      await DataExport.exportForChild(childId);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Couldn't export: $e")),
      );
    }
  }

  Future<void> _confirmDeleteChild(ChildProfile c) async {
    final isLast = HiveSetup.childBox.length <= 1;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text("Delete ${c.name}'s data?"),
        content: Text(
          isLast
              ? "This will permanently delete all of ${c.name}'s data from this device. Since this is the only child, you will be signed out and returned to the start."
              : "This will permanently delete all of ${c.name}'s profile, progress, rewards and custom tasks from this device. This cannot be undone.",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.pop(context, true),
            child: const Text("Delete permanently"),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    // Delete all progress for this child
    final progressKeys = HiveSetup.progressBox.keys
        .where((k) => (k as String).startsWith(c.id))
        .toList();
    await HiveSetup.progressBox.deleteAll(progressKeys);

    // Delete custom tasks for this child
    final customTaskKeys = HiveSetup.customTaskBox.values
        .where((t) => t.childId == c.id)
        .map((t) => t.id)
        .toList();
    await HiveSetup.customTaskBox.deleteAll(customTaskKeys);

    // Delete custom rewards for this child
    final customRewardKeys = HiveSetup.customRewardBox.values
        .where((r) => r.childId == c.id)
        .map((r) => r.id)
        .toList();
    await HiveSetup.customRewardBox.deleteAll(customRewardKeys);

    // Delete session-scoped child keys (practice counts, rewards, filters)
    final sessionKeysToDelete = HiveSetup.sessionBox.keys
        .where((k) => k is String && k.contains(c.id))
        .toList();
    await HiveSetup.sessionBox.deleteAll(sessionKeysToDelete);

    // Finally delete the child record
    await HiveSetup.childBox.delete(c.id);

    if (isLast) {
      // No children left — sign out completely, consent still counts
      await HiveSetup.sessionBox.clear();
      if (!mounted) return;
      context.go('/consent');
      return;
    }

    // Switch active child to another if the deleted one was active
    if (ref.read(activeChildIdProvider) == c.id) {
      final next = HiveSetup.childBox.values.first.id;
      setActiveChild(ref.read(activeChildIdProvider.notifier), next);
    }
    ref.read(progressVersionProvider.notifier).state++;
    if (!mounted) return;
    setState(() {});
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("${c.name}'s data was deleted.")),
    );
  }

  void _contactPrivacy() {
    Share.share(
      "Subject: SmartStep Privacy Request\n\n"
      "Please include your request (access / correction / deletion / "
      "withdraw consent / grievance) when emailing drdentalmail@gmail.com.",
      subject: 'SmartStep Privacy Request',
    );
  }

  Future<void> _confirmLogout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Log Out?"),
        content: const Text(
          "This will remove all children and progress from this device. "
          "You will need to set up the app again.",
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
            child: const Text("Log Out"),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    await HiveSetup.childBox.clear();
    await HiveSetup.progressBox.clear();
    await HiveSetup.sessionBox.clear();
    await HiveSetup.rewardUsageBox.clear();
    await HiveSetup.customRewardBox.clear();
    await HiveSetup.customTaskBox.clear();
    if (mounted) context.go('/signin');
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
          const SizedBox(height: 10),
          _CategoryPreferencesTile(
            enabledCategories: _loadEnabledCategories(),
            allCategories: _allCategories,
            categoryLabels: _categoryLabels,
            onTap: _editCategoryPreferences,
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            icon: const Icon(Icons.tune, size: 16),
            label: const Text("Recalibrate Ladder"),
            onPressed: () => context.push(
              '/onboarding/baseline?childId=${child.id}',
            ),
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
            "Profiles on This Device",
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 10),
          for (final c in HiveSetup.childBox.values) ...[
            Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: Column(
                children: [
                  ListTile(
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
                    title: Row(
                      children: [
                        Expanded(
                          child: Text(c.name,
                              overflow: TextOverflow.ellipsis),
                        ),
                        if (c.isAdult) ...[
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.indigo.shade50,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.indigo.shade200),
                            ),
                            child: Text(
                              "Adult",
                              style: TextStyle(
                                fontSize: 10.5,
                                fontWeight: FontWeight.w700,
                                color: Colors.indigo.shade700,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
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
                  Padding(
                    padding: const EdgeInsets.fromLTRB(12, 0, 12, 10),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextButton.icon(
                            icon: const Icon(Icons.download_outlined, size: 16),
                            label: const Text("Export data",
                                style: TextStyle(fontSize: 12.5)),
                            onPressed: () => _exportChildData(c.id),
                          ),
                        ),
                        Expanded(
                          child: TextButton.icon(
                            icon: Icon(Icons.delete_outline,
                                size: 16, color: cs.error),
                            label: Text(
                              "Delete",
                              style: TextStyle(
                                  fontSize: 12.5, color: cs.error),
                            ),
                            onPressed: () => _confirmDeleteChild(c),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 8),
          OutlinedButton.icon(
            icon: const Icon(Icons.add),
            label: const Text("Add Another Profile"),
            onPressed: () => context.push('/onboarding/child?adding=true'),
          ),
          const SizedBox(height: 20),

          // ── Privacy & Data ────────────────────────────────────────
          const Divider(),
          const SizedBox(height: 12),
          Text(
            "Privacy & Data",
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 10),
          const _DataTransparencyCard(),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            icon: const Icon(Icons.description_outlined, size: 16),
            label: const Text("Privacy Policy"),
            onPressed: () => context.push('/legal/privacy'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            icon: const Icon(Icons.article_outlined, size: 16),
            label: const Text("Terms of Use"),
            onPressed: () => context.push('/legal/terms'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            icon: const Icon(Icons.email_outlined, size: 16),
            label: const Text("Contact us about privacy"),
            onPressed: _contactPrivacy,
          ),
          const SizedBox(height: 16),

          // ── Share & Logout ────────────────────────────────────────
          const Divider(),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            icon: const Icon(Icons.share_outlined),
            label: const Text("Share SmartStep"),
            onPressed: _shareApp,
          ),
          const SizedBox(height: 10),

          // ── Danger zone ───────────────────────────────────────────
          OutlinedButton.icon(
            icon: Icon(Icons.refresh,
                color: Theme.of(context).colorScheme.error),
            label: Text(
              "Reset All Progress",
              style: TextStyle(
                  color: Theme.of(context).colorScheme.error),
            ),
            style: OutlinedButton.styleFrom(
              side: BorderSide(
                  color: Theme.of(context).colorScheme.error),
            ),
            onPressed: _confirmResetProgress,
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            icon: Icon(Icons.logout,
                color: Theme.of(context).colorScheme.error),
            label: Text(
              "Log Out",
              style: TextStyle(
                  color: Theme.of(context).colorScheme.error),
            ),
            style: OutlinedButton.styleFrom(
              side: BorderSide(
                  color: Theme.of(context).colorScheme.error),
            ),
            onPressed: _confirmLogout,
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

class _CategoryPreferencesTile extends StatelessWidget {
  const _CategoryPreferencesTile({
    required this.enabledCategories,
    required this.allCategories,
    required this.categoryLabels,
    required this.onTap,
  });
  final Set<String> enabledCategories;
  final List<String> allCategories;
  final Map<String, String> categoryLabels;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isAll = enabledCategories.isEmpty;
    final subtitle = isAll
        ? "All categories shown"
        : enabledCategories
            .map((c) => categoryLabels[c] ?? c)
            .join(', ');
    return OutlinedButton.icon(
      icon: const Icon(Icons.category_outlined, size: 16),
      label: Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Category Preferences"),
            Text(
              subtitle,
              style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
      onPressed: onTap,
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

class _DataTransparencyCard extends StatefulWidget {
  const _DataTransparencyCard();

  @override
  State<_DataTransparencyCard> createState() => _DataTransparencyCardState();
}

class _DataTransparencyCardState extends State<_DataTransparencyCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => setState(() => _expanded = !_expanded),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Row(
                children: [
                  Icon(Icons.shield_outlined,
                      color: Colors.blue.shade700, size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      "What data SmartStep holds",
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 14,
                        color: Colors.blue.shade900,
                      ),
                    ),
                  ),
                  Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    color: Colors.blue.shade700,
                  ),
                ],
              ),
            ),
          ),
          if (_expanded)
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const _DataRow(
                    emoji: '📱',
                    title: 'On this device only',
                    items: [
                      "Child's name, date of birth, sex, environment",
                      'Skill progress and completion dates',
                      'Reward choices you select',
                      'Custom tasks and rewards you add',
                    ],
                    subtle: false,
                  ),
                  const SizedBox(height: 10),
                  const _DataRow(
                    emoji: '📊',
                    title: 'Sent anonymously to server',
                    items: [
                      'Skill identifier + age band + environment when a skill is completed',
                      'No name, phone, child ID, or date of birth',
                    ],
                    subtle: false,
                  ),
                  const SizedBox(height: 10),
                  const _DataRow(
                    emoji: '🚫',
                    title: 'Never collected',
                    items: [
                      'Location, contacts, camera, microphone',
                      'Advertising identifiers, biometric data',
                      'Photos, recordings, or writings of your child',
                    ],
                    subtle: true,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    "All sensitive on-device data is encrypted with AES-256.",
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.blue.shade900,
                      fontStyle: FontStyle.italic,
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

class _DataRow extends StatelessWidget {
  const _DataRow({
    required this.emoji,
    required this.title,
    required this.items,
    required this.subtle,
  });
  final String emoji;
  final String title;
  final List<String> items;
  final bool subtle;

  @override
  Widget build(BuildContext context) {
    final color = subtle ? Colors.grey.shade700 : Colors.blue.shade900;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 14)),
            const SizedBox(width: 6),
            Text(
              title,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 3),
        for (final item in items)
          Padding(
            padding: const EdgeInsets.only(left: 22, top: 2),
            child: Text(
              '• $item',
              style: TextStyle(
                fontSize: 12.5,
                color: color,
                height: 1.35,
              ),
            ),
          ),
      ],
    );
  }
}

