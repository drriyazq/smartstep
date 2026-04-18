import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/custom_task.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/ladder.dart';
import '../../domain/models.dart';
import '../../providers.dart';

String _sexParam(Sex sex) => switch (sex) {
      Sex.boy => "male",
      Sex.girl => "female",
      Sex.other => "any",
    };

// Fetches all tasks for this child's environment and sex.
// Age filtering happens in Flutter, not the API, so that tasks unlocked via
// prerequisites always appear regardless of the child's age.
final _catalogProvider = FutureProvider<List<Task>>((ref) async {
  final activeId = ref.watch(activeChildIdProvider);
  final child = HiveSetup.childBox.get(activeId)!;
  return ref.read(taskRepositoryProvider).fetchAll(
        environment: child.environment.name,
        sex: _sexParam(child.sex),
      );
});

({IconData icon, String label, Color color}) _categoryMeta(String cat) =>
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
      'custom' => (
          icon: Icons.star_outline,
          label: 'My Tasks',
          color: const Color(0xFF880E4F),
        ),
      _ => (
          icon: Icons.category_outlined,
          label: cat[0].toUpperCase() + cat.substring(1),
          color: const Color(0xFF546E7A),
        ),
    };

const _categoryOrder = [
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
    ref.watch(progressVersionProvider); // rebuild when any progress changes
    final child = HiveSetup.childBox.get(activeId)!;
    final asyncCatalog = ref.watch(_catalogProvider);
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
                  "${child.name}'s Ladder",
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
        data: (tasks) => _LadderList(tasks: tasks, childId: activeId),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.wifi_off, size: 48),
                const SizedBox(height: 12),
                Text("Could not fetch ladder: $e",
                    textAlign: TextAlign.center),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => ref.invalidate(_catalogProvider),
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
                "Switch Child",
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
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                title: Text(c.name),
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
              leading: const CircleAvatar(
                child: Icon(Icons.add),
              ),
              title: const Text("Add Another Child"),
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

class _LadderList extends ConsumerStatefulWidget {
  const _LadderList({required this.tasks, required this.childId});
  final List<Task> tasks;
  final String childId;

  @override
  ConsumerState<_LadderList> createState() => _LadderListState();
}

class _LadderListState extends ConsumerState<_LadderList> {
  static const _nextUpLimit = 5;
  bool _showAllNextUp = false;

  String _filterKey() => 'cat_filter::${widget.childId}';
  String _doneExpandedKey(String cat) => 'done_exp::${widget.childId}::$cat';
  String _todayPickKey(String date) => 'today_pick::${widget.childId}::$date';

  Set<String> _loadEnabledCategories() {
    final saved = HiveSetup.sessionBox.get(_filterKey()) as String?;
    return (saved != null && saved.isNotEmpty)
        ? saved.split(',').toSet()
        : <String>{};
  }

  Future<void> _toggleFilterCategory(String cat) async {
    final current = _loadEnabledCategories();
    final next = Set<String>.from(current);
    if (next.contains(cat)) {
      next.remove(cat);
    } else {
      next.add(cat);
    }
    // If they've selected every category, treat that as "All" (empty)
    final allCats = _categoryOrder.toSet();
    final toSave = (next.length == allCats.length) ? '' : next.join(',');
    await HiveSetup.sessionBox.put(_filterKey(), toSave);
    ref.read(progressVersionProvider.notifier).state++;
    if (mounted) setState(() {});
  }

  Future<void> _clearFilter() async {
    await HiveSetup.sessionBox.put(_filterKey(), '');
    ref.read(progressVersionProvider.notifier).state++;
    if (mounted) setState(() {});
  }

  bool _isDoneExpanded(String cat) =>
      (HiveSetup.sessionBox.get(_doneExpandedKey(cat)) as String?) == '1';

  Future<void> _toggleDoneExpanded(String cat) async {
    final cur = _isDoneExpanded(cat);
    await HiveSetup.sessionBox.put(_doneExpandedKey(cat), cur ? '0' : '1');
    if (mounted) setState(() {});
  }

  // ── Streak computation ──────────────────────────────────────────────
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

