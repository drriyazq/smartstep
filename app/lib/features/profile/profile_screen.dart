import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  ChildProfile get _child => HiveSetup.childBox.values.first;

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
