import 'package:dio/dio.dart';
import 'package:reme/services/mydio.dart'; // MyDio 클래스의 실제 경로로 수정하세요.

class ChallengeApi {
  final MyDio _dio = MyDio();

  Future<Response> createChallenge(String name) async {
    try {
      // _dio.post 호출 시 'data:' 이름표 없이 두 번째 인자로 데이터를 전달합니다.
      final Map<String, dynamic> payload = {
        'challenge_name': name,
        'owner_type': 'USER',
        'status': 'LIVE'
      };
      return await _dio.post(
          '/retrospect/challenges/', payload); // <--- 이 부분 수정
    } catch (e) {
      rethrow;
    }
  }

  Future<Response> getChallenges() async {
    try {
      // get 메소드는 파라미터가 없으므로 변경 없음
      return await _dio.get('/retrospect/challenges/');
    } catch (e) {
      rethrow;
    }
  }

  // 만약 다른 API 호출 (예: PUT, PATCH)도 있다면 동일하게 수정 필요
  // 예시:
  // Future<Response> updateChallenge(String id, Map<String, dynamic> challengeData) async {
  //   try {
  //     return await _dio.put('/retrospect/challenges/$id/', challengeData); // 'data:' 없이 전달
  //   } catch (e) {
  //     rethrow;
  //   }
  // }
}
