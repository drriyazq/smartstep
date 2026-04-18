import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/api/reward_repository.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/reward_usage.dart';
import '../../domain/models.dart';

final _rewardsProvider = FutureProvider.family<List<Reward>, int>((ref, age) {
  return ref.read(rewardRepositoryProvider).fetch(age: age);
});

/// Shows rewards grouped by category. Returns the chosen reward title,
/// or an empty string if the parent skips the reward step.
/// Returns null only if dismissed without completing (sheet swiped away).
class RewardPickerSheet extends ConsumerWidget {
  const RewardPickerSheet({super.key, required this.childId});
  final String childId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final child = HiveSetup.childBox.get(childId)!;
    final age = child.ageOn(DateTime.now());
    final asyncRewards = ref.watch(_rewardsProvider(age));

    return asyncRewards.when(
      data: (rewards) => _RewardList(
        childId: childId,
        rewards: rewards,
      ),
      loading: () => const SizedBox(
        height: 200,
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (e, _) => _SkipOnly(
        message: "Couldn't load rewards.",
        context: context,
      ),
    );
  }
}

class _RewardList extends StatelessWidget {
  const _RewardList({required this.childId, required this.rewards});
  final String childId;
  final List<Reward> rewards;

  @override
  Widget build(BuildContext context) {
    final recent = HiveSetup.rewardUsageBox.values
        .where((u) => u.childId == childId)
        .toList()
      ..sort((a, b) => b.usedAt.compareTo(a.usedAt));
    final overused = recent.take(3).map((u) => u.rewardCategory).toSet();

    final grouped = <String, List<Reward>>{};
    for (final r in rewards) {
      grouped.putIfAbsent(r.category, () => []).add(r);
    }

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text("Pick a reward",
                      style: Theme.of(context).textTheme.titleLarge),
                ),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(""),
                  child: const Text("Skip reward"),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (rewards.isEmpty)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Text(
                  "No rewards set up for this age yet.",
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              )
            else
              Flexible(
                child: ListView(
                  shrinkWrap: true,
                  children: [
                    for (final category in grouped.keys) ...[
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          children: [
                            Text(
                              category[0].toUpperCase() + category.substring(1),
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                            Padding(
                              padding: const EdgeInsets.only(left: 8),
                              child: Text(
                                overused.contains(category)
                                    ? "· used recently"
                                    : "· fresh pick",
                                style: TextStyle(
                                  color: overused.contains(category)
                                      ? Colors.grey
                                      : Colors.green,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      for (final r in grouped[category]!)
                        ListTile(
                          title: Text(r.title),
                          subtitle:
                              r.notes.isEmpty ? null : Text(r.notes),
                          trailing: r.isFree
                              ? null
                              : const Icon(Icons.attach_money, size: 16),
                          onTap: () async {
                            await HiveSetup.rewardUsageBox.add(RewardUsage(
                              childId: childId,
                              rewardCategory: r.category,
                              rewardTitle: r.title,
                              usedAt: DateTime.now(),
                            ));
                            if (context.mounted) {
                              Navigator.of(context).pop(r.title);
                            }
                          },
                        ),
                    ],
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _SkipOnly extends StatelessWidget {
  const _SkipOnly({required this.message, required this.context});
  final String message;
  final BuildContext context;

  @override
  Widget build(BuildContext ctx) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(message, style: TextStyle(color: Colors.grey.shade600)),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => Navigator.of(ctx).pop(""),
              child: const Text("Complete without reward"),
            ),
          ],
        ),
      ),
    );
  }
}
