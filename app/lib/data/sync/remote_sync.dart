// Server-of-truth orchestrator. All user data (profiles, progress, custom
// tasks/rewards, masteries, UI session state) lives on the server now;
// the Hive boxes are kept around as a transparent in-memory cache so the
// existing screen code can stay synchronous-feeling for reads.
//
// Contract:
// - Reads from screens still hit the Hive boxes directly (fast, sync).
// - Writes from screens must funnel through `RemoteSync.persist*`, which
//   sends the change to the server first and only updates Hive on success.
//   The app is "online-required" for writes — see [SyncException].
// - On every cold start, `RemoteSync.bootstrap()` wipes the local cache
//   and re-hydrates from `GET /api/v1/me/state/`, so a fresh install on a
//   new device immediately sees the user's existing data.
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/me_api.dart';
import '../local/child_profile.dart';
import '../local/custom_reward.dart';
import '../local/custom_task.dart';
import '../local/hive_setup.dart';
import '../local/reward_usage.dart';
import '../local/task_progress.dart';

class SyncException implements Exception {
  SyncException(this.userMessage, {this.cause});
  final String userMessage;
  final Object? cause;
  @override
  String toString() => 'SyncException: $userMessage';
}

/// Maps a profile's local Hive key (millisecondsSinceEpoch string the
/// Flutter app generated when the profile was first authored) to the
/// server-assigned numeric `Profile.id`. Used by every write that
/// references a profile FK on the server.
class _ProfileIdMap {
  final Map<String, int> _byClientId = {};

  int? serverIdFor(String clientId) => _byClientId[clientId];
  void set(String clientId, int serverId) => _byClientId[clientId] = serverId;
  void clear() => _byClientId.clear();
}

class RemoteSync {
  RemoteSync(this._api);
  final MeApi _api;
  final _ProfileIdMap _profileIds = _ProfileIdMap();

  /// Server `Profile.id` for a given Hive client_id, or null if we haven't
  /// seen it yet (caller must persistProfile first).
  int? serverProfileId(String clientId) => _profileIds.serverIdFor(clientId);

  // ── Bootstrap ────────────────────────────────────────────────────────────

