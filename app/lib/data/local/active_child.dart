import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../sync/remote_sync.dart';
import 'hive_setup.dart';

/// Tracks which child is currently active on this device.
/// Persisted to sessionBox so it survives app restarts.
final activeChildIdProvider = StateProvider<String>((ref) {
  final stored = HiveSetup.sessionBox.get('active_child_id') as String?;
  if (stored != null && HiveSetup.childBox.containsKey(stored)) return stored;
  return HiveSetup.childBox.keys.cast<String>().first;
});

/// Convenience: switch the active child and persist the choice both locally
/// and (where possible) on the server. The remote write is best-effort —
/// `is_active` is a UI hint, not load-bearing data, so a network failure
/// shouldn't block the user from switching profiles on the device.
void setActiveChild(
  StateController<String> notifier,
  String childId, {
  WidgetRef? ref,
}) {
  notifier.state = childId;
  HiveSetup.sessionBox.put('active_child_id', childId);
  if (ref != null) {
    // Fire-and-forget: server flip is async, UI doesn't need to wait.
    ref.read(remoteSyncProvider).activateProfile(childId).catchError((_) {});
  }
}
