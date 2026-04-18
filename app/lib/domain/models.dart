/// Domain DTOs mirroring the backend JSON shape. Kept deliberately simple —
/// no freezed/json_serializable — parsing is manual in `task_repository`.

class Tag {
  const Tag({required this.id, required this.name, required this.category});
  final int id;
  final String name;
  final String category;

  factory Tag.fromJson(Map<String, dynamic> j) => Tag(
        id: j["id"] as int,
        name: j["name"] as String,
        category: j["category"] as String,
      );
}

class Prerequisite {
  const Prerequisite({required this.taskSlug, required this.isMandatory});
  final String taskSlug;
  final bool isMandatory;

  factory Prerequisite.fromJson(Map<String, dynamic> j) => Prerequisite(
        taskSlug: j["task_slug"] as String,
        isMandatory: j["is_mandatory"] as bool,
      );
}

class Task {
  const Task({
    required this.id,
    required this.slug,
    required this.title,
    required this.howToMd,
    required this.safetyMd,
    required this.parentNoteMd,
    required this.minAge,
    required this.maxAge,
    required this.repetitionsRequired,
    required this.environments,
    required this.tags,
    required this.prerequisites,
  });

  final int id;
  final String slug;
  final String title;
  final String howToMd;
  final String safetyMd;
  final String parentNoteMd;
  final int minAge;
  final int maxAge;
  final int repetitionsRequired;
  final List<String> environments;
  final List<Tag> tags;
  final List<Prerequisite> prerequisites;

  factory Task.fromJson(Map<String, dynamic> j) => Task(
        id: j["id"] as int,
        slug: j["slug"] as String,
        title: j["title"] as String,
        howToMd: j["how_to_md"] as String,
        safetyMd: (j["safety_md"] as String?) ?? "",
        parentNoteMd: (j["parent_note_md"] as String?) ?? "",
        minAge: j["min_age"] as int,
        maxAge: j["max_age"] as int,
        repetitionsRequired: (j["repetitions_required"] as int?) ?? 3,
        environments:
            (j["environments"] as List? ?? const []).cast<String>(),
        tags: (j["tags"] as List? ?? const [])
            .cast<Map<String, dynamic>>()
            .map(Tag.fromJson)
            .toList(),
        prerequisites: (j["prerequisites"] as List? ?? const [])
            .cast<Map<String, dynamic>>()
            .map(Prerequisite.fromJson)
            .toList(),
      );
}

class Reward {
  const Reward({
    required this.id,
    required this.title,
    required this.category,
    required this.minAge,
    required this.maxAge,
    required this.isFree,
    required this.notes,
  });

  final int id;
  final String title;
  final String category;
  final int minAge;
  final int maxAge;
  final bool isFree;
  final String notes;

  factory Reward.fromJson(Map<String, dynamic> j) => Reward(
        id: j["id"] as int,
        title: j["title"] as String,
        category: j["category"] as String,
        minAge: j["min_age"] as int,
        maxAge: j["max_age"] as int,
        isFree: j["is_free"] as bool,
        notes: (j["notes"] as String?) ?? "",
      );
}
