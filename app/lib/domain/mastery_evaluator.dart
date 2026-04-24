import '../data/local/hive_setup.dart';
import '../data/local/task_progress.dart';
import 'masteries.dart';

/// Returns the list of masteries that `childId` has earned right now,
/// evaluated against the passed progress map.
///
/// A mastery is "earned" when every one of its `requiredTaskSlugs` has a
/// TaskProgress whose `satisfies == true` (completed or bypassed). Tasks
/// not yet in the progress map are treated as not-satisfied.
List<Mastery> earnedMasteries({
  required String childId,
  required bool isAdult,
  required Map<String, TaskProgress> progressBySlug,
}) {
  final out = <Mastery>[];
  for (final m in kMasteries) {
    if (m.isAdult != isAdult) continue;
    final allSatisfied = m.requiredTaskSlugs.every((slug) {
      final p = progressBySlug[slug];
      return p != null && p.satisfies;
    });
    if (allSatisfied) out.add(m);
  }
  return out;
}

/// Returns how many of this mastery's prerequisites are currently satisfied
/// for the given child. Used for the Achievements tab progress indicator.
int masteryProgressCount(
  Mastery m,
  Map<String, TaskProgress> progressBySlug,
) {
  var done = 0;
  for (final slug in m.requiredTaskSlugs) {
    final p = progressBySlug[slug];
    if (p != null && p.satisfies) done++;
  }
  return done;
}

// ─────────────────────────────────────────────── Earned-mastery store ──
//
// Earned masteries are stored in sessionBox under a namespaced key. Value is
// the ISO-8601 timestamp of when the mastery was first earned (so future
// certificates can show the earn date).

String _earnedKey(String childId, String masteryId) =>
    'mastery::$childId::$masteryId';

DateTime? earnedAt(String childId, Mastery m) {
  final iso = HiveSetup.sessionBox.get(_earnedKey(childId, m.id));
  if (iso is String && iso.isNotEmpty) {
    return DateTime.tryParse(iso);
  }
  return null;
}

bool isAlreadyEarned(String childId, Mastery m) =>
    earnedAt(childId, m) != null;

Future<void> markEarned(String childId, Mastery m, {DateTime? at}) async {
  final ts = (at ?? DateTime.now()).toIso8601String();
  await HiveSetup.sessionBox.put(_earnedKey(childId, m.id), ts);
}

/// Evaluates which masteries are newly earned this moment — i.e. currently
/// satisfied by progress AND not previously marked as earned. Used after a
/// task completion to trigger the celebration certificate popup.
///
/// Returns the newly-earned masteries and marks them as earned in storage.
Future<List<Mastery>> claimNewlyEarnedMasteries({
  required String childId,
  required bool isAdult,
  required Map<String, TaskProgress> progressBySlug,
}) async {
  final currently = earnedMasteries(
    childId: childId,
    isAdult: isAdult,
    progressBySlug: progressBySlug,
  );
  final newly = <Mastery>[];
  for (final m in currently) {
    if (!isAlreadyEarned(childId, m)) {
      await markEarned(childId, m);
      newly.add(m);
    }
  }
  return newly;
}