  /// Pulls /me/state/ and rebuilds every Hive box from scratch. Safe to
  /// call multiple times — it always clears first. Throws [SyncException]
  /// on network failure so the sign-in path can decide whether to retry.
  Future<void> bootstrap() async {
    final Map<String, dynamic> state;
    try {
      state = await _api.fetchState();
    } on DioException catch (e) {
      throw SyncException(
        'Could not reach SmartStep server. Connect to the internet and try again.',
        cause: e,
      );
    }

    _profileIds.clear();

    // ── Wipe local caches ────────────────────────────────────────────────
    await Future.wait([
      HiveSetup.childBox.clear(),
      HiveSetup.progressBox.clear(),
      HiveSetup.customTaskBox.clear(),
      HiveSetup.customRewardBox.clear(),
      HiveSetup.rewardUsageBox.clear(),
    ]);
    // sessionBox is partially wiped — auth tokens + device-only flags
    // (consent, encryption-key marker) must survive. We only clear the
    // keys that mirror server-side SessionItem rows + per-task derived
    // state (reward titles, practice counts).
    final session = HiveSetup.sessionBox;
    final keysToWipe = session.keys
        .cast<String>()
        .where(
          (k) =>
              k.startsWith('reward::') ||
              k.startsWith('count::') ||
              k.startsWith('mastery::') ||
              k.startsWith('filter::') ||
              k.startsWith('collapsed::') ||
              k == 'todays_pick' ||
              k == 'active_child_id',
        )
        .toList();
    if (keysToWipe.isNotEmpty) {
      await session.deleteAll(keysToWipe);
    }

    // ── Rehydrate profiles ───────────────────────────────────────────────
    final profiles = (state['profiles'] as List).cast<Map<String, dynamic>>();
    for (final p in profiles) {
      final profile = _profileFromJson(p);
      _profileIds.set(profile.id, p['id'] as int);
      await HiveSetup.childBox.put(profile.id, profile);
      if (p['is_active'] == true) {
        await session.put('active_child_id', profile.id);
      }
    }

    // ── Rehydrate progress ───────────────────────────────────────────────
    final progressRows = (state['progress'] as List).cast<Map<String, dynamic>>();
    for (final row in progressRows) {
      final clientId = row['profile_client_id'] as String;
      final tp = _progressFromJson(row, childClientId: clientId);
      await HiveSetup.progressBox.put(
        TaskProgress.key(clientId, tp.taskSlug),
        tp,
      );
      // Reward title chosen for this task — restore the per-task sessionBox key
      // the celebration sheet reads.
      final rewardTitle = row['reward_title'] as String? ?? '';
      if (rewardTitle.isNotEmpty) {
        await session.put('reward::$clientId::${tp.taskSlug}', rewardTitle);
      }
      // Practice count — restore for dashboard's "almost done" boost.
      final reps = row['repetitions_done'] as int? ?? 0;
      if (reps > 0) {
        await session.put('count::$clientId::${tp.taskSlug}', reps);
      }
    }

    // ── Rehydrate custom tasks ───────────────────────────────────────────
    final customTasks = (state['custom_tasks'] as List).cast<Map<String, dynamic>>();
    final profileClientIdByServerId = {
      for (final p in profiles) p['id'] as int: p['client_id'] as String,
    };
    for (final t in customTasks) {
      final childClientId = profileClientIdByServerId[t['profile'] as int];
      if (childClientId == null) continue;
      final ct = CustomTask(
        id: t['client_id'] as String,
        childId: childClientId,
        title: t['title'] as String,
        howToMd: t['how_to_md'] as String? ?? '',
        parentNoteMd: t['parent_note_md'] as String? ?? '',
      );
      await HiveSetup.customTaskBox.put(ct.id, ct);
    }

    // ── Rehydrate custom rewards ─────────────────────────────────────────
    final customRewards = (state['custom_rewards'] as List).cast<Map<String, dynamic>>();
    for (final r in customRewards) {
      final childClientId = profileClientIdByServerId[r['profile'] as int];
      if (childClientId == null) continue;
      final cr = CustomReward(
        id: r['client_id'] as String,
        childId: childClientId,
        title: r['title'] as String,
        notes: r['notes'] as String? ?? '',
        isFree: r['is_free'] as bool? ?? true,
      );
      await HiveSetup.customRewardBox.put(cr.id, cr);
    }

    // ── Rehydrate reward usage ───────────────────────────────────────────
    final usages = (state['reward_usages'] as List).cast<Map<String, dynamic>>();
    for (final u in usages) {
      final childClientId = profileClientIdByServerId[u['profile'] as int];
      if (childClientId == null) continue;
      final usage = RewardUsage(
        childId: childClientId,
        rewardCategory: u['reward_category'] as String,
        rewardTitle: u['reward_title'] as String,
        usedAt: DateTime.parse(u['used_at'] as String),
      );
      await HiveSetup.rewardUsageBox.add(usage);
    }

    // ── Rehydrate masteries ──────────────────────────────────────────────
    final masteries = (state['masteries'] as List).cast<Map<String, dynamic>>();
    for (final m in masteries) {
      final childClientId = profileClientIdByServerId[m['profile'] as int];
      if (childClientId == null) continue;
      await session.put(
        'mastery::$childClientId::${m['mastery_id']}',
        m['earned_at'],
      );
    }

    // ── Rehydrate session items (filter chips, todays_pick, collapsed…) ──
    final sessionItems = (state['session_items'] as List).cast<Map<String, dynamic>>();
    for (final s in sessionItems) {
      final childClientId = profileClientIdByServerId[s['profile'] as int];
      if (childClientId == null) continue;
      final localKey = s['key'] as String;
      // Local session keys are global (not prefixed by child id) for the
      // dashboard filter state etc. The server keys it per-profile so the
      // same account's adult vs child profiles can differ; we collapse to
      // the active profile on hydrate.
      await session.put(localKey, s['value']);
    }
  }

  // ── Profile persistence ──────────────────────────────────────────────────