  // ── Today's pick ────────────────────────────────────────────────────
  Task? _pickTodaysTask(List<_TaskRow> unlockedRows) {
    if (unlockedRows.isEmpty) return null;
    final now = DateTime.now();
    final dateKey =
        "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}";
    final stored = HiveSetup.sessionBox.get(_todayPickKey(dateKey)) as String?;
    if (stored != null) {
      for (final r in unlockedRows) {
        if (r.task.slug == stored) return r.task;
      }
    }
    // Pick deterministically by date so it doesn't change on rebuilds
    final index = Random(dateKey.hashCode).nextInt(unlockedRows.length);
    final pick = unlockedRows[index].task;
    HiveSetup.sessionBox.put(_todayPickKey(dateKey), pick.slug);
    return pick;
  }

  @override
  Widget build(BuildContext context) {
    final childId = widget.childId;
    final enabledCategories = _loadEnabledCategories();
    final isFilterActive = enabledCategories.isNotEmpty;
    final tasks = !isFilterActive
        ? widget.tasks
        : widget.tasks.where((t) {
            final cat = t.tags.isEmpty ? 'other' : t.tags.first.category;
            return enabledCategories.contains(cat);
          }).toList();
    final child = HiveSetup.childBox.get(childId)!;
    final childAge = child.ageOn(DateTime.now());

    final allProgress = HiveSetup.progressBox.values
        .where((p) => p.childId == childId)
        .toList();
    final progress = {for (final p in allProgress) p.taskSlug: p};
    final taskBySlug = {for (final t in tasks) t.slug: t};

    // ── Classify every task ─────────────────────────────────────────
    final nextUpRows = <_TaskRow>[];
    final doneByCategory = <String, List<_TaskRow>>{};
    final skippedRows = <_TaskRow>[];

    for (final t in tasks) {
      final state = computeLadderState(task: t, progressBySlug: progress);
      final prog = progress[t.slug];
      final category = t.tags.isEmpty ? "other" : t.tags.first.category;
      final isAboveAge = t.minAge > childAge;
      final hasPrereqs = t.prerequisites.isNotEmpty;

      if (prog?.status == ProgressStatus.skippedUnsuitable) {
        skippedRows.add(_TaskRow(t, state));
        continue;
      }
      if (state == LadderState.completed || state == LadderState.satisfied) {
        doneByCategory.putIfAbsent(category, () => []).add(_TaskRow(t, state));
        continue;
      }
      if (state == LadderState.unlocked ||
          state == LadderState.lockedWithWarning) {
        if (!hasPrereqs && isAboveAge) continue;
        String? warningTitle;
        if (state == LadderState.lockedWithWarning) {
          for (final p in t.prerequisites) {
            if (!p.isMandatory) continue;
            if (progress[p.taskSlug]?.softSkipped == true) {
              warningTitle = taskBySlug[p.taskSlug]?.title;
              break;
            }
          }
        }
        nextUpRows.add(_TaskRow(
          t,
          state,
          warningPrereqTitle: warningTitle,
          isAboveAge: hasPrereqs && isAboveAge,
        ));
        continue;
      }
    }
    nextUpRows.sort((a, b) => a.state.index.compareTo(b.state.index));

    final visibleNextUp = _showAllNextUp
        ? nextUpRows
        : nextUpRows.take(_nextUpLimit).toList();
    final hiddenCount = nextUpRows.length - visibleNextUp.length;

    // ── Continue practising (partial practice counts) ───────────────
    final continueRow = _findContinueRow(nextUpRows);

    // ── Today's Pick (deterministic daily pick) ─────────────────────
    final unlockedOnly =
        nextUpRows.where((r) => r.state == LadderState.unlocked).toList();
    final todaysPick = _pickTodaysTask(unlockedOnly);

    // ── Custom tasks ─────────────────────────────────────────────────
    final customTasks = HiveSetup.customTaskBox.values
        .where((t) => t.childId == childId)
        .toList();

    // ── Totals ───────────────────────────────────────────────────────
    final completedCount =
        allProgress.where((p) => p.status == ProgressStatus.completed).length;
    final satisfiedCount = allProgress
        .where((p) => p.satisfies && p.status != ProgressStatus.completed)
        .length;
    final doneCount = completedCount + satisfiedCount;
    final total = tasks.length + customTasks.length;

    // ── Per-category stats (unfiltered totals so numbers make sense) ─
    final allTasksBySlug = {for (final t in widget.tasks) t.slug: t};
    final allDoneByCategory = <String, int>{};
    final allTotalByCategory = <String, int>{};
    for (final t in widget.tasks) {
      final cat = t.tags.isEmpty ? "other" : t.tags.first.category;
      allTotalByCategory[cat] = (allTotalByCategory[cat] ?? 0) + 1;
    }
    for (final p in allProgress) {
      if (!p.satisfies) continue;
      final t = allTasksBySlug[p.taskSlug];
      if (t == null) continue;
      final cat = t.tags.isEmpty ? "other" : t.tags.first.category;
      allDoneByCategory[cat] = (allDoneByCategory[cat] ?? 0) + 1;
    }
    final categoryStats = _categoryOrder
        .where((c) => (allTotalByCategory[c] ?? 0) > 0)
        .map((c) => _CategoryStat(
              category: c,
              done: allDoneByCategory[c] ?? 0,
              total: allTotalByCategory[c]!,
            ))
        .toList();

    // ── Streak + today indicator ─────────────────────────────────────
    final streak = _computeStreak(allProgress);
    final didToday = _completedToday(allProgress);

    final doneCategories = doneByCategory.keys.toList()
      ..sort((a, b) => _categoryOrder.indexOf(a).compareTo(
            _categoryOrder.indexOf(b),
          ));

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        // ── Compact progress card with streak ─────────────────────
        _ProgressCard(
          done: doneCount,
          completed: completedCount,
          total: total,
          streak: streak,
          didToday: didToday,
          categoryStats: categoryStats,
          enabledCategories: enabledCategories,
          onCategoryPillTap: _toggleFilterCategory,
        ),
        const SizedBox(height: 16),

        // ── Category filter chips ─────────────────────────────────
        _CategoryFilterBar(
          enabled: enabledCategories,
          stats: categoryStats,
          onToggle: _toggleFilterCategory,
          onClear: _clearFilter,
        ),
        const SizedBox(height: 16),

        // ── Today's Pick ──────────────────────────────────────────
        if (todaysPick != null) ...[
          _TodaysPickCard(
            task: todaysPick,
            didToday: didToday,
            onTap: () => context.push("/task/${todaysPick.slug}"),
          ),
          const SizedBox(height: 16),
        ],

        // ── Continue practising strip ─────────────────────────────
        if (continueRow != null) ...[
          _ContinuePractisingCard(
            row: continueRow,
            practiceCount: (HiveSetup.sessionBox
                    .get('count::${widget.childId}::${continueRow.task.slug}')
                as int?) ??
                0,
            onTap: () => context.push("/task/${continueRow.task.slug}"),
          ),
          const SizedBox(height: 16),
        ],

        // ── Next Up ───────────────────────────────────────────────
        if (nextUpRows.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.rocket_launch_outlined,
            label: "Next Up",
            color: Theme.of(context).colorScheme.primary,
            count: "${nextUpRows.length} available",
          ),
          const SizedBox(height: 10),
          ...visibleNextUp.map(
            (row) => _buildTile(
              context,
              row,
              row.task.tags.isEmpty ? "other" : row.task.tags.first.category,
            ),
          ),
          if (hiddenCount > 0)
            TextButton.icon(
              onPressed: () => setState(() => _showAllNextUp = true),
              icon: const Icon(Icons.expand_more, size: 18),
              label: Text("$hiddenCount more available"),
            )
          else if (_showAllNextUp && nextUpRows.length > _nextUpLimit)
            TextButton.icon(
              onPressed: () => setState(() => _showAllNextUp = false),
              icon: const Icon(Icons.expand_less, size: 18),
              label: const Text("Show fewer"),
            ),
          const SizedBox(height: 20),
        ] else
          _EmptyStateCard(
            isFiltered: isFilterActive,
            onClearFilter: isFilterActive ? _clearFilter : null,
          ),

