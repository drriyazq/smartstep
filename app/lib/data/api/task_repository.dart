import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models.dart';
import 'client.dart';

class TaskRepository {
  TaskRepository(this._dio);
  final Dio _dio;

  List<Task>? _cache;
  Map<String, String?> _cacheParams = {};

  Future<List<Task>> fetchAll({
    String? environment,
    int? minAge,
    int? maxAge,
    String? sex,
  }) async {
    final params = <String, String?>{
      'environment': environment,
      'sex': (sex != null && sex != 'any') ? sex : null,
    };

    if (_cache != null && _cacheParams['environment'] == params['environment'] && _cacheParams['sex'] == params['sex']) {
      return _cache!;
    }

    final resp = await _dio.get<dynamic>(
      "/tasks/",
      queryParameters: {
        if (environment != null) "environment": environment,
        if (minAge != null) "min_age": minAge,
        if (maxAge != null) "max_age": maxAge,
        if (sex != null && sex != "any") "sex": sex,
      },
    );
    final list = (resp.data as List).cast<Map<String, dynamic>>();
    _cache = list.map(Task.fromJson).toList(growable: false);
    _cacheParams = params;
    return _cache!;
  }

  List<Task>? get cached => _cache;

  void invalidate() {
    _cache = null;
    _cacheParams = {};
  }
}

final taskRepositoryProvider = Provider<TaskRepository>((ref) {
  return TaskRepository(ref.watch(dioProvider));
});
