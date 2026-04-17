import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/api/reward_repository.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/reward_usage.dart';
import '../../domain/models.dart';

final _rewardsProvider = FutureProvider.family<List<Reward>, int>((ref, age) {
  return ref.read(rewardRepositoryProvider).fetch(age: age);
});

/// Shows rewards grouped by category, biasing *against* categories this parent has
/// picked most recently for this child.
class RewardPickerSheet extends ConsumerWidget {
  const RewardPickerSheet({super.key, required this.childId});
  final String childId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final child = HiveSetup.childBox.get(childId)!;
    final age = child.ageOn(DateTime.now());
    final asyncRewards = ref.watch(_rewardsProvider(age));

    return asyncRewards.when(
      data: (rewards) => _build(context, rewards),
      loading: () => const SizedBox(
        height: 200,
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (e, _) => SizedBox(
        height: 200,
        child: Center(child: Text("Couldn't load rewards: $e")),
      ),
    );
  }

  Widget _build(BuildContext context, List<Reward> rewards) {
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
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text("Pick a reward",
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
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
                          if (overused.contains(category))
                            const Padding(
                              padding: EdgeInsets.only(left: 8),
                              child: Text("· used recently",
                                  style: TextStyle(color: Colors.grey)),
                            )
                          else
                            const Padding(
                              padding: EdgeInsets.only(left: 8),
                              child: Text("· fresh pick",
                                  style: TextStyle(color: Colors.green)),
                            ),
                        ],
                      ),
                    ),
                    for (final r in grouped[category]!)
                      ListTile(
                        title: Text(r.title),
                        subtitle: r.notes.isEmpty ? null : Text(r.notes),
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
                          if (context.mounted) Navigator.of(context).pop(r.title);
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
