import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'client.dart';

/// Typed wrapper for `/api/v1/me/`. Every method requires the Dio
/// interceptor to have already loaded the access-token from sessionBox
/// (see `dioProvider`). 401s bubble up as DioException — the call sites
/// are responsible for prompting re-login.
///
/// Use the higher-level `RemoteSync` service (in `data/sync/remote_sync.dart`)
/// from screens — it composes these calls with local Hive cache updates and
/// surfaces "online required" errors as user-facing snackbars.
class MeApi {
  MeApi(this._dio);
  final Dio _dio;

  // ── State (bulk hydrate) ─────────────────────────────────────────────────

  Future<Map<String, dynamic>> fetchState() async {
    final resp = await _dio.get<Map<String, dynamic>>('/me/state/');
    return resp.data!;
  }

  // ── Profiles ─────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> upsertProfile(Map<String, dynamic> body) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/profiles/upsert/',
      data: body,
    );
    return resp.data!;
  }

  Future<void> deleteProfile(int id) async {
    await _dio.delete<void>('/me/profiles/$id/');
  }

  Future<Map<String, dynamic>> activateProfile(int id) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/profiles/$id/activate/',
    );
    return resp.data!;
  }

  Future<Map<String, dynamic>> resetProfileProgress(int id) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/profiles/$id/reset-progress/',
    );
    return resp.data!;
  }

  // ── Progress ─────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> upsertProgress(Map<String, dynamic> body) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/progress/upsert/',
      data: body,
    );
    return resp.data!;
  }

  Future<void> deleteProgress(int id) async {
    await _dio.delete<void>('/me/progress/$id/');
  }

  // ── Custom tasks ─────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> upsertCustomTask(
      Map<String, dynamic> body) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/custom-tasks/upsert/',
      data: body,
    );
    return resp.data!;
  }

  Future<List<Map<String, dynamic>>> listCustomTasks(int profileId) async {
    final resp = await _dio.get<List<dynamic>>(
      '/me/custom-tasks/',
      queryParameters: {'profile': profileId},
    );
    return (resp.data ?? const []).cast<Map<String, dynamic>>();
  }

  Future<void> deleteCustomTask(int id) async {
    await _dio.delete<void>('/me/custom-tasks/$id/');
  }

  // ── Custom rewards ───────────────────────────────────────────────────────

  Future<Map<String, dynamic>> upsertCustomReward(
      Map<String, dynamic> body) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/custom-rewards/upsert/',
      data: body,
    );
    return resp.data!;
  }

  Future<List<Map<String, dynamic>>> listCustomRewards(int profileId) async {
    final resp = await _dio.get<List<dynamic>>(
      '/me/custom-rewards/',
      queryParameters: {'profile': profileId},
    );
    return (resp.data ?? const []).cast<Map<String, dynamic>>();
  }

  Future<void> deleteCustomReward(int id) async {
    await _dio.delete<void>('/me/custom-rewards/$id/');
  }

  // ── Reward usage ─────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> createRewardUsage(
      Map<String, dynamic> body) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/reward-usage/',
      data: body,
    );
    return resp.data!;
  }

  // ── Masteries ────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> claimMastery(
      Map<String, dynamic> body) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/masteries/claim/',
      data: body,
    );
    return resp.data!;
  }

  // ── Session items ────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> upsertSession(
      Map<String, dynamic> body) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/me/session/upsert/',
      data: body,
    );
    return resp.data!;
  }

  // ── Account wipe (DPDP delete) ───────────────────────────────────────────

  Future<void> wipe() async {
    await _dio.delete<void>('/me/wipe/');
  }
}

final meApiProvider = Provider<MeApi>((ref) {
  return MeApi(ref.watch(dioProvider));
});