  Future<ChildProfile> persistProfile(ChildProfile profile,
      {bool isActive = false}) async {
    final body = {
      'client_id': profile.id,
      'kind': profile.kind == ProfileKind.adult ? 'adult' : 'child',
      'name': profile.name,
      'dob': profile.dob.toIso8601String().split('T').first,
      'sex': _sexToWire(profile.sex),
      'environment': _envToWire(profile.environment),
      'religion_interest': profile.religionInterest,
      'religion': profile.religion ?? '',
      'consent_given': HiveSetup.sessionBox.get('consent_given') == true,
      'consent_ts': HiveSetup.sessionBox.get('consent_ts'),
      'is_active': isActive,
    };
    final resp = await _call(() => _api.upsertProfile(body),
        userMessage: 'Could not save profile. Check your connection.');
    _profileIds.set(profile.id, resp['id'] as int);
    await HiveSetup.childBox.put(profile.id, profile);
    return profile;
  }

  Future<void> activateProfile(String clientId) async {
    final serverId = _profileIds.serverIdFor(clientId);
    if (serverId == null) return; // not yet pushed — sign-in flow handles it
    await _call(() => _api.activateProfile(serverId),
        userMessage: 'Could not switch profile.');
    await HiveSetup.sessionBox.put('active_child_id', clientId);
  }

  /// Wipes ALL progress / reward-usage / mastery rows for one profile.
  /// Returns the local Hive boxes to a clean state too. The profile row
  /// itself, custom tasks, and custom rewards are preserved.
  Future<void> resetProgress(String clientId) async {
    final serverId = _profileIds.serverIdFor(clientId);
    if (serverId == null) {
      throw SyncException('Profile not synced yet.');
    }
    await _call(() => _api.resetProfileProgress(serverId),
        userMessage: 'Could not reset progress.');
    final progressKeys = HiveSetup.progressBox.keys
        .cast<String>()
        .where((k) => k.startsWith('$clientId::'))
        .toList();
    await HiveSetup.progressBox.deleteAll(progressKeys);
    // Reward usages cascade across all children since the box isn't keyed
    // by childId — match by value.
    final rewardKeys = HiveSetup.rewardUsageBox.toMap().entries
        .where((e) => e.value.childId == clientId)
        .map((e) => e.key)
        .toList();
    await HiveSetup.rewardUsageBox.deleteAll(rewardKeys);
    // Wipe practice counts / saved rewards / mastery markers.
    final session = HiveSetup.sessionBox;
    final wipeKeys = session.keys
        .cast<String>()
        .where(
          (k) =>
              k.startsWith('count::$clientId::') ||
              k.startsWith('reward::$clientId::') ||
              k.startsWith('mastery::$clientId::'),
        )
        .toList();
    if (wipeKeys.isNotEmpty) {
      await session.deleteAll(wipeKeys);
    }
  }

  Future<void> deleteProfile(String clientId) async {
    final serverId = _profileIds.serverIdFor(clientId);
    if (serverId != null) {
      await _call(() => _api.deleteProfile(serverId),
          userMessage: 'Could not delete profile.');
    }
    _profileIds._byClientId.remove(clientId);
    await HiveSetup.childBox.delete(clientId);
    // Cascade-clean local caches that referenced this profile.
    final progressKeys = HiveSetup.progressBox.keys
        .cast<String>()
        .where((k) => k.startsWith('$clientId::'))
        .toList();
    await HiveSetup.progressBox.deleteAll(progressKeys);
    final customTaskKeys = HiveSetup.customTaskBox.values
        .where((t) => t.childId == clientId)
        .map((t) => t.id)
        .toList();
    await HiveSetup.customTaskBox.deleteAll(customTaskKeys);
    final customRewardKeys = HiveSetup.customRewardBox.values
        .where((r) => r.childId == clientId)
        .map((r) => r.id)
        .toList();
    await HiveSetup.customRewardBox.deleteAll(customRewardKeys);
  }

  // ── Progress ─────────────────────────────────────────────────────────────

  Future<void> persistProgress(TaskProgress progress, {
    int? repetitionsDone,
    String? rewardTitle,
  }) async {
    final serverId = _profileIds.serverIdFor(progress.childId);
    if (serverId == null) {
      throw SyncException(
        'Profile not synced yet. Please re-open the app while online.',
      );
    }
    final body = <String, dynamic>{
      'profile': serverId,
      'task_slug': progress.taskSlug,
      'status': _statusToWire(progress.status),
      'repetitions_done': repetitionsDone ?? 0,
      'reward_title': rewardTitle ?? '',
      'completed_at': progress.completedAt?.toIso8601String(),
    };
    await _call(() => _api.upsertProgress(body),
        userMessage: 'Could not save progress. Check your connection.');
    await HiveSetup.progressBox.put(
      TaskProgress.key(progress.childId, progress.taskSlug),
      progress,
    );
  }