        // ── Completed & Mastered (collapsible by category) ────────
        for (final c in doneCategories) ...[
          _CategoryHeader(
            category: c,
            rows: doneByCategory[c]!,
            expanded: _isDoneExpanded(c),
            onTap: () => _toggleDoneExpanded(c),
          ),
          if (_isDoneExpanded(c)) ...[
            const SizedBox(height: 8),
            ...doneByCategory[c]!.map(
              (row) => _buildTile(context, row, c),
            ),
          ],
          const SizedBox(height: 14),
        ],

        // ── Skipped / Unsuitable ──────────────────────────────────
        if (skippedRows.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.block_outlined,
            label: "Skipped",
            color: Colors.grey.shade600,
            count: "${skippedRows.length}",
          ),
          const SizedBox(height: 10),
          ...skippedRows.map(
            (row) => _buildTile(context, row,
                row.task.tags.isEmpty ? "other" : row.task.tags.first.category),
          ),
          const SizedBox(height: 20),
        ],

        // ── My Tasks (custom) ─────────────────────────────────────
        if (customTasks.isNotEmpty) ...[
          _CustomCategoryHeader(tasks: customTasks, childId: childId),
          const SizedBox(height: 10),
          for (final ct in customTasks)
            _buildCustomTile(context, ct, progress),
          const SizedBox(height: 20),
        ],
      ],
    );
  }

  _TaskRow? _findContinueRow(List<_TaskRow> rows) {
    _TaskRow? best;
    int bestCount = 0;
    for (final row in rows) {
      final required = row.task.repetitionsRequired;
      if (required <= 1) continue;
      final key = 'count::${widget.childId}::${row.task.slug}';
      final count = (HiveSetup.sessionBox.get(key) as int?) ?? 0;
      if (count > 0 && count < required && count > bestCount) {
        best = row;
        bestCount = count;
      }
    }
    return best;
  }

  Widget _buildTile(BuildContext context, _TaskRow row, String category) {
    final meta = _categoryMeta(category);
    final isSkipped = row.state == LadderState.locked;
    final isDone = row.state == LadderState.completed ||
        row.state == LadderState.satisfied;
    final countKey = 'count::${widget.childId}::${row.task.slug}';
    final practiceCount = (HiveSetup.sessionBox.get(countKey) as int?) ?? 0;
    final showPracticeProgress = practiceCount > 0 &&
        !isDone &&
        row.task.repetitionsRequired > 1;

    final (leadIcon, leadColor) = switch (row.state) {
      LadderState.completed => (Icons.check_circle, Colors.green.shade600),
      LadderState.satisfied =>
        (Icons.check_circle_outline, Colors.green.shade500),
      LadderState.unlocked => (Icons.play_circle_outline, meta.color),
      LadderState.lockedWithWarning =>
        (Icons.warning_amber_outlined, Colors.orange.shade700),
      LadderState.locked => (Icons.block_outlined, Colors.grey.shade400),
    };

    // One-line subtitle summary
    final stateText = _subtitle(row);
    final subtitleParts = <String>[
      stateText,
      meta.label,
      "Age ${row.task.minAge}–${row.task.maxAge}",
    ];

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isSkipped ? Colors.grey.shade50 : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSkipped
              ? Colors.grey.shade200
              : meta.color.withOpacity(0.15),
        ),
        boxShadow: isSkipped
            ? null
            : [
                BoxShadow(
                  color: Colors.black.withOpacity(0.03),
                  blurRadius: 4,
                  offset: const Offset(0, 1),
                ),
              ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () => context.push("/task/${row.task.slug}"),
          child: IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Left accent stripe
                Container(
                  width: 4,
                  decoration: BoxDecoration(
                    color: isSkipped
                        ? Colors.grey.shade300
                        : isDone
                            ? Colors.green.shade400
                            : meta.color,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(12),
                      bottomLeft: Radius.circular(12),
                    ),
                  ),
                ),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(leadIcon, color: leadColor, size: 22),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                row.task.title,
                                style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w600,
                                  color: isSkipped
                                      ? Colors.grey.shade500
                                      : Colors.black87,
                                ),
                              ),
                            ),
                            if (row.isAboveAge)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: Colors.amber.shade100,
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(
                                      color: Colors.amber.shade400,
                                      width: 0.8),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.star,
                                        size: 11,
                                        color: Colors.amber.shade800),
                                    const SizedBox(width: 2),
                                    Text(
                                      "Advanced",
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.amber.shade800,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            const SizedBox(width: 4),
                            Icon(Icons.chevron_right,
                                color: Colors.grey.shade400, size: 20),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Padding(
                          padding: const EdgeInsets.only(left: 32),
                          child: Text(
                            subtitleParts.join(" · "),
                            style: TextStyle(
                              fontSize: 12.5,
                              color: row.state == LadderState.lockedWithWarning
                                  ? Colors.orange.shade700
                                  : Colors.grey.shade600,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        if (showPracticeProgress) ...[
                          const SizedBox(height: 8),
                          Padding(
                            padding: const EdgeInsets.only(left: 32),
                            child: _PracticeBar(
                              done: practiceCount,
                              total: row.task.repetitionsRequired,
                              color: meta.color,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCustomTile(
    BuildContext context,
    CustomTask ct,
    Map<String, TaskProgress> progress,
  ) {
    final prog = progress[ct.progressSlug];
    final isDone = prog?.status == ProgressStatus.completed;
    final meta = _categoryMeta('custom');

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: meta.color.withOpacity(0.15)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () => context.push("/custom-task/${ct.id}"),
          child: IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  width: 4,
                  decoration: BoxDecoration(
                    color: isDone ? Colors.green.shade400 : meta.color,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(12),
                      bottomLeft: Radius.circular(12),
                    ),
                  ),
                ),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 12),
                    child: Row(
                      children: [
                        Icon(
                          isDone
                              ? Icons.check_circle
                              : Icons.play_circle_outline,
                          color:
                              isDone ? Colors.green.shade600 : meta.color,
                          size: 22,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                ct.title,
                                style: const TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.black87,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                isDone ? "Completed" : "Ready to try",
                                style: TextStyle(
                                  fontSize: 12.5,
                                  color: Colors.grey.shade600,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(Icons.chevron_right,
                            color: Colors.grey.shade400, size: 20),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _subtitle(_TaskRow row) => switch (row.state) {
        LadderState.completed => "Completed",
        LadderState.satisfied => "Already knows",
        LadderState.unlocked =>
          row.isAboveAge ? "Above their age — impressive!" : "Ready to try",
        LadderState.lockedWithWarning => row.warningPrereqTitle != null
            ? 'Needs: "${row.warningPrereqTitle}"'
            : "Requires a skipped skill",
        LadderState.locked => "Skipped",
      };
}

// ─── Progress Card (compact with streak + horizontal pills) ──────────

class _ProgressCard extends StatelessWidget {
  const _ProgressCard({
    required this.done,
    required this.completed,
    required this.total,
    required this.streak,
    required this.didToday,
    required this.categoryStats,
    required this.enabledCategories,
    required this.onCategoryPillTap,
  });
  final int done;
  final int completed;
  final int total;
  final int streak;
  final bool didToday;
  final List<_CategoryStat> categoryStats;
  final Set<String> enabledCategories;
  final Future<void> Function(String) onCategoryPillTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final pct = total == 0 ? 0.0 : done / total;
    return Card(
      elevation: 0,
      color: cs.primaryContainer,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
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
                    style:
                        Theme.of(context).textTheme.titleMedium?.copyWith(
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
                backgroundColor: cs.onPrimaryContainer.withOpacity(0.15),
                valueColor:
                    AlwaysStoppedAnimation<Color>(cs.onPrimaryContainer),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              completed > 0
                  ? "$completed completed · ${done - completed} already mastered"
                  : "Tap any unlocked skill to get started",
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: cs.onPrimaryContainer.withOpacity(0.8),
                    fontSize: 12.5,
                  ),
            ),
            if (categoryStats.isNotEmpty) ...[
              const SizedBox(height: 14),
              SizedBox(
                height: 38,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: categoryStats.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (ctx, i) {
                    final stat = categoryStats[i];
                    final meta = _categoryMeta(stat.category);
                    final selected =
                        enabledCategories.contains(stat.category);
                    return _CategoryPill(
                      stat: stat,
                      meta: meta,
                      selected: selected,
                      onPrimary: cs.onPrimaryContainer,
                      onTap: () => onCategoryPillTap(stat.category),
                    );
                  },
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _CategoryPill extends StatelessWidget {
  const _CategoryPill({
    required this.stat,
    required this.meta,
    required this.selected,
    required this.onPrimary,
    required this.onTap,
  });
  final _CategoryStat stat;
  final ({IconData icon, String label, Color color}) meta;
  final bool selected;
  final Color onPrimary;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final bg = selected
        ? onPrimary.withOpacity(0.25)
        : onPrimary.withOpacity(0.08);
    final border =
        selected ? onPrimary : onPrimary.withOpacity(0.15);
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: border, width: selected ? 1.5 : 1),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(meta.icon, color: onPrimary, size: 14),
              const SizedBox(width: 6),
              Text(
                meta.label,
                style: TextStyle(
                  fontSize: 12.5,
                  fontWeight: FontWeight.w600,
                  color: onPrimary,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                "${stat.done}/${stat.total}",
                style: TextStyle(
                  fontSize: 11.5,
                  color: onPrimary.withOpacity(0.85),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Category filter chip bar ────────────────────────────────────────

class _CategoryFilterBar extends StatelessWidget {
  const _CategoryFilterBar({
    required this.enabled,
    required this.stats,
    required this.onToggle,
    required this.onClear,
  });
  final Set<String> enabled;
  final List<_CategoryStat> stats;
  final Future<void> Function(String) onToggle;
  final Future<void> Function() onClear;

  @override
  Widget build(BuildContext context) {
    if (stats.isEmpty) return const SizedBox.shrink();
    final allActive = enabled.isEmpty;
    return SizedBox(
      height: 36,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          _FilterChip(
            label: "All",
            icon: Icons.apps_outlined,
            color: Theme.of(context).colorScheme.primary,
            selected: allActive,
            onTap: allActive ? () {} : onClear,
          ),
          const SizedBox(width: 8),
          for (final stat in stats) ...[
            _FilterChip(
              label: _categoryMeta(stat.category).label,
              icon: _categoryMeta(stat.category).icon,
              color: _categoryMeta(stat.category).color,
              selected: enabled.contains(stat.category),
              onTap: () => onToggle(stat.category),
            ),
            const SizedBox(width: 8),
          ],
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.icon,
    required this.color,
    required this.selected,
    required this.onTap,
  });
  final String label;
  final IconData icon;
  final Color color;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
          decoration: BoxDecoration(
            color: selected ? color : color.withOpacity(0.08),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: selected ? color : color.withOpacity(0.3),
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 14, color: selected ? Colors.white : color),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: selected ? Colors.white : color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Today's Pick ─────────────────────────────────────────────────────

class _TodaysPickCard extends StatelessWidget {
  const _TodaysPickCard({
    required this.task,
    required this.didToday,
    required this.onTap,
  });
  final Task task;
  final bool didToday;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final category =
        task.tags.isEmpty ? "other" : task.tags.first.category;
    final meta = _categoryMeta(category);
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                meta.color.withOpacity(0.12),
                meta.color.withOpacity(0.04),
              ],
            ),
            border: Border.all(color: meta.color.withOpacity(0.3), width: 1.2),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: meta.color,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text("✨", style: TextStyle(fontSize: 12)),
                        SizedBox(width: 4),
                        Text(
                          "TODAY'S PICK",
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.5,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Spacer(),
                  if (didToday)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.check_circle,
                              size: 12, color: Colors.green.shade700),
                          const SizedBox(width: 3),
                          Text(
                            "Active today",
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: Colors.green.shade700,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(meta.icon, color: meta.color, size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      task.title,
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w700,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                  Icon(Icons.arrow_forward, color: meta.color, size: 22),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                "${meta.label} · Age ${task.minAge}–${task.maxAge}",
                style: TextStyle(
                  fontSize: 12.5,
                  color: meta.color.withOpacity(0.85),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Continue Practising ──────────────────────────────────────────────

class _ContinuePractisingCard extends StatelessWidget {
  const _ContinuePractisingCard({
    required this.row,
    required this.practiceCount,
    required this.onTap,
  });
  final _TaskRow row;
  final int practiceCount;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final category =
        row.task.tags.isEmpty ? "other" : row.task.tags.first.category;
    final meta = _categoryMeta(category);
    final required = row.task.repetitionsRequired;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: Colors.blue.shade200),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.shade100,
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.replay,
                    color: Colors.blue.shade700, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Keep practising",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.3,
                        color: Colors.blue.shade700,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      row.task.title,
                      style: const TextStyle(
                        fontSize: 14.5,
                        fontWeight: FontWeight.w700,
                        color: Colors.black87,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 6),
                    _PracticeBar(
                      done: practiceCount,
                      total: required,
                      color: meta.color,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "$practiceCount of $required practices done",
                      style: TextStyle(
                        fontSize: 11.5,
                        color: Colors.grey.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 6),
              Icon(Icons.chevron_right, color: Colors.grey.shade500),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Practice bar (used in tiles + continue card) ─────────────────────

class _PracticeBar extends StatelessWidget {
  const _PracticeBar(
      {required this.done, required this.total, required this.color});
  final int done;
  final int total;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(total, (i) {
        final filled = i < done;
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(right: i < total - 1 ? 3 : 0),
            height: 5,
            decoration: BoxDecoration(
              color: filled ? color : color.withOpacity(0.18),
              borderRadius: BorderRadius.circular(3),
            ),
          ),
        );
      }),
    );
  }
}

// ─── Section / Category Headers ───────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.icon,
    required this.label,
    required this.color,
    required this.count,
  });
  final IconData icon;
  final String label;
  final Color color;
  final String count;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 18),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            label,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: color,
                  fontSize: 15,
                ),
          ),
        ),
        Text(
          count,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
                fontSize: 12.5,
              ),
        ),
      ],
    );
  }
}

class _CategoryHeader extends StatelessWidget {
  const _CategoryHeader({
    required this.category,
    required this.rows,
    required this.expanded,
    required this.onTap,
  });
  final String category;
  final List<_TaskRow> rows;
  final bool expanded;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final meta = _categoryMeta(category);
    final doneInCat = rows
        .where((r) =>
            r.state == LadderState.completed ||
            r.state == LadderState.satisfied)
        .length;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: meta.color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(meta.icon, color: meta.color, size: 18),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  meta.label,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: meta.color,
                        fontSize: 15,
                      ),
                ),
              ),
              Text(
                "$doneInCat done",
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey.shade600,
                      fontWeight: FontWeight.w500,
                      fontSize: 12.5,
                    ),
              ),
              const SizedBox(width: 4),
              Icon(
                expanded ? Icons.expand_less : Icons.expand_more,
                color: Colors.grey.shade500,
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CustomCategoryHeader extends StatelessWidget {
  const _CustomCategoryHeader(
      {required this.tasks, required this.childId});
  final List<CustomTask> tasks;
  final String childId;

  @override
  Widget build(BuildContext context) {
    final meta = _categoryMeta('custom');
    final doneCount = tasks.where((t) {
      final prog = HiveSetup.progressBox
          .get(TaskProgress.key(childId, t.progressSlug));
      return prog?.status == ProgressStatus.completed;
    }).length;

    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: meta.color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(meta.icon, color: meta.color, size: 18),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            meta.label,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: meta.color,
                  fontSize: 15,
                ),
          ),
        ),
        Text(
          "$doneCount / ${tasks.length}",
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
                fontSize: 12.5,
              ),
        ),
      ],
    );
  }
}

