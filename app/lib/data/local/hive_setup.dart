import 'package:hive_flutter/hive_flutter.dart';

import 'child_profile.dart';
import 'custom_reward.dart';
import 'custom_task.dart';
import 'reward_usage.dart';
import 'task_progress.dart';

/// Single entry point for local storage. All child PII lives in these boxes —
/// nothing here is ever sent to the server.
class HiveSetup {
  static const _children = "children";
  static const _progress = "task_progress";
  static const _rewardUsage = "reward_usage";
  static const _session = "session";
  static const _customRewards = "custom_rewards";
  static const _customTasks = "custom_tasks";

  static Future<void> init() async {
    await Hive.initFlutter();
    Hive.registerAdapter(ChildProfileAdapter());
    Hive.registerAdapter(TaskProgressAdapter());
    Hive.registerAdapter(RewardUsageAdapter());
    Hive.registerAdapter(CustomRewardAdapter());
    Hive.registerAdapter(CustomTaskAdapter());
    await Future.wait([
      Hive.openBox<ChildProfile>(_children),
      Hive.openBox<TaskProgress>(_progress),
      Hive.openBox<RewardUsage>(_rewardUsage),
      Hive.openBox(_session),
      Hive.openBox<CustomReward>(_customRewards),
      Hive.openBox<CustomTask>(_customTasks),
    ]);
  }

  static Box<ChildProfile> get childBox => Hive.box<ChildProfile>(_children);
  static Box<TaskProgress> get progressBox => Hive.box<TaskProgress>(_progress);
  static Box<RewardUsage> get rewardUsageBox => Hive.box<RewardUsage>(_rewardUsage);
  static Box get sessionBox => Hive.box(_session);
  static Box<CustomReward> get customRewardBox => Hive.box<CustomReward>(_customRewards);
  static Box<CustomTask> get customTaskBox => Hive.box<CustomTask>(_customTasks);
}
