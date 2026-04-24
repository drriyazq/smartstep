import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../data/local/active_child.dart';
import '../../data/local/hive_setup.dart';
import '../../domain/masteries.dart';
import '../../domain/mastery_evaluator.dart';
import '../../providers.dart';
import '../task/certificate_card.dart';
import '../task/certificate_share.dart';

class AchievementsScreen extends ConsumerWidget {
  const AchievementsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeId = ref.watch(activeChildIdProvider);
    ref.watch(progressVersionProvider);
    final child = HiveSetup.childBox.get(activeId)!;

    final allProgress = HiveSetup.progressBox.values
        .where((p) => p.childId == activeId)
        .toList();
    final progressBySlug = {for (final p in allProgress) p.taskSlug: p};

    final forKind =
        kMasteries.where((m) => m.isAdult == child.isAdult).toList();

    final earned = <Mastery>[];
    final inProgress = <Mastery>[];
    final locked = <Mastery>[];
    for (final m in forKind) {
      final done = masteryProgressCount(m, progressBySlug);
      if (done == m.requiredTaskSlugs.length) {
        earned.add(m);
      } else if (done > 0) {
        inProgress.add(m);
      } else {
        locked.add(m);
      }
    }
    inProgress.sort((a, b) =>
        (masteryProgressCount(b, progressBySlug) /
                b.requiredTaskSlugs.length)
            .compareTo(masteryProgressCount(a, progressBySlug) /
                a.requiredTaskSlugs.length));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mastery Milestones'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        children: [
          _StatsCard(
            earned: earned.length,
            total: forKind.length,
          ),
          const SizedBox(height: 20),
          if (earned.isNotEmpty) ...[
            _SectionHeader(title: 'Earned', count: earned.length),
            const SizedBox(height: 8),
            ...earned.map((m) => _MasteryTile(
                  mastery: m,
                  progressCount: m.requiredTaskSlugs.length,
                  earnedWhen: earnedAt(activeId, m),
                  childName: child.name,
                  childAge: child.ageOn(DateTime.now()),
                )),
            const SizedBox(height: 24),
          ],
          if (inProgress.isNotEmpty) ...[
            _SectionHeader(title: 'In Progress', count: inProgress.length),
            const SizedBox(height: 8),
            ...inProgress.map((m) => _MasteryTile(
                  mastery: m,
                  progressCount: masteryProgressCount(m, progressBySlug),
                  earnedWhen: null,
                  childName: child.name,
                  childAge: child.ageOn(DateTime.now()),
                )),
            const SizedBox(height: 24),
          ],
          if (locked.isNotEmpty) ...[
            _SectionHeader(title: 'Locked', count: locked.length),
            const SizedBox(height: 8),
            ...locked.map((m) => _MasteryTile(
                  mastery: m,
                  progressCount: 0,
                  earnedWhen: null,
                  childName: child.name,
                  childAge: child.ageOn(DateTime.now()),
                )),
          ],
        ],
      ),
    );
  }
}

class _StatsCard extends StatelessWidget {
  const _StatsCard({required this.earned, required this.total});
  final int earned;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF1B6CA8),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          const Text('🏆', style: TextStyle(fontSize: 48)),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$earned of $total masteries earned',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  earned == 0
                      ? 'Complete a full group of tasks to earn your first!'
                      : 'Keep going — each milestone is a shareable certificate.',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 13,
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

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, required this.count});
  final String title;
  final int count;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: Colors.grey.shade200,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            '$count',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}

class _MasteryTile extends StatelessWidget {
  const _MasteryTile({
    required this.mastery,
    required this.progressCount,
    required this.earnedWhen,
    required this.childName,
    required this.childAge,
  });

  final Mastery mastery;
  final int progressCount;
  final DateTime? earnedWhen;
  final String childName;
  final int childAge;

  bool get isEarned => progressCount == mastery.requiredTaskSlugs.length;
  bool get isLocked => progressCount == 0;

  @override
  Widget build(BuildContext context) {
    final color = categoryColor(mastery.category);
    final total = mastery.requiredTaskSlugs.length;
    final ratio = progressCount / total;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isEarned ? color : Colors.grey.shade300,
          width: isEarned ? 1.5 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: isLocked ? Colors.grey.shade100 : color.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  alignment: Alignment.center,
                  child: Opacity(
                    opacity: isLocked ? 0.4 : 1.0,
                    child: Text(
                      mastery.emoji,
                      style: const TextStyle(fontSize: 28),
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        mastery.title,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isEarned && earnedWhen != null
                            ? 'Earned on ${DateFormat('d MMM yyyy').format(earnedWhen!)}'
                            : '$progressCount of $total tasks done',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade700,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isEarned)
                  IconButton(
                    icon: Icon(Icons.share_outlined, color: color),
                    tooltip: 'Share certificate',
                    onPressed: () {
                      Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => MasteryCertificatePreview(
                          childName: childName,
                          childAge: childAge,
                          mastery: mastery,
                          earnedAt: earnedWhen ?? DateTime.now(),
                        ),
                      ));
                    },
                  ),
              ],
            ),
            if (!isEarned) ...[
              const SizedBox(height: 10),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: LinearProgressIndicator(
                  value: ratio,
                  minHeight: 6,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation(color),
                ),
              ),
            ],
            const SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.only(left: 70),
              child: Text(
                mastery.celebration,
                style: const TextStyle(fontSize: 13, height: 1.4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
