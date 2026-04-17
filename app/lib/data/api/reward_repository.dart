import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models.dart';
import 'client.dart';

class RewardRepository {
  RewardRepository(this._dio);
  final Dio _dio;

  Future<List<Reward>> fetch({int? age}) async {
    final resp = await _dio.get<dynamic>(
      "/rewards/",
      queryParameters: {if (age != null) "age": age},
    );
    return (resp.data as List)
        .cast<Map<String, dynamic>>()
        .map(Reward.fromJson)
        .toList(growable: false);
  }

  Future<void> postCompletion({
    required String taskSlug,
    required String ageBand,
    required String environment,
  }) async {
    await _dio.post<dynamic>(
      "/telemetry/task-completion/",
      data: {
        "task_slug": taskSlug,
        "age_band": ageBand,
        "environment": environment,
      },
    );
  }
}

final rewardRepositoryProvider = Provider<RewardRepository>((ref) {
  return RewardRepository(ref.watch(dioProvider));
});
