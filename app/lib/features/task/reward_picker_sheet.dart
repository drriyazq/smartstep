import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../data/api/reward_repository.dart';
import '../../data/local/custom_reward.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/reward_usage.dart';
import '../../domain/models.dart';

final _rewardsProvider = FutureProvider.family<List<Reward>, int>((ref, age) {
  return ref.read(rewardRepositoryProvider).fetch(age: age);
});

/// A unified reward entry used for both API rewards and custom rewards.
class _Entry {
  _Entry({
    required this.category,
    required this.title,
    required this.notes,
    required this.isFree,
    this.isCustom = false,
  });
  final String category;
  final String title;
  final String notes;
  final bool isFree;
  final bool isCustom;
}

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

    final customRewards = HiveSetup.customRewardBox.values
        .where((r) => r.childId == childId)
        .toList();

    return asyncRewards.when(
      data: (rewards) => _RewardList(
        childId: childId,
        apiRewards: rewards,
        customRewards: customRewards,
      ),
      loading: () => _RewardList(
        childId: childId,
        apiRewards: const [],
        customRewards: customRewards,
        loading: true,
      ),
      error: (e, _) => _RewardList(
        childId: childId,
        apiRewards: const [],
        customRewards: customRewards,
        errorMessage: "Couldn't load rewards.",
      ),
    );
  }
}

class _RewardList extends StatelessWidget {
  const _RewardList({
    required this.childId,
    required this.apiRewards,
    required this.customRewards,
    this.loading = false,
    this.errorMessage,
  });
  final String childId;
  final List<Reward> apiRewards;
  final List<CustomReward> customRewards;
  final bool loading;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
    final recent = HiveSetup.rewardUsageBox.values
        .where((u) => u.childId == childId)
        .toList()
      ..sort((a, b) => b.usedAt.compareTo(a.usedAt));
    final overused = recent.take(3).map((u) => u.rewardCategory).toSet();

    // Build past-use lookup: rewardTitle -> sorted list of dates
    final pastUses = <String, List<DateTime>>{};
    for (final u in HiveSetup.rewardUsageBox.values.where((u) => u.childId == childId)) {
      pastUses.putIfAbsent(u.rewardTitle, () => []).add(u.usedAt);
    }
    for (final dates in pastUses.values) {
      dates.sort((a, b) => b.compareTo(a));
    }

    // Merge API rewards + custom rewards into _Entry list
    final entries = <_Entry>[
      for (final r in apiRewards)
        _Entry(
          category: r.category,
          title: r.title,
          notes: r.notes,
          isFree: r.isFree,
        ),
      for (final r in customRewards)
        _Entry(
          category: CustomReward.category,
          title: r.title,
          notes: r.notes,
          isFree: r.isFree,
          isCustom: true,
        ),
    ];

    final grouped = <String, List<_Entry>>{};
    for (final e in entries) {
      grouped.putIfAbsent(e.category, () => []).add(e);
    }

    final hasAnyRewards = entries.isNotEmpty;

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
            if (loading && !hasAnyRewards)
              const SizedBox(
                height: 120,
                child: Center(child: CircularProgressIndicator()),
              )
            else if (errorMessage != null && !hasAnyRewards)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Column(
                  children: [
                    Text(errorMessage!,
                        style: TextStyle(color: Colors.grey.shade600)),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => Navigator.of(context).pop(""),
                      child: const Text("Complete without reward"),
                    ),
                  ],
                ),
              )
            else if (!hasAnyRewards)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Text(
                  "No rewards set up yet. Add custom rewards in Profile.",
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
                              category[0].toUpperCase() +
                                  category.substring(1),
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                            if (category != CustomReward.category)
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
                      for (final entry in grouped[category]!)
                        _RewardTile(
                          entry: entry,
                          pastDates: pastUses[entry.title] ?? const [],
                          childId: childId,
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

class _RewardTile extends StatelessWidget {
  const _RewardTile({
    required this.entry,
    required this.pastDates,
    required this.childId,
  });
  final _Entry entry;
  final List<DateTime> pastDates;
  final String childId;

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('d MMM yy');
    final subtitle = _buildSubtitle(fmt);

    return ListTile(
      title: Text(entry.title),
      subtitle: subtitle != null
          ? Text(subtitle,
              style: TextStyle(
                  fontSize: 11,
                  color: pastDates.isEmpty
                      ? Colors.grey.shade500
                      : Colors.orange.shade700))
          : null,
      trailing: entry.isFree
          ? null
          : const Icon(Icons.attach_money, size: 16),
      onTap: () async {
        final category = entry.isCustom ? CustomReward.category : entry.category;
        await HiveSetup.rewardUsageBox.add(RewardUsage(
          childId: childId,
          rewardCategory: category,
          rewardTitle: entry.title,
          usedAt: DateTime.now(),
        ));
        if (context.mounted) {
          Navigator.of(context).pop(entry.title);
        }
      },
    );
  }

  String? _buildSubtitle(DateFormat fmt) {
    if (entry.notes.isNotEmpty && pastDates.isEmpty) return entry.notes;
    if (pastDates.isEmpty) return null;
    final recent = pastDates.take(2).map((d) => fmt.format(d)).join(', ');
    final suffix = pastDates.length > 2 ? ' +${pastDates.length - 2} more' : '';
    final base = 'Given: $recent$suffix';
    return entry.notes.isNotEmpty ? '$base · ${entry.notes}' : base;
  }
}

