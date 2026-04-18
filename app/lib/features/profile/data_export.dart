import 'dart:convert';

import 'package:share_plus/share_plus.dart';

import '../../data/local/child_profile.dart';
import '../../data/local/custom_reward.dart';
import '../../data/local/custom_task.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';

/// Builds a JSON export of every piece of data SmartStep holds about a given
/// child on this device, and shares it via the system share sheet.
///
/// Satisfies the "right to access" under the DPDP Act 2023 and the broader
/// Play Store expectation that a user can see what has been collected.
class DataExport {
  static Future<void> exportForChild(String childId) async {
    final child = HiveSetup.childBox.get(childId);
    if (child == null) return;

    final progress = HiveSetup.progressBox.values
        .where((p) => p.childId == childId)
        .map(_progressToJson)
        .toList();

    final customTasks = HiveSetup.customTaskBox.values
        .where((t) => t.childId == childId)
        .map(_customTaskToJson)
        .toList();

    final customRewards = HiveSetup.customRewardBox.values
        .where((r) => r.childId == childId)
        .map(_customRewardToJson)
        .toList();

    // Session-level keys relevant to this child (counts, rewards, filters).
    final sessionEntries = <String, Object?>{};
    for (final key in HiveSetup.sessionBox.keys) {
      if (key is! String) continue;
      if (key.contains(childId)) {
        sessionEntries[key] = HiveSetup.sessionBox.get(key);
      }
    }

    final payload = <String, Object?>{
      'exported_at': DateTime.now().toIso8601String(),
      'child': _childToJson(child),
      'skill_progress': progress,
      'custom_tasks': customTasks,
      'custom_rewards': customRewards,
      'device_only_session': sessionEntries,
      '_note':
          'All of this data is stored only on this device. SmartStep servers hold only anonymous task-completion counts (age band + environment), which cannot be linked back to this child.',
    };

    final json = const JsonEncoder.withIndent('  ').convert(payload);
    final safeName = child.name
        .replaceAll(RegExp(r'[^A-Za-z0-9_-]+'), '_')
        .toLowerCase();
    final filename =
        'smartstep_${safeName}_${DateTime.now().millisecondsSinceEpoch}.json';

    await Share.shareXFiles(
      [XFile.fromData(utf8.encode(json), name: filename, mimeType: 'application/json')],
      text: "SmartStep data export for ${child.name}",
    );
  }

  static Map<String, Object?> _childToJson(ChildProfile c) => {
        'id': c.id,
        'name': c.name,
        'dob': c.dob.toIso8601String(),
        'sex': c.sex.name,
        'environment': c.environment.name,
      };

  static Map<String, Object?> _progressToJson(TaskProgress p) => {
        'task_slug': p.taskSlug,
        'status': p.status.name,
        'completed_at': p.completedAt?.toIso8601String(),
      };

  static Map<String, Object?> _customTaskToJson(CustomTask t) => {
        'id': t.id,
        'title': t.title,
        'how_to': t.howToMd,
        'parent_note': t.parentNoteMd,
      };

  static Map<String, Object?> _customRewardToJson(CustomReward r) => {
        'id': r.id,
        'title': r.title,
        'notes': r.notes,
        'is_free': r.isFree,
      };
}
