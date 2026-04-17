import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models.dart';
import 'client.dart';

class TaskRepository {
  TaskRepository(this._dio);
  final Dio _dio;

  List<Task>? _cache;

  Future<List<Task>> fetchAll({
    String? environment,
    int? minAge,
    int? maxAge,
  }) async {
    final resp = await _dio.get<dynamic>(
      "/tasks/",
      queryParameters: {
        if (environment != null) "environment": environment,
        if (minAge != null) "min_age": minAge,
        if (maxAge != null) "max_age": maxAge,
      },
    );
    final list = (resp.data as List).cast<Map<String, dynamic>>();
    _cache = list.map(Task.fromJson).toList(growable: false);
    return _cache!;
  }

  List<Task>? get cached => _cache;
}

final taskRepositoryProvider = Provider<TaskRepository>((ref) {
  return TaskRepository(ref.watch(dioProvider));
});
