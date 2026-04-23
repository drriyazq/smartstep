import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/ladder.dart';
import '../../domain/models.dart';
import '../../providers.dart';
import 'dashboard_screen.dart' show categoryMeta;

class CategoryLadderScreen extends ConsumerStatefulWidget {
  const CategoryLadderScreen({super.key, required this.category});
  final String category;

  @override
  ConsumerState<CategoryLadderScreen> createState() =>
      _CategoryLadderScreenState();
}

class _CategoryLadderScreenState
    extends ConsumerState<CategoryLadderScreen> {
  bool _doneExpanded = false;

  @override
  Widget build(BuildContext context) {
    final activeId = ref.watch(activeChildIdProvider);
    ref.watch(progressVersionProvider);
    final asyncCatalog = ref.watch(catalogProvider);
    final meta = categoryMeta(widget.category);

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(meta.icon, color: meta.color, size: 20),
            const SizedBox(width: 8),
            Text(meta.label),
          ],
        ),
      ),
      body: asyncCatalog.when(
        data: (allTasks) =>
            _buildList(context, allTasks, activeId, meta),
        loading: () =>
            const Center(child: CircularProgressIndicator()),
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

  Widget _buildList(
    BuildContext context,
    List<Task> allTasks,
    String childId,
    ({IconData icon, String label, Color color}) meta,
  ) {
    final child = HiveSetup.childBox.get(childId)!;
    final childAge = child.ageOn(DateTime.now());

    final allProgress = HiveSetup.progressBox.values
        .where((p) => p.childId == childId)
        .toList();
    final progress = {for (final p in allProgress) p.taskSlug: p};
    final knownSlugs = allTasks.map((t) => t.slug).toSet();

    // Filter to this category and sort by minAge ascending
    final categoryTasks = allTasks.where((t) {
      final cat =
          t.tags.isEmpty ? 'other' : t.tags.first.category;
      return cat == widget.category;
    }).toList()
      ..sort((a, b) => a.minAge.compareTo(b.minAge));

    final eligibleRows = <_TaskRow>[];
    final doneRows = <_TaskRow>[];
    final skippedRows = <_TaskRow>[];

    for (final t in categoryTasks) {
      final state = computeLadderState(
        task: t,
        progressBySlug: progress,
        knownSlugs: knownSlugs,
      );
      final prog = progress[t.slug];

      if (prog?.status == ProgressStatus.skippedUnsuitable) {
        skippedRows.add(_TaskRow(t, state));
        continue;
      }
      if (state == LadderState.completed ||
          state == LadderState.satisfied) {
        doneRows.add(_TaskRow(t, state));
        continue;
      }
      if (state == LadderState.unlocked ||
          state == LadderState.lockedWithWarning) {
        // Hide tasks above the child's age that have no prerequisites
        if (t.prerequisites.isEmpty && t.minAge > childAge) continue;
        eligibleRows.add(_TaskRow(t, state));
      }
      // locked (unreachable) tasks are hidden
    }

    // Show only the first 2 eligible tasks; reveal more only after one is done
    final visibleEligible = eligibleRows.take(2).toList();
    final pct = categoryTasks.isEmpty
        ? 0.0
        : doneRows.length / categoryTasks.length;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
      children: [
        // Category progress header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: meta.color.withOpacity(0.07),
            borderRadius: BorderRadius.circular(14),
            border:
                Border.all(color: meta.color.withOpacity(0.2)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: meta.color.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(meta.icon,
                        color: meta.color, size: 22),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        Text(
                          meta.label,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: meta.color,
                          ),
                        ),
                        Text(
                          "${doneRows.length} of ${categoryTasks.length} done",
                          style: TextStyle(
                            fontSize: 12.5,
                            color: Colors.grey.shade600,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: LinearProgressIndicator(
                  value: pct,
                  minHeight: 8,
                  backgroundColor:
                      meta.color.withOpacity(0.12),
                  valueColor:
                      AlwaysStoppedAnimation<Color>(meta.color),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // ── Up Next (max 2 eligible tasks) ────────────────────
        if (visibleEligible.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.play_circle_outline,
            label: "Up Next",
            color: meta.color,
          ),
          const SizedBox(height: 10),
          ...visibleEligible.map(
            (row) => _buildTile(context, row, childId, meta),
          ),
          const SizedBox(height: 20),
        ],

        // ── All done in this category ─────────────────────────
        if (visibleEligible.isEmpty && doneRows.isNotEmpty) ...[
          _AllDoneCard(meta: meta),
          const SizedBox(height: 20),
        ],

        // ── No tasks at all ───────────────────────────────────
        if (categoryTasks.isEmpty) ...[
          _EmptyCard(meta: meta),
          const SizedBox(height: 20),
        ],

        // ── Completed / Mastered (collapsible) ─────────────────
        if (doneRows.isNotEmpty) ...[
          _DoneSectionHeader(
            count: doneRows.length,
            expanded: _doneExpanded,
            onTap: () =>
                setState(() => _doneExpanded = !_doneExpanded),
          ),
          if (_doneExpanded) ...[
            const SizedBox(height: 10),
            ...doneRows.map(
              (row) => _buildTile(context, row, childId, meta),
            ),
          ],
          const SizedBox(height: 20),
        ],

        // ── Skipped ───────────────────────────────────────────
        if (skippedRows.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.block_outlined,
            label: "Skipped",
            color: Colors.grey.shade600,
          ),
          const SizedBox(height: 10),
          ...skippedRows.map(
            (row) => _buildTile(context, row, childId, meta),
          ),
        ],
      ],
    );
  }

  Widget _buildTile(
    BuildContext context,
    _TaskRow row,
    String childId,
    ({IconData icon, String label, Color color}) meta,
  ) {
    final isSkipped = row.state == LadderState.locked;
    final isDone = row.state == LadderState.completed ||
        row.state == LadderState.satisfied;

    final countKey = 'count::$childId::${row.task.slug}';
    final practiceCount =
        (HiveSetup.sessionBox.get(countKey) as int?) ?? 0;
    final showPracticeProgress = practiceCount > 0 &&
        !isDone &&
        row.task.repetitionsRequired > 1;

    final (leadIcon, leadColor) = switch (row.state) {
      LadderState.completed =>
        (Icons.check_circle, Colors.green.shade600),
      LadderState.satisfied =>
        (Icons.check_circle_outline, Colors.green.shade500),
      LadderState.unlocked =>
        (Icons.play_circle_outline, meta.color),
      LadderState.lockedWithWarning =>
        (Icons.warning_amber_outlined, Colors.orange.shade700),
      LadderState.locked =>
        (Icons.block_outlined, Colors.grey.shade400),
    };

    final stateText = switch (row.state) {
      LadderState.completed => "Completed",
      LadderState.satisfied => "Already knows",
      LadderState.unlocked => "Ready to try",
      LadderState.lockedWithWarning =>
        "Requires a skipped skill",
      LadderState.locked => "Skipped",
    };

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isSkipped ? Colors.grey.shade50 : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSkipped
              ? Colors.grey.shade200
              : isDone
                  ? Colors.green.shade200
                  : meta.color.withOpacity(0.2),
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
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(leadIcon,
                                color: leadColor, size: 22),
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
                            Icon(Icons.chevron_right,
                                color: Colors.grey.shade400,
                                size: 20),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Padding(
                          padding:
                              const EdgeInsets.only(left: 32),
                          child: Text(
                            "$stateText · Age ${row.task.minAge}–${row.task.maxAge}",
                            style: TextStyle(
                              fontSize: 12.5,
                              color: row.state ==
                                      LadderState
                                          .lockedWithWarning
                                  ? Colors.orange.shade700
                                  : Colors.grey.shade600,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        if (showPracticeProgress) ...[
                          const SizedBox(height: 8),
                          Padding(
                            padding: const EdgeInsets.only(
                                left: 32),
                            child: _PracticeBar(
                              done: practiceCount,
                              total:
                                  row.task.repetitionsRequired,
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
}

// ─── Widgets ──────────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.icon,
    required this.label,
    required this.color,
  });
  final IconData icon;
  final String label;
  final Color color;

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
        Text(
          label,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
                color: color,
                fontSize: 15,
              ),
        ),
      ],
    );
  }
}

