import 'package:hive/hive.dart';

class CustomTask {
  CustomTask({
    required this.id,
    required this.childId,
    required this.title,
    this.howToMd = '',
    this.parentNoteMd = '',
  });

  /// Unique key: millisecondsSinceEpoch as string, used as Hive box key too.
  final String id;
  final String childId;
  final String title;
  final String howToMd;
  final String parentNoteMd;

  /// Slug used in progressBox: "custom::<id>"
  String get progressSlug => 'custom::$id';
}

class CustomTaskAdapter extends TypeAdapter<CustomTask> {
  @override
  final int typeId = 5;

  @override
  CustomTask read(BinaryReader r) => CustomTask(
        id: r.readString(),
        childId: r.readString(),
        title: r.readString(),
        howToMd: r.readString(),
        parentNoteMd: r.readString(),
      );

  @override
  void write(BinaryWriter w, CustomTask t) {
    w.writeString(t.id);
    w.writeString(t.childId);
    w.writeString(t.title);
    w.writeString(t.howToMd);
    w.writeString(t.parentNoteMd);
  }
}
