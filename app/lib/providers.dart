import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'data/api/task_repository.dart';
import 'data/local/active_child.dart';
import 'data/local/child_profile.dart';
import 'data/local/hive_setup.dart';
import 'domain/models.dart';

final progressVersionProvider = StateProvider<int>((ref) => 0);

String _sexParam(Sex sex) => switch (sex) {
      Sex.boy => "male",
      Sex.girl => "female",
      Sex.other => "any",
    };

/// All tasks for the active child's environment + sex, filtered by profile kind
/// and religion opt-in.
///
/// Age slice: adult profiles → minAge >= 17; child profiles → minAge <= 16.
///
/// Religion slice: tasks with a non-empty `religion` field are hidden from
/// profiles that didn't opt in, or that picked a different religion. Tasks
/// with empty religion are universal.
final catalogProvider = FutureProvider<List<Task>>((ref) async {
  final activeId = ref.watch(activeChildIdProvider);
  final profile = HiveSetup.childBox.get(activeId)!;
  final all = await ref.read(taskRepositoryProvider).fetchAll(
        environment: profile.environment.name,
        sex: _sexParam(profile.sex),
      );

  final optedIn = profile.religionInterest;
  final pickedReligion = profile.religion ?? "";

  bool religionAllows(Task t) {
    if (t.religion.isEmpty) return true; // universal
    if (!optedIn) return false;
    return t.religion == pickedReligion;
  }

  final ageSliced = profile.isAdult
      ? all.where((t) => t.minAge >= 17)
      : all.where((t) => t.minAge <= 16);
  return ageSliced.where(religionAllows).toList(growable: false);
});
