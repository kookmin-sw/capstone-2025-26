import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:reme/utils/secret.dart';

class MyDio {
  var _dio = Dio();
  var storage = FlutterSecureStorage();
  String? token;
  MyDio() {
    _dio.options.baseUrl = api_baseUrl;
    _dio.options.connectTimeout = const Duration(seconds: 5);
    _dio.options.receiveTimeout = const Duration(seconds: 3);
    getToken().then((value) {
      token = value;
      _dio.options.headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      };
    });
  }

  Future<String?> getToken() async {
    return await storage.read(key: 'AccessToken');
  }

  Future<void> get(String path) async {
    try {
      var response = await _dio.get(path);
      return response.data;
    } catch (e) {
      throw e;
    }
  }

  Future<void> post(String path, dynamic data) async {
    try {
      var response = await _dio.post(path, data: data);
      return response.data;
    } catch (e) {
      throw e;
    }
  }

  Future<void> put(String path, dynamic data) async {
    try {
      var response = await _dio.put(path, data: data);
      return response.data;
    } catch (e) {
      throw e;
    }
  }

  Future<void> delete(String path) async {
    try {
      var response = await _dio.delete(path);
      return response.data;
    } catch (e) {
      throw e;
    }
  }
}
