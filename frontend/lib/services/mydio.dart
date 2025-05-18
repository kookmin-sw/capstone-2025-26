import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:reme/utils/secret.dart';

class MyDio {
  late Dio _dio;
  final storage = const FlutterSecureStorage();
  String? token;

  MyDio() {
    _dio = Dio(BaseOptions(
      baseUrl: api_baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
    initializeToken();
  }

  Future<void> initializeToken() async {
    token = await storage.read(key: 'AccessToken');
    if (token != null) {
      _dio.options.headers['Authorization'] = 'Bearer $token';
    }
  }

  Future<dynamic> get(String path) async {
    await initializeToken();
    try {
      var response = await _dio.get(path);
      return response;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout) {
        print('Timeout Error: ${e.message}');
      } else if (e.type == DioExceptionType.connectionError) {
        print('Connection Error: ${e.message}');
      } else {
        print('GET Error: ${e.message}');
        print('Response: ${e.response?.data}');
      }
      rethrow;
    }
  }

  Future<dynamic> post(String path, dynamic data) async {
    try {
      var response = await _dio.post(path, data: data);
      return response;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout) {
        print('Timeout Error: ${e.message}');
      } else if (e.type == DioExceptionType.connectionError) {
        print('Connection Error: ${e.message}');
      } else {
        print('POST Error: ${e.message}');
        print('Response: ${e.response?.data}');
      }
      rethrow;
    }
  }

  Future<dynamic> put(String path, dynamic data) async {
    try {
      var response = await _dio.put(path, data: data);
      return response;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout) {
        print('Timeout Error: ${e.message}');
      } else if (e.type == DioExceptionType.connectionError) {
        print('Connection Error: ${e.message}');
      } else {
        print('PUT Error: ${e.message}');
        print('Response: ${e.response?.data}');
      }
      rethrow;
    }
  }

  Future<dynamic> delete(String path) async {
    try {
      var response = await _dio.delete(path);
      return response;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout) {
        print('Timeout Error: ${e.message}');
      } else if (e.type == DioExceptionType.connectionError) {
        print('Connection Error: ${e.message}');
      } else {
        print('DELETE Error: ${e.message}');
        print('Response: ${e.response?.data}');
      }
      rethrow;
    }
  }

  Future<dynamic> patch(String path, dynamic data) async {
    try {
      var response = await _dio.patch(path, data: data);
      return response;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout) {
        print('Timeout Error: ${e.message}');
      } else if (e.type == DioExceptionType.connectionError) {
        print('Connection Error: ${e.message}');
      } else {
        print('DELETE Error: ${e.message}');
        print('Response: ${e.response?.data}');
      }
      rethrow;
    }
  }
}
