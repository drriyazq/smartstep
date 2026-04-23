import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/models.dart';
import '../../providers.dart';

({IconData icon, String label, Color color}) categoryMeta(String cat) =>
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
      'social' => (
          icon: Icons.people_outlined,
          label: 'Social',
          color: const Color(0xFFC62828),
        ),
      _ => (
          icon: Icons.category_outlined,
          label: cat[0].toUpperCase() + cat.substring(1),
          color: const Color(0xFF546E7A),
        ),
    };

const categoryOrder = [
  'financial',
  'household',
  'digital',
  'navigation',
  'cognitive',
  'social',
];

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeId = ref.watch(activeChildIdProvider);
    ref.watch(progressVersionProvider);
    final child = HiveSetup.childBox.get(activeId)!;
    final asyncCatalog = ref.watch(catalogProvider);
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
                  child.isAdult
                      ? (hasMultiple ? "${child.name}'s Ladder" : "Your Ladder")
                      : "${child.name}'s Ladder",
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
        data: (tasks) => _CategoryHome(tasks: tasks, childId: activeId),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.wifi_off, size: 48),
                const SizedBox(height: 12),
                Text("Could not load skills: $e",
                    textAlign: TextAlign.center),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => ref.invalidate(catalogProvider),
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
                "Switch Profile",
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
                      color:
                          Theme.of(context).colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                title: Row(
                  children: [
                    Expanded(
                      child:
                          Text(c.name, overflow: TextOverflow.ellipsis),
                    ),
                    if (c.isAdult) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.indigo.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border:
                              Border.all(color: Colors.indigo.shade200),
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
              leading: const CircleAvatar(child: Icon(Icons.add)),
              title: const Text("Add Another Profile"),
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

// ─── Category home (progress card + grid) ────────────────────────────

class _CategoryHome extends StatelessWidget {
  const _CategoryHome({required this.tasks, required this.childId});
  final List<Task> tasks;
  final String childId;

  int _computeStreak(Iterable<TaskProgress> progresses) {
    final dates = progresses
        .where((p) => p.completedAt != null)
        .map((p) => DateTime(
              p.completedAt!.year,
              p.completedAt!.month,
              p.completedAt!.day,
            ))
        .toSet();
    if (dates.isEmpty) return 0;
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    DateTime cursor;
    if (dates.contains(today)) {
      cursor = today;
    } else if (dates.contains(yesterday)) {
      cursor = yesterday;
    } else {
      return 0;
    }
    var count = 0;
    while (dates.contains(cursor)) {
      count++;
      cursor = cursor.subtract(const Duration(days: 1));
    }
    return count;
  }

  bool _completedToday(Iterable<TaskProgress> progresses) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    return progresses.any((p) =>
        p.completedAt != null &&
        DateTime(p.completedAt!.year, p.completedAt!.month,
                p.completedAt!.day) ==
            today);
  }

  @override
  Widget build(BuildContext context) {
    final allProgress = HiveSetup.progressBox.values
        .where((p) => p.childId == childId)
        .toList();
    final tasksBySlug = {for (final t in tasks) t.slug: t};

    final completedCount =
        allProgress.where((p) => p.status == ProgressStatus.completed).length;
    final satisfiedCount = allProgress
        .where((p) => p.satisfies && p.status != ProgressStatus.completed)
        .length;
    final doneCount = completedCount + satisfiedCount;

    final streak = _computeStreak(allProgress);
    final didToday = _completedToday(allProgress);

    final allDoneByCategory = <String, int>{};
    final allTotalByCategory = <String, int>{};
    for (final t in tasks) {
      final cat = t.tags.isEmpty ? 'other' : t.tags.first.category;
      allTotalByCategory[cat] = (allTotalByCategory[cat] ?? 0) + 1;
    }
    for (final p in allProgress) {
      if (!p.satisfies) continue;
      final t = tasksBySlug[p.taskSlug];
      if (t == null) continue;
      final cat = t.tags.isEmpty ? 'other' : t.tags.first.category;
      allDoneByCategory[cat] = (allDoneByCategory[cat] ?? 0) + 1;
    }

    final categoryStats = categoryOrder
        .where((c) => (allTotalByCategory[c] ?? 0) > 0)
        .map((c) => _CategoryStat(
              category: c,
              done: allDoneByCategory[c] ?? 0,
              total: allTotalByCategory[c]!,
            ))
        .toList();

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        _ProgressCard(
          done: doneCount,
          completed: completedCount,
          total: tasks.length,
          streak: streak,
          didToday: didToday,
        ),
        const SizedBox(height: 20),
        Text(
          "Skill Areas",
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
                color: Colors.black87,
                fontSize: 16,
              ),
        ),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.25,
          children: categoryStats.map((stat) {
            final meta = categoryMeta(stat.category);
            return _CategoryCard(
              stat: stat,
              meta: meta,
              onTap: () =>
                  context.push('/category/${stat.category}'),
            );
          }).toList(),
        ),
      ],
    );
  }
}

// ─── Category card (grid item) ───────────────────────────────────────

class _CategoryCard extends StatelessWidget {
  const _CategoryCard({
    required this.stat,
    required this.meta,
    required this.onTap,
  });
  final _CategoryStat stat;
  final ({IconData icon, String label, Color color}) meta;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final pct =
        stat.total == 0 ? 0.0 : stat.done / stat.total;
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
                color: meta.color.withOpacity(0.25), width: 1.2),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: meta.color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(meta.icon,
                        color: meta.color, size: 20),
                  ),
                  const Spacer(),
                  Icon(Icons.chevron_right,
                      color: Colors.grey.shade400, size: 18),
                ],
              ),
              const Spacer(),
              Text(
                meta.label,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                "${stat.done} / ${stat.total} done",
                style: TextStyle(
                  fontSize: 11.5,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: pct,
                  minHeight: 5,
                  backgroundColor: meta.color.withOpacity(0.12),
                  valueColor:
                      AlwaysStoppedAnimation<Color>(meta.color),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Progress card (overall) ─────────────────────────────────────────

class _ProgressCard extends StatelessWidget {
  const _ProgressCard({
    required this.done,
    required this.completed,
    required this.total,
    required this.streak,
    required this.didToday,
  });
  final int done;
  final int completed;
  final int total;
  final int streak;
  final bool didToday;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final pct = total == 0 ? 0.0 : done / total;
    return Card(
      elevation: 0,
      color: cs.primaryContainer,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.rocket_launch_outlined,
                    color: cs.onPrimaryContainer, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    "$done of $total skills done",
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(
                          color: cs.onPrimaryContainer,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
                if (streak > 0)
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: didToday
                          ? Colors.orange.shade600
                          : cs.onPrimaryContainer.withOpacity(0.18),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text("🔥",
                            style: TextStyle(fontSize: 13)),
                        const SizedBox(width: 4),
                        Text(
                          "$streak-day",
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: didToday
                                ? Colors.white
                                : cs.onPrimaryContainer,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(
                value: pct,
                minHeight: 10,
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
                  : "Choose a skill area below to get started",
              style:
                  Theme.of(context).textTheme.bodySmall?.copyWith(
                        color:
                            cs.onPrimaryContainer.withOpacity(0.8),
                        fontSize: 12.5,
                      ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Data class ───────────────────────────────────────────────────────

class _CategoryStat {
  const _CategoryStat({
    required this.category,
    required this.done,
    required this.total,
  });
  final String category;
  final int done;
  final int total;
}