// ─── Empty state ──────────────────────────────────────────────────────

class _EmptyStateCard extends StatelessWidget {
  const _EmptyStateCard({
    required this.isFiltered,
    this.onClearFilter,
  });
  final bool isFiltered;
  final Future<void> Function()? onClearFilter;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(
            isFiltered ? Icons.filter_alt_outlined : Icons.celebration_outlined,
            size: 44,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 12),
          Text(
            isFiltered ? "No tasks in this filter" : "All caught up!",
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            isFiltered
                ? "Try another category, or show them all."
                : "New skills unlock as your child practises.",
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey.shade600,
            ),
          ),
          if (isFiltered && onClearFilter != null) ...[
            const SizedBox(height: 12),
            TextButton.icon(
              onPressed: onClearFilter,
              icon: const Icon(Icons.close, size: 16),
              label: const Text("Show all categories"),
            ),
          ],
        ],
      ),
    );
  }
}

// ─── Data classes ─────────────────────────────────────────────────────

class _CategoryStat {
  const _CategoryStat(
      {required this.category, required this.done, required this.total});
  final String category;
  final int done;
  final int total;
}

class _TaskRow {
  _TaskRow(this.task, this.state,
      {this.warningPrereqTitle, this.isAboveAge = false});
  final Task task;
  final LadderState state;
  final String? warningPrereqTitle;
  final bool isAboveAge;
}