  // ── Custom tasks ─────────────────────────────────────────────────────────

  Future<void> persistCustomTask(CustomTask task) async {
    final serverId = _profileIds.serverIdFor(task.childId);
    if (serverId == null) {
      throw SyncException('Profile not synced yet.');
    }
    final body = {
      'profile': serverId,
      'client_id': task.id,
      'title': task.title,
      'how_to_md': task.howToMd,
      'parent_note_md': task.parentNoteMd,
    };
    await _call(() => _api.upsertCustomTask(body),
        userMessage: 'Could not save custom task.');
    await HiveSetup.customTaskBox.put(task.id, task);
  }

  Future<void> deleteCustomTask(CustomTask task) async {
    // Server has no upsert-by-client_id delete, so we resolve the row id
    // by listing the user's custom tasks (cheap — bounded per-user) and
    // deleting by pk. If the row doesn't exist on the server we still
    // wipe the local cache row.
    final serverId = _profileIds.serverIdFor(task.childId);
    if (serverId != null) {
      final rows = await _call(() => _api.listCustomTasks(serverId),
          userMessage: 'Could not delete task.');
      final match = rows.firstWhere(
        (r) => r['client_id'] == task.id,
        orElse: () => const {},
      );
      if (match.isNotEmpty) {
        await _call(() => _api.deleteCustomTask(match['id'] as int),
            userMessage: 'Could not delete task.');
      }
    }
    await HiveSetup.customTaskBox.delete(task.id);
    await HiveSetup.progressBox.delete(
      TaskProgress.key(task.childId, task.progressSlug),
    );
  }

  // ── Custom rewards ───────────────────────────────────────────────────────

  Future<void> persistCustomReward(CustomReward reward) async {
    final serverId = _profileIds.serverIdFor(reward.childId);
    if (serverId == null) {
      throw SyncException('Profile not synced yet.');
    }
    final body = {
      'profile': serverId,
      'client_id': reward.id,
      'title': reward.title,
      'notes': reward.notes,
      'is_free': reward.isFree,
    };
    await _call(() => _api.upsertCustomReward(body),
        userMessage: 'Could not save reward.');
    await HiveSetup.customRewardBox.put(reward.id, reward);
  }

  Future<void> deleteCustomReward(CustomReward reward) async {
    final serverId = _profileIds.serverIdFor(reward.childId);
    if (serverId != null) {
      final rows = await _call(() => _api.listCustomRewards(serverId),
          userMessage: 'Could not delete reward.');
      final match = rows.firstWhere(
        (r) => r['client_id'] == reward.id,
        orElse: () => const {},
      );
      if (match.isNotEmpty) {
        await _call(() => _api.deleteCustomReward(match['id'] as int),
            userMessage: 'Could not delete reward.');
      }
    }
    await HiveSetup.customRewardBox.delete(reward.id);
  }

  // ── Reward usage ─────────────────────────────────────────────────────────

  Future<void> recordRewardUsage(RewardUsage usage) async {
    final serverId = _profileIds.serverIdFor(usage.childId);
    if (serverId == null) {
      throw SyncException('Profile not synced yet.');
    }
    final body = {
      'profile': serverId,
      'reward_category': usage.rewardCategory,
      'reward_title': usage.rewardTitle,
      'used_at': usage.usedAt.toIso8601String(),
    };
    await _call(() => _api.createRewardUsage(body),
        userMessage: 'Could not log reward use.');
    await HiveSetup.rewardUsageBox.add(usage);
  }

  // ── Masteries ────────────────────────────────────────────────────────────

  Future<void> claimMastery({
    required String childClientId,
    required String masteryId,
    required DateTime earnedAt,
  }) async {
    final serverId = _profileIds.serverIdFor(childClientId);
    if (serverId == null) return; // race: sign-in not finished — skip remote
    final body = {
      'profile': serverId,
      'mastery_id': masteryId,
      'earned_at': earnedAt.toIso8601String(),
    };
    try {
      await _api.claimMastery(body);
    } on DioException {
      // Masteries are derived from progress; if the server didn't accept
      // we can re-derive on next bootstrap. Don't block the celebration.
    }
    await HiveSetup.sessionBox.put(
      'mastery::$childClientId::$masteryId',
      earnedAt.toIso8601String(),
    );
  }

