import 'package:hive/hive.dart';

enum ProgressStatus {
  locked,
  unlocked,
  completed,
  skippedKnown, // "my kid already knows this — bypass the prereq chain"
  skippedUnsuitable, // "not appropriate for my child — don't surface again"
  bypassed, // auto-granted by baseline assessment
}

class TaskProgress {
  TaskProgress({
    required this.taskSlug,
    required this.childId,
    required this.status,
    this.completedAt,
  });

  final String taskSlug;
  final String childId;
  ProgressStatus status;
  DateTime? completedAt;

  /// Treats these statuses as "satisfying" a downstream prereq.
  bool get satisfies =>
      status == ProgressStatus.completed || status == ProgressStatus.bypassed;

  /// Treats these as "skipped with warning" for downstream prereq checks.
  bool get softSkipped => status == ProgressStatus.skippedKnown;

  static String key(String childId, String taskSlug) => "$childId::$taskSlug";
}

class TaskProgressAdapter extends TypeAdapter<TaskProgress> {
  @override
  final int typeId = 2;

  @override
  TaskProgress read(BinaryReader r) {
    final slug = r.readString();
    final childId = r.readString();
    final status = ProgressStatus.values[r.readByte()];
    final hasCompleted = r.readBool();
    final completedAt = hasCompleted
        ? DateTime.fromMillisecondsSinceEpoch(r.readInt())
        : null;
    return TaskProgress(
      taskSlug: slug,
      childId: childId,
      status: status,
      completedAt: completedAt,
    );
  }

  @override
  void write(BinaryWriter w, TaskProgress p) {
    w.writeString(p.taskSlug);
    w.writeString(p.childId);
    w.writeByte(p.status.index);
    w.writeBool(p.completedAt != null);
    if (p.completedAt != null) w.writeInt(p.completedAt!.millisecondsSinceEpoch);
  }
}
