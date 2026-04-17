import 'package:hive/hive.dart';

/// On-device only. The backend never sees this.
class ChildProfile {
  ChildProfile({
    required this.id,
    required this.name,
    required this.dob,
    required this.sex,
    required this.environment,
  });

  final String id;
  final String name;
  final DateTime dob;
  final Sex sex;
  final Environment environment;

  int ageOn(DateTime ref) {
    var years = ref.year - dob.year;
    if (ref.month < dob.month || (ref.month == dob.month && ref.day < dob.day)) {
      years -= 1;
    }
    return years;
  }

  String ageBand(DateTime ref) {
    final age = ageOn(ref);
    if (age <= 8) return "7_8";
    if (age <= 10) return "9_10";
    return "11";
  }
}

enum Sex { boy, girl, other }

enum Environment { urban, suburban, rural }

class ChildProfileAdapter extends TypeAdapter<ChildProfile> {
  @override
  final int typeId = 1;

  @override
  ChildProfile read(BinaryReader r) => ChildProfile(
        id: r.readString(),
        name: r.readString(),
        dob: DateTime.fromMillisecondsSinceEpoch(r.readInt()),
        sex: Sex.values[r.readByte()],
        environment: Environment.values[r.readByte()],
      );

  @override
  void write(BinaryWriter w, ChildProfile p) {
    w.writeString(p.id);
    w.writeString(p.name);
    w.writeInt(p.dob.millisecondsSinceEpoch);
    w.writeByte(p.sex.index);
    w.writeByte(p.environment.index);
  }
}