  // ── Session items (UI state — filters, today's pick, etc.) ──────────────

  Future<void> persistSession({
    required String childClientId,
    required String key,
    required Object? value,
  }) async {
    final serverId = _profileIds.serverIdFor(childClientId);
    if (serverId == null) {
      // Pre-auth filter changes are a noop on the server; still cache locally.
      await HiveSetup.sessionBox.put(key, value);
      return;
    }
    try {
      await _api.upsertSession({
        'profile': serverId,
        'key': key,
        'value': value is bool ? {'v': value} : (value is List ? {'v': value} : value ?? {}),
      });
    } on DioException {
      // UI state is non-critical — don't surface a snackbar for a flipped chip.
    }
    await HiveSetup.sessionBox.put(key, value);
  }

  // ── Wipe (DPDP delete) ───────────────────────────────────────────────────

  Future<void> wipeRemote() async {
    await _call(() => _api.wipe(),
        userMessage: 'Could not delete remote data.');
    _profileIds.clear();
    await Future.wait([
      HiveSetup.childBox.clear(),
      HiveSetup.progressBox.clear(),
      HiveSetup.customTaskBox.clear(),
      HiveSetup.customRewardBox.clear(),
      HiveSetup.rewardUsageBox.clear(),
      HiveSetup.sessionBox.clear(),
    ]);
  }

  // ── Helpers ──────────────────────────────────────────────────────────────

  Future<T> _call<T>(Future<T> Function() fn,
      {required String userMessage}) async {
    try {
      return await fn();
    } on DioException catch (e) {
      throw SyncException(userMessage, cause: e);
    }
  }

  static String _sexToWire(Sex s) => switch (s) {
        Sex.boy => 'boy',
        Sex.girl => 'girl',
        Sex.other => 'other',
      };

  static String _envToWire(Environment e) => switch (e) {
        Environment.urban => 'urban',
        Environment.suburban => 'suburban',
        Environment.rural => 'rural',
      };

  static String _statusToWire(ProgressStatus s) => switch (s) {
        ProgressStatus.locked => 'locked',
        ProgressStatus.unlocked => 'unlocked',
        ProgressStatus.completed => 'completed',
        ProgressStatus.skippedKnown => 'skipped_known',
        ProgressStatus.skippedUnsuitable => 'skipped_unsuitable',
        ProgressStatus.bypassed => 'bypassed',
      };

  static ChildProfile _profileFromJson(Map<String, dynamic> p) {
    return ChildProfile(
      id: p['client_id'] as String,
      name: p['name'] as String,
      dob: DateTime.parse(p['dob'] as String),
      sex: switch (p['sex']) {
        'boy' => Sex.boy,
        'girl' => Sex.girl,
        _ => Sex.other,
      },
      environment: switch (p['environment']) {
        'urban' => Environment.urban,
        'rural' => Environment.rural,
        _ => Environment.suburban,
      },
      kind: p['kind'] == 'adult' ? ProfileKind.adult : ProfileKind.child,
      religionInterest: p['religion_interest'] as bool? ?? false,
      religion: (p['religion'] as String?)?.isEmpty == true
          ? null
          : p['religion'] as String?,
    );
  }

  static TaskProgress _progressFromJson(Map<String, dynamic> row,
      {required String childClientId}) {
    final raw = row['status'] as String;
    final status = switch (raw) {
      'locked' => ProgressStatus.locked,
      'completed' => ProgressStatus.completed,
      'skipped_known' => ProgressStatus.skippedKnown,
      'skipped_unsuitable' => ProgressStatus.skippedUnsuitable,
      'bypassed' => ProgressStatus.bypassed,
      _ => ProgressStatus.unlocked,
    };
    return TaskProgress(
      taskSlug: row['task_slug'] as String,
      childId: childClientId,
      status: status,
      completedAt: row['completed_at'] != null
          ? DateTime.parse(row['completed_at'] as String)
          : null,
    );
  }
}

final remoteSyncProvider = Provider<RemoteSync>((ref) {
  return RemoteSync(ref.watch(meApiProvider));
});
