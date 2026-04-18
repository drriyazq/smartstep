import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'hive_setup.dart';

/// Tracks which child is currently active on this device.
/// Persisted to sessionBox so it survives app restarts.
final activeChildIdProvider = StateProvider<String>((ref) {
  final stored = HiveSetup.sessionBox.get('active_child_id') as String?;
  if (stored != null && HiveSetup.childBox.containsKey(stored)) return stored;
  return HiveSetup.childBox.keys.cast<String>().first;
});

/// Convenience: switch the active child and persist the choice.
void setActiveChild(StateController<String> notifier, String childId) {
  notifier.state = childId;
  HiveSetup.sessionBox.put('active_child_id', childId);
}
