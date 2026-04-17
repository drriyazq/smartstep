import 'package:flutter_test/flutter_test.dart';
import 'package:smartstep_app/data/local/task_progress.dart';
import 'package:smartstep_app/domain/ladder.dart';
import 'package:smartstep_app/domain/models.dart';

Task _task(String slug, {List<Prerequisite> prereqs = const []}) => Task(
      id: slug.hashCode,
      slug: slug,
      title: slug,
      howToMd: "_",
      safetyMd: "",
      minAge: 7,
      maxAge: 11,
      environments: const ["urban"],
      tags: const [],
      prerequisites: prereqs,
    );

TaskProgress _prog(String slug, ProgressStatus status) => TaskProgress(
      taskSlug: slug,
      childId: "child-1",
      status: status,
    );

void main() {
  group("computeLadderState", () {
    test("no prerequisites => unlocked", () {
      final t = _task("a");
      expect(
        computeLadderState(task: t, progressBySlug: const {}),
        LadderState.unlocked,
      );
    });

    test("missing mandatory prereq => locked", () {
      final t = _task(
        "b",
        prereqs: const [Prerequisite(taskSlug: "a", isMandatory: true)],
      );
      expect(
        computeLadderState(task: t, progressBySlug: const {}),
        LadderState.locked,
      );
    });

    test("completed prereq => unlocked", () {
      final t = _task(
        "b",
        prereqs: const [Prerequisite(taskSlug: "a", isMandatory: true)],
      );
      expect(
        computeLadderState(
          task: t,
          progressBySlug: {"a": _prog("a", ProgressStatus.completed)},
        ),
        LadderState.unlocked,
      );
    });

    test("bypassed prereq satisfies downstream => unlocked", () {
      final t = _task(
        "b",
        prereqs: const [Prerequisite(taskSlug: "a", isMandatory: true)],
      );
      expect(
        computeLadderState(
          task: t,
          progressBySlug: {"a": _prog("a", ProgressStatus.bypassed)},
        ),
        LadderState.unlocked,
      );
    });

    test("skippedKnown on prereq => lockedWithWarning", () {
      final t = _task(
        "b",
        prereqs: const [Prerequisite(taskSlug: "a", isMandatory: true)],
      );
      expect(
        computeLadderState(
          task: t,
          progressBySlug: {"a": _prog("a", ProgressStatus.skippedKnown)},
        ),
        LadderState.lockedWithWarning,
      );
    });

    test("skippedUnsuitable on prereq => locked", () {
      final t = _task(
        "b",
        prereqs: const [Prerequisite(taskSlug: "a", isMandatory: true)],
      );
      expect(
        computeLadderState(
          task: t,
          progressBySlug: {"a": _prog("a", ProgressStatus.skippedUnsuitable)},
        ),
        LadderState.locked,
      );
    });

    test("soft (non-mandatory) prereq missing => still unlocked", () {
      final t = _task(
        "b",
        prereqs: const [Prerequisite(taskSlug: "a", isMandatory: false)],
      );
      expect(
        computeLadderState(task: t, progressBySlug: const {}),
        LadderState.unlocked,
      );
    });

    test("task itself completed => completed", () {
      final t = _task("a");
      expect(
        computeLadderState(
          task: t,
          progressBySlug: {"a": _prog("a", ProgressStatus.completed)},
        ),
        LadderState.completed,
      );
    });

    test("mix: one completed + one skippedKnown => lockedWithWarning", () {
      final t = _task(
        "c",
        prereqs: const [
          Prerequisite(taskSlug: "a", isMandatory: true),
          Prerequisite(taskSlug: "b", isMandatory: true),
        ],
      );
      expect(
        computeLadderState(
          task: t,
          progressBySlug: {
            "a": _prog("a", ProgressStatus.completed),
            "b": _prog("b", ProgressStatus.skippedKnown),
          },
        ),
        LadderState.lockedWithWarning,
      );
    });
  });
}
