import 'package:hive/hive.dart';

class RewardUsage {
  RewardUsage({
    required this.childId,
    required this.rewardCategory,
    required this.rewardTitle,
    required this.usedAt,
  });

  final String childId;
  final String rewardCategory;
  final String rewardTitle;
  final DateTime usedAt;
}

class RewardUsageAdapter extends TypeAdapter<RewardUsage> {
  @override
  final int typeId = 3;

  @override
  RewardUsage read(BinaryReader r) => RewardUsage(
        childId: r.readString(),
        rewardCategory: r.readString(),
        rewardTitle: r.readString(),
        usedAt: DateTime.fromMillisecondsSinceEpoch(r.readInt()),
      );

  @override
  void write(BinaryWriter w, RewardUsage u) {
    w.writeString(u.childId);
    w.writeString(u.rewardCategory);
    w.writeString(u.rewardTitle);
    w.writeInt(u.usedAt.millisecondsSinceEpoch);
  }
}
