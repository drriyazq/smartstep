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

({IconData icon, Color color, String label}) _categoryMeta(String cat) =>
    switch (cat.toLowerCase()) {
      'time' || 'time & freedom' => (
          icon: Icons.hourglass_bottom_outlined,
          color: const Color(0xFFE65100),
          label: 'Time & Freedom',
        ),
      'experience' => (
          icon: Icons.explore_outlined,
          color: const Color(0xFF2E7D32),
          label: 'Experience',
        ),
      'material' => (
          icon: Icons.card_giftcard_outlined,
          color: const Color(0xFF1565C0),
          label: 'Material',
        ),
      _ => (
          icon: Icons.star_outlined,
          color: const Color(0xFF6A1B9A),
          label: cat,
        ),
    };

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

class _RewardList extends StatefulWidget {
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
  State<_RewardList> createState() => _RewardListState();
}

class _RewardListState extends State<_RewardList> {
  // Track which category sections are expanded; default all open
  final Set<String> _collapsed = {};

  @override
  Widget build(BuildContext context) {
    final recent = HiveSetup.rewardUsageBox.values
        .where((u) => u.childId == widget.childId)
        .toList()
      ..sort((a, b) => b.usedAt.compareTo(a.usedAt));

    // Overused = appeared in last 3 picks
    final overused = recent.take(3).map((u) => u.rewardCategory).toSet();

    // Past-use lookup: rewardTitle → sorted dates
    final pastUses = <String, List<DateTime>>{};
    for (final u in HiveSetup.rewardUsageBox.values
        .where((u) => u.childId == widget.childId)) {
      pastUses.putIfAbsent(u.rewardTitle, () => []).add(u.usedAt);
    }
    for (final dates in pastUses.values) {
      dates.sort((a, b) => b.compareTo(a));
    }

    final entries = <_Entry>[
      for (final r in widget.apiRewards)
        _Entry(
          category: r.category,
          title: r.title,
          notes: r.notes,
          isFree: r.isFree,
        ),
      for (final r in widget.customRewards)
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

    // Canonical display order: time → experience → material → custom
    final orderedKeys = [
      ...['time', 'experience', 'material']
          .where((k) => grouped.containsKey(k)),
      ...grouped.keys
          .where((k) => !['time', 'experience', 'material'].contains(k)),
    ];

    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ── Handle + header ──────────────────────────────────────
          Center(
            child: Container(
              margin: const EdgeInsets.only(top: 10, bottom: 4),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 10, 12, 8),
            child: Row(
              children: [
                const Icon(Icons.emoji_events_outlined,
                    color: Color(0xFFF9A825), size: 26),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Choose a reward",
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      Text(
                        "A well-earned treat for completing this skill",
                        style: TextStyle(
                            fontSize: 12, color: Colors.grey.shade500),
                      ),
                    ],
                  ),
                ),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(""),
                  child: Text(
                    "Skip",
                    style:
                        TextStyle(color: Colors.grey.shade500, fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          // ── Body ─────────────────────────────────────────────────
          if (widget.loading && entries.isEmpty)
            const SizedBox(
              height: 140,
              child: Center(child: CircularProgressIndicator()),
            )
          else if (widget.errorMessage != null && entries.isEmpty)
            Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.wifi_off_outlined,
                      size: 40, color: Colors.grey.shade400),
                  const SizedBox(height: 10),
                  Text(widget.errorMessage!,
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey.shade600)),
                  const SizedBox(height: 14),
                  FilledButton(
                    onPressed: () => Navigator.of(context).pop(""),
                    child: const Text("Complete without reward"),
                  ),
                ],
              ),
            )
          else if (entries.isEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 20, 24, 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.card_giftcard_outlined,
                      size: 40, color: Colors.grey.shade400),
                  const SizedBox(height: 10),
                  Text(
                    "No rewards yet",
                    style: const TextStyle(
                        fontWeight: FontWeight.w700, fontSize: 15),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    "Add custom rewards in Profile to celebrate this achievement.",
                    textAlign: TextAlign.center,
                    style:
                        TextStyle(color: Colors.grey.shade600, fontSize: 13),
                  ),
                ],
              ),
            )
          else
            Flexible(
              child: ListView(
                shrinkWrap: true,
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                children: [
                  for (final catKey in orderedKeys) ...[
                    _CategorySection(
                      catKey: catKey,
                      entries: grouped[catKey]!,
                      pastUses: pastUses,
                      overused: overused,
                      collapsed: _collapsed.contains(catKey),
                      onToggle: () => setState(() {
                        if (_collapsed.contains(catKey)) {
                          _collapsed.remove(catKey);
                        } else {
                          _collapsed.add(catKey);
                        }
                      }),
                      childId: widget.childId,
                    ),
                    const SizedBox(height: 6),
                  ],
                ],
              ),
            ),
        ],
      ),
    );
  }
}

// ─── Category section (collapsible) ──────────────────────────────────

