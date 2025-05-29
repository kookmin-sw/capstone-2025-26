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
}
