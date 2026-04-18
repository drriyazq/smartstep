/// Priority scoring for Next Up ordering.
///
/// A pure-function pass that replaces the old `sort by state.index` with a
/// score blending:
///   * state (unlocked vs lockedWithWarning)
///   * close-to-done — tasks where practice has been started but not finished
///   * gateway — tasks that unlock many downstream skills
///   * sweet spot — tasks whose age band contains the child's age
///   * above-age — tasks unlocked via prereqs despite being above age
///   * stable daily jitter — seeded by date so ordering refreshes each day
///     but stays consistent within a day
///
/// Then a category-balance pass gently interleaves categories so a run of
/// same-category tasks never exceeds [maxRun].
import 'models.dart';

class PriorityScored {
  const PriorityScored({
    required this.slug,
    required this.score,
    required this.unlocksDownstream,
  });
  final String slug;
  final double score;
  final int unlocksDownstream;
}

/// Score every candidate task. Returns a map keyed by slug.
///
/// [candidates] — the set of tasks to score (typically unlocked + lockedWithWarning)
/// [allTasks] — full catalog for the child, used to count downstream dependencies
/// [isUnlocked] — per-slug: true if fully unlocked, false if lockedWithWarning
/// [isAboveAge] — per-slug: true if unlocked via prereqs despite being above age
/// [childAge] — child's current age in years
/// [practiceCounts] — per-slug: number of practice sessions completed so far
/// [today] — the date used to seed stable daily jitter
Map<String, PriorityScored> scoreTasks({
  required List<Task> candidates,
  required List<Task> allTasks,
  required Map<String, bool> isUnlocked,
  required Map<String, bool> isAboveAge,
  required int childAge,
  required Map<String, int> practiceCounts,
  required DateTime today,
}) {
  // Reverse DAG: how many tasks depend on this one as a mandatory prereq?
  final downstream = <String, int>{};
  for (final t in allTasks) {
    for (final p in t.prerequisites) {
      if (!p.isMandatory) continue;
      downstream[p.taskSlug] = (downstream[p.taskSlug] ?? 0) + 1;
    }
  }

  // Stable daily seed — same jitter all day, different across days
  final dateSeed = today.year * 10000 + today.month * 100 + today.day;

  final result = <String, PriorityScored>{};
  for (final t in candidates) {
    var score = 0.0;

    // 1. Base state score
    score += isUnlocked[t.slug] == true ? 100.0 : 50.0;

    // 2. Close-to-done boost — if practice has started, finish it
    final required = t.repetitionsRequired;
    final count = practiceCounts[t.slug] ?? 0;
    if (required > 1 && count > 0 && count < required) {
      score += 30.0 * (count / required);
    }

    // 3. Gateway boost — each downstream mandatory dependency = +5
    final unlocks = downstream[t.slug] ?? 0;
    score += 5.0 * unlocks;

    // 4. Sweet spot — child's age is inside the task's age band
    if (childAge >= t.minAge && childAge <= t.maxAge) {
      score += 15.0;
    }

    // 5. Above-age — unlocked via prereqs, celebrate
    if (isAboveAge[t.slug] == true) {
      score += 10.0;
    }

    // 6. Stable daily jitter — breaks ties freshly each day
    final slugHash = t.slug.hashCode;
    final combined = slugHash ^ dateSeed;
    final jitter = (combined.abs() % 1000) / 100.0; // 0.0–10.0
    score += jitter;

    result[t.slug] = PriorityScored(
      slug: t.slug,
      score: score,
      unlocksDownstream: unlocks,
    );
  }

  return result;
}

/// Sort [tasks] by descending priority score, then gently redistribute so no
/// more than [maxRun] consecutive tasks share the same category (when enough
/// variety is available).
List<Task> orderByPriorityWithBalance(
  List<Task> tasks,
  Map<String, PriorityScored> scores, {
  int maxRun = 2,
}) {
  final sorted = List<Task>.from(tasks)
    ..sort((a, b) {
      final sa = scores[a.slug]?.score ?? 0;
      final sb = scores[b.slug]?.score ?? 0;
      return sb.compareTo(sa);
    });

  String catOf(Task t) =>
      t.tags.isEmpty ? 'other' : t.tags.first.category;

  final result = <Task>[];
  final pending = List<Task>.from(sorted);
  String? lastCat;
  int runCount = 0;

  while (pending.isNotEmpty) {
    Task pick;
    int pickIdx = 0;

    if (runCount >= maxRun && lastCat != null) {
      // We've had [maxRun] in a row from lastCat — try to pick something else
      var found = -1;
      for (int i = 0; i < pending.length; i++) {
        if (catOf(pending[i]) != lastCat) {
          found = i;
          break;
        }
      }
      if (found >= 0) {
        pick = pending[found];
        pickIdx = found;
      } else {
        // No alternative left, just take the top
        pick = pending.first;
        pickIdx = 0;
      }
    } else {
      pick = pending.first;
      pickIdx = 0;
    }

    final cat = catOf(pick);
    if (cat == lastCat) {
      runCount++;
    } else {
      lastCat = cat;
      runCount = 1;
    }

    result.add(pick);
    pending.removeAt(pickIdx);
  }

  return result;
}

/// Dynamic limit for visible Next Up count: scales with total unlocked tasks.
/// Minimum 5, maximum 10.
int dynamicNextUpLimit(int totalAvailable) {
  final scaled = totalAvailable ~/ 4;
  if (scaled < 5) return 5;
  if (scaled > 10) return 10;
  return scaled;
}
