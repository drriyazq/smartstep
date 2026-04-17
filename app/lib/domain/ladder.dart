import '../data/local/task_progress.dart';
import 'models.dart';

enum LadderState {
  /// All mandatory prerequisites are satisfied or bypassed.
  unlocked,

  /// At least one mandatory prereq is `skippedKnown` — surface with a warning.
  lockedWithWarning,

  /// At least one mandatory prereq is `locked`, not yet completed, or `skippedUnsuitable`.
  locked,

  /// Child has completed the task.
  completed,

  /// Child marked this as already known, or bypassed via baseline.
  satisfied,
}

/// Pure function. Given the full catalog and a per-child progress map, returns
/// the LadderState for `task`.
LadderState computeLadderState({
  required Task task,
  required Map<String, TaskProgress> progressBySlug,
}) {
  final self = progressBySlug[task.slug];
  if (self != null) {
    switch (self.status) {
      case ProgressStatus.completed:
        return LadderState.completed;
      case ProgressStatus.bypassed:
      case ProgressStatus.skippedKnown:
        return LadderState.satisfied;
      case ProgressStatus.skippedUnsuitable:
        return LadderState.locked;
      case ProgressStatus.locked:
      case ProgressStatus.unlocked:
        break; // fall through to prereq evaluation
    }
  }

  var sawWarning = false;
  for (final p in task.prerequisites) {
    if (!p.isMandatory) continue;
    final prog = progressBySlug[p.taskSlug];
    if (prog == null) return LadderState.locked;
    if (prog.satisfies) continue;
    if (prog.softSkipped) {
      sawWarning = true;
      continue;
    }
    return LadderState.locked;
  }
  return sawWarning ? LadderState.lockedWithWarning : LadderState.unlocked;
}
