import 'package:dio/dio.dart';
import 'package:reme/services/mydio.dart';
import 'package:logger/logger.dart';

class ChallengeApi {
  final MyDio _dio = MyDio();
  final _logger = Logger();

  Future<Response> createChallenge(
    String name,
    String deadline,
    String ownerType,
    String status,
  ) async {
    try {
      final Map<String, dynamic> payload = {
        'challenge_name': name,
        'deadline': deadline,
        'owner_type': ownerType,
        'status': status,
      };
      _logger.i('챌린지 생성 요청 페이로드: $payload');
      return await _dio.post('/retrospect/challenges/', payload);
    } catch (e) {
      _logger.e('ChallengeApi.createChallenge 오류: $e');
      rethrow;
    }
  }

  Future<Response> getChallenges() async {
    try {
      return await _dio.get('/retrospect/challenges/');
    } catch (e) {
      rethrow;
    }
  }

  Future<Response> createPlan(int challengeId, String planText) async {
    try {
      final Map<String, dynamic> payload = {
        'challenge': challengeId,
        'plan_text': planText,
      };
      _logger.i('플랜 생성 요청 페이로드: $payload');
      return await _dio.post('/retrospect/plans/', payload);
    } catch (e) {
      _logger.e('ChallengeApi.createPlan 오류: $e');
      rethrow;
    }
  }

  Future<Response> getPlans(int challengeId) async {
    try {
      return await _dio.get('/retrospect/plans/?challenge=$challengeId');
    } catch (e) {
      _logger.e('ChallengeApi.getPlans 오류: $e');
      rethrow;
    }
  }

  Future<Response> updatePlan(int planId, String planText) async {
    try {
      final Map<String, dynamic> payload = {
        'plan_text': planText,
      };
      return await _dio.patch('/retrospect/plans/$planId/', payload);
    } catch (e) {
      _logger.e('ChallengeApi.updatePlan 오류: $e');
      rethrow;
    }
  }

  Future<Response> generateAIPlans(
      int challengeId, String challengeName) async {
    try {
      final Map<String, dynamic> payload = {
        'challenge_id': challengeId,
        'user_context': '$challengeName 챌린지를 성공적으로 달성하고 싶습니다',
        'item_count': 5
      };
      return await _dio.post('/ai/generate-plan/', payload);
    } catch (e) {
      _logger.e('AI 플랜 생성 오류: $e');
      rethrow;
    }
  }

  Future<Response> generateAIKPIs(int challengeId, List<int> planIds) async {
    try {
      final Map<String, dynamic> payload = {
        'challenge_id': challengeId,
        'plan_ids': planIds,
        'context': '측정 가능한 성과 지표가 필요합니다',
        'item_count': 3
      };
      return await _dio.post('/ai/generate-kpi/', payload);
    } catch (e) {
      _logger.e('AI KPI 생성 오류: $e');
      rethrow;
    }
  }

  Future<Response> getKPIs(int challengeId) async {
    try {
      return await _dio.get('/retrospect/kpis/?challenge=$challengeId');
    } catch (e) {
      _logger.e('ChallengeApi.getKPIs 오류: $e');
      rethrow;
    }
  }

  /// 회고 가능한 챌린지 목록 조회
  Future<Response> getRetrospectChallenges({int? limit}) async {
    try {
      String endpoint = '/retrospect/challenges/';
      if (limit != null) {
        endpoint += '?limit=$limit';
      }

      _logger.i('회고 챌린지 조회 요청: $endpoint');
      return await _dio.get(endpoint);
    } catch (e) {
      _logger.e('회고 챌린지 조회 오류: $e');
      rethrow;
    }
  }

  /// 특정 사용자의 완료된 챌린지 조회 (회고 대상)
  Future<Response> getCompletedChallenges({int? userId}) async {
    try {
      String endpoint = '/challenges/completed/';
      if (userId != null) {
        endpoint += '?user_id=$userId';
      }

      _logger.i('완료된 챌린지 조회 요청: $endpoint');
      return await _dio.get(endpoint);
    } catch (e) {
      _logger.e('완료된 챌린지 조회 오류: $e');
      rethrow;
    }
  }

  /// 회고 데이터가 있는 챌린지 조회
  Future<Response> getChallengesWithRetrospect() async {
    try {
      const endpoint = '/challenges/with-retrospect/';

      _logger.i('회고 데이터 포함 챌린지 조회 요청');
      return await _dio.get(endpoint);
    } catch (e) {
      _logger.e('회고 데이터 포함 챌린지 조회 오류: $e');
      rethrow;
    }
  }
}