class _CategorySection extends StatelessWidget {
  const _CategorySection({
    required this.catKey,
    required this.entries,
    required this.pastUses,
    required this.overused,
    required this.collapsed,
    required this.onToggle,
    required this.childId,
  });
  final String catKey;
  final List<_Entry> entries;
  final Map<String, List<DateTime>> pastUses;
  final Set<String> overused;
  final bool collapsed;
  final VoidCallback onToggle;
  final String childId;

  @override
  Widget build(BuildContext context) {
    final meta = _categoryMeta(catKey);
    final isOverused = overused.contains(catKey);
    final freeCount = entries.where((e) => e.isFree).length;

    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border:
            Border.all(color: meta.color.withOpacity(0.2), width: 1.2),
      ),
      child: Column(
        children: [
          // Section header
          InkWell(
            borderRadius: const BorderRadius.vertical(
                top: Radius.circular(14),
                bottom: Radius.circular(14)),
            onTap: onToggle,
            child: Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(
                      color: meta.color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(9),
                    ),
                    child: Icon(meta.icon, color: meta.color, size: 18),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          meta.label,
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 13.5,
                            color: meta.color,
                          ),
                        ),
                        Text(
                          "${entries.length} options · $freeCount free",
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey.shade500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (isOverused)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(10),
                        border:
                            Border.all(color: Colors.orange.shade200),
                      ),
                      child: Text(
                        "used recently",
                        style: TextStyle(
                            fontSize: 10.5,
                            color: Colors.orange.shade800,
                            fontWeight: FontWeight.w600),
                      ),
                    )
                  else if (catKey != CustomReward.category.toLowerCase())
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: Colors.green.shade200),
                      ),
                      child: Text(
                        "fresh pick",
                        style: TextStyle(
                            fontSize: 10.5,
                            color: Colors.green.shade800,
                            fontWeight: FontWeight.w600),
                      ),
                    ),
                  const SizedBox(width: 6),
                  Icon(
                    collapsed ? Icons.expand_more : Icons.expand_less,
                    color: Colors.grey.shade400,
                    size: 20,
                  ),
                ],
              ),
            ),
          ),
          if (!collapsed) ...[
            Divider(
                height: 1, color: meta.color.withOpacity(0.15), indent: 14),
            ...entries.map((entry) => _RewardCard(
                  entry: entry,
                  meta: meta,
                  pastDates: pastUses[entry.title] ?? const [],
                  childId: childId,
                  isLast: entry == entries.last,
                )),
          ],
        ],
      ),
    );
  }
}

// ─── Single reward card ───────────────────────────────────────────────

class _RewardCard extends StatelessWidget {
  const _RewardCard({
    required this.entry,
    required this.meta,
    required this.pastDates,
    required this.childId,
    required this.isLast,
  });
  final _Entry entry;
  final ({IconData icon, Color color, String label}) meta;
  final List<DateTime> pastDates;
  final String childId;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('d MMM yy');
    final usedRecently = pastDates.isNotEmpty &&
        DateTime.now().difference(pastDates.first).inDays <= 14;

    return InkWell(
      borderRadius: isLast
          ? const BorderRadius.vertical(bottom: Radius.circular(14))
          : BorderRadius.zero,
      onTap: () async {
        final category =
            entry.isCustom ? CustomReward.category : entry.category;
        await HiveSetup.rewardUsageBox.add(RewardUsage(
          childId: childId,
          rewardCategory: category,
          rewardTitle: entry.title,
          usedAt: DateTime.now(),
        ));
        if (context.mounted) Navigator.of(context).pop(entry.title);
      },
      child: Padding(
        padding: const EdgeInsets.fromLTRB(14, 11, 14, 11),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Left accent dot
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: usedRecently
                      ? Colors.orange.shade300
                      : meta.color.withOpacity(0.5),
                ),
              ),
            ),
            const SizedBox(width: 10),
            // Title + sub-info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    entry.title,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: Colors.black87,
                    ),
                  ),
                  if (pastDates.isNotEmpty) ...[
                    const SizedBox(height: 3),
                    Row(
                      children: [
                        Icon(Icons.history,
                            size: 11, color: Colors.orange.shade600),
                        const SizedBox(width: 3),
                        Text(
                          "Last given ${fmt.format(pastDates.first)}"
                          "${pastDates.length > 1 ? ' · ${pastDates.length}× total' : ''}",
                          style: TextStyle(
                              fontSize: 11,
                              color: Colors.orange.shade700),
                        ),
                      ],
                    ),
                  ] else if (entry.notes.isNotEmpty) ...[
                    const SizedBox(height: 3),
                    Text(
                      entry.notes,
                      style: TextStyle(
                          fontSize: 11.5, color: Colors.grey.shade500),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(width: 8),
            // Free / paid badge
            if (entry.isFree)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Text(
                  "Free",
                  style: TextStyle(
                    fontSize: 10.5,
                    fontWeight: FontWeight.w700,
                    color: Colors.green.shade700,
                  ),
                ),
              )
            else
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.amber.shade200),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.currency_rupee,
                        size: 10, color: Colors.amber.shade800),
                    Text(
                      "Costs",
                      style: TextStyle(
                        fontSize: 10.5,
                        fontWeight: FontWeight.w700,
                        color: Colors.amber.shade800,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
