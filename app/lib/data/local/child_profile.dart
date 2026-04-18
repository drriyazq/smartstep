import 'package:hive/hive.dart';

/// On-device only. The backend never sees this.
///
/// Despite the name "ChildProfile", this type also represents adult users
/// (via [ProfileKind.adult]). The class name is preserved for backward
/// compatibility with existing Hive boxes. Prefer calling instances
/// "profile" in new code; treat `ChildProfile` as the underlying schema.
class ChildProfile {
  ChildProfile({
    required this.id,
    required this.name,
    required this.dob,
    required this.sex,
    required this.environment,
    this.kind = ProfileKind.child,
  });

  final String id;
  final String name;
  final DateTime dob;
  final Sex sex;
  final Environment environment;
  final ProfileKind kind;

  bool get isAdult => kind == ProfileKind.adult;

  int ageOn(DateTime ref) {
    var years = ref.year - dob.year;
    if (ref.month < dob.month ||
        (ref.month == dob.month && ref.day < dob.day)) {
      years -= 1;
    }
    return years;
  }

  String ageBand(DateTime ref) {
    final age = ageOn(ref);
    // Child bands (used by anonymous telemetry)
    if (kind == ProfileKind.child) {
      if (age <= 8) return "7_8";
      if (age <= 10) return "9_10";
      return "11";
    }
    // Adult bands
    if (age < 26) return "18_25";
    if (age < 36) return "26_35";
    if (age < 46) return "36_45";
    if (age < 56) return "46_55";
    return "56_plus";
  }
}

enum Sex { boy, girl, other }

enum Environment { urban, suburban, rural }

enum ProfileKind { child, adult }

class ChildProfileAdapter extends TypeAdapter<ChildProfile> {
  @override
  final int typeId = 1;

  @override
  ChildProfile read(BinaryReader r) {
    final id = r.readString();
    final name = r.readString();
    final dob = DateTime.fromMillisecondsSinceEpoch(r.readInt());
    final sex = Sex.values[r.readByte()];
    final environment = Environment.values[r.readByte()];
    // Backward-compat: older adapters didn't write [kind]. If the record is
    // short, assume child (the only possibility before this field existed).
    var kind = ProfileKind.child;
    if (r.availableBytes > 0) {
      final raw = r.readByte();
      if (raw >= 0 && raw < ProfileKind.values.length) {
        kind = ProfileKind.values[raw];
      }
    }
    return ChildProfile(
      id: id,
      name: name,
      dob: dob,
      sex: sex,
      environment: environment,
      kind: kind,
    );
  }

  @override
  void write(BinaryWriter w, ChildProfile p) {
    w.writeString(p.id);
    w.writeString(p.name);
    w.writeInt(p.dob.millisecondsSinceEpoch);
    w.writeByte(p.sex.index);
    w.writeByte(p.environment.index);
    w.writeByte(p.kind.index);
  }
}
