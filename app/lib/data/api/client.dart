import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../local/hive_setup.dart';

/// Production API via Nginx proxy.
/// Override for local dev: --dart-define=API_BASE_URL=http://10.0.2.2:8001/api/v1
const apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://areafair.in/smartstep-admin/api/v1',
);

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
    contentType: 'application/json',
  ));
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) {
      final token = HiveSetup.sessionBox.get('access_token') as String?;
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
      handler.next(options);
    },
  ));
  return dio;
});
