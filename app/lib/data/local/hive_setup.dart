import 'dart:convert';
import 'dart:math';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'child_profile.dart';
import 'custom_reward.dart';
import 'custom_task.dart';
import 'reward_usage.dart';
import 'task_progress.dart';

/// Single entry point for local storage.
///
/// Sensitive boxes (child PII, auth tokens, per-child progress) are encrypted
/// with AES-256 using a device-generated key held in platform secure storage
/// (Android Keystore / iOS Keychain). The key itself never leaves secure
/// storage and is not readable by other apps or by backups.
///
/// Non-sensitive boxes (reward usage, custom tasks/rewards authored by the
/// parent) remain unencrypted — they contain no PII.
class HiveSetup {
  static const _children = "children";
  static const _progress = "task_progress";
  static const _rewardUsage = "reward_usage";
  static const _session = "session";
  static const _customRewards = "custom_rewards";
  static const _customTasks = "custom_tasks";

  static const _encKeyName = 'smartstep_hive_key_v1';

  static Future<void> init() async {
    await Hive.initFlutter();
    Hive.registerAdapter(ChildProfileAdapter());
    Hive.registerAdapter(TaskProgressAdapter());
    Hive.registerAdapter(RewardUsageAdapter());
    Hive.registerAdapter(CustomRewardAdapter());
    Hive.registerAdapter(CustomTaskAdapter());

    final encKey = await _readOrCreateEncryptionKey();
    final cipher = HiveAesCipher(encKey);

    await Future.wait([
      // Encrypted: contain PII or auth tokens
      Hive.openBox<ChildProfile>(_children, encryptionCipher: cipher),
      Hive.openBox<TaskProgress>(_progress, encryptionCipher: cipher),
      Hive.openBox(_session, encryptionCipher: cipher),
      Hive.openBox<CustomTask>(_customTasks, encryptionCipher: cipher),
      // Not encrypted: no PII
      Hive.openBox<RewardUsage>(_rewardUsage),
      Hive.openBox<CustomReward>(_customRewards),
    ]);
  }

  /// Generates or retrieves a 256-bit AES key held in the platform's
  /// secure keystore. The key persists across launches and is bound to the
  /// device — an attacker cannot read encrypted Hive data without the key.
  static Future<List<int>> _readOrCreateEncryptionKey() async {
    const storage = FlutterSecureStorage(
      aOptions: AndroidOptions(encryptedSharedPreferences: true),
    );
    final existing = await storage.read(key: _encKeyName);
    if (existing != null) {
      return base64Decode(existing);
    }
    final key = List<int>.generate(32, (_) => Random.secure().nextInt(256));
    await storage.write(key: _encKeyName, value: base64Encode(key));
    return key;
  }

  static Box<ChildProfile> get childBox =>
      Hive.box<ChildProfile>(_children);
  static Box<TaskProgress> get progressBox =>
      Hive.box<TaskProgress>(_progress);
  static Box<RewardUsage> get rewardUsageBox =>
      Hive.box<RewardUsage>(_rewardUsage);
  static Box get sessionBox => Hive.box(_session);
  static Box<CustomReward> get customRewardBox =>
      Hive.box<CustomReward>(_customRewards);
  static Box<CustomTask> get customTaskBox =>
      Hive.box<CustomTask>(_customTasks);
}
