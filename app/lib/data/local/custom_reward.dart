import 'package:hive/hive.dart';

class CustomReward {
  CustomReward({
    required this.id,
    required this.childId,
    required this.title,
    this.notes = '',
    this.isFree = true,
  });

  /// Unique key: millisecondsSinceEpoch as string, used as Hive box key too.
  final String id;
  final String childId;
  final String title;
  final String notes;
  final bool isFree;

  static const String category = 'My Rewards';
}

class CustomRewardAdapter extends TypeAdapter<CustomReward> {
  @override
  final int typeId = 4;

  @override
  CustomReward read(BinaryReader r) => CustomReward(
        id: r.readString(),
        childId: r.readString(),
        title: r.readString(),
        notes: r.readString(),
        isFree: r.readBool(),
      );

  @override
  void write(BinaryWriter w, CustomReward r) {
    w.writeString(r.id);
    w.writeString(r.childId);
    w.writeString(r.title);
    w.writeString(r.notes);
    w.writeBool(r.isFree);
  }
}
