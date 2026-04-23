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

/// All tasks for the active child's environment + sex, filtered by profile kind.
/// Adult profiles → minAge >= 17; child profiles → minAge <= 16.
final catalogProvider = FutureProvider<List<Task>>((ref) async {
  final activeId = ref.watch(activeChildIdProvider);
  final profile = HiveSetup.childBox.get(activeId)!;
  final all = await ref.read(taskRepositoryProvider).fetchAll(
        environment: profile.environment.name,
        sex: _sexParam(profile.sex),
      );
  if (profile.isAdult) {
    return all.where((t) => t.minAge >= 17).toList(growable: false);
  }
  return all.where((t) => t.minAge <= 16).toList(growable: false);
});