class _DoneSectionHeader extends StatelessWidget {
  const _DoneSectionHeader({
    required this.count,
    required this.expanded,
    required this.onTap,
  });
  final int count;
  final bool expanded;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(
              vertical: 6, horizontal: 4),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(Icons.check_circle_outline,
                    color: Colors.green.shade600, size: 18),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  "Completed",
                  style: Theme.of(context)
                      .textTheme
                      .titleSmall
                      ?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: Colors.green.shade700,
                        fontSize: 15,
                      ),
                ),
              ),
              Text(
                "$count done",
                style:
                    Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w500,
                          fontSize: 12.5,
                        ),
              ),
              const SizedBox(width: 4),
              Icon(
                expanded
                    ? Icons.expand_less
                    : Icons.expand_more,
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

class _AllDoneCard extends StatelessWidget {
  const _AllDoneCard({required this.meta});
  final ({IconData icon, String label, Color color}) meta;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Column(
        children: [
          Icon(Icons.celebration_outlined,
              size: 44, color: Colors.green.shade500),
          const SizedBox(height: 12),
          const Text(
            "All caught up!",
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            "You've finished all available ${meta.label.toLowerCase()} skills.",
            textAlign: TextAlign.center,
            style:
                TextStyle(fontSize: 13, color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }
}

class _EmptyCard extends StatelessWidget {
  const _EmptyCard({required this.meta});
  final ({IconData icon, String label, Color color}) meta;

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
        children: [
          Icon(meta.icon, size: 44, color: Colors.grey.shade400),
          const SizedBox(height: 12),
          Text(
            "No ${meta.label.toLowerCase()} skills available yet",
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}

class _PracticeBar extends StatelessWidget {
  const _PracticeBar({
    required this.done,
    required this.total,
    required this.color,
  });
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
            margin: EdgeInsets.only(
                right: i < total - 1 ? 3 : 0),
            height: 5,
            decoration: BoxDecoration(
              color: filled
                  ? color
                  : color.withOpacity(0.18),
              borderRadius: BorderRadius.circular(3),
            ),
          ),
        );
      }),
    );
  }
}

// ─── Data class ───────────────────────────────────────────────────────

class _TaskRow {
  _TaskRow(this.task, this.state);
  final Task task;
  final LadderState state;
}
