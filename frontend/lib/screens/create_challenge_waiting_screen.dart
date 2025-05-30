import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/routes.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/services/challenge_api.dart';
import 'package:logger/logger.dart';
import 'package:dio/dio.dart';

class CreateChallengeWaitingScreen extends StatefulWidget {
  const CreateChallengeWaitingScreen({super.key});

  @override
  State<CreateChallengeWaitingScreen> createState() =>
      _CreateChallengeWaitingScreenState();
}

class _CreateChallengeWaitingScreenState
    extends State<CreateChallengeWaitingScreen> {
  bool _isNavigating = false;

  final _challengeApi = ChallengeApi();
  final _logger = Logger();
  @override
  void initState() {
    super.initState();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _createChallengeAndProceed();
    });
  }

  Future<void> _createChallengeAndProceed() async {
    if (_isNavigating) return; // 이미 네비게이션 중이면 중단
    _isNavigating = true;
    try {
      try {
        await _challengeApi.getChallenges(); // 이미 있는 GET 메소드 활용
      } catch (e) {
        // GET 요청 실패는 무시 (토큰 초기화가 목적)
      }
      final arguments = ModalRoute.of(context)?.settings.arguments;
      String challengeName = '새 챌린지';

      if (arguments is String) {
        challengeName = arguments;
      }
      final String deadlineValue =
          DateTime.now().add(const Duration(days: 7)).toIso8601String();
      const String ownerTypeValue = 'USER';
      const String statusValue = 'LIVE';

      // 1. 챌린지 생성
      final challengeResponse = await _challengeApi.createChallenge(
        challengeName,
        deadlineValue,
        ownerTypeValue,
        statusValue,
      );

      if (challengeResponse.statusCode == 201) {
        final challengeData = challengeResponse.data as Map<String, dynamic>;
        final challengeId = challengeData['id'];

        _logger.i('챌린지 생성 성공: $challengeId');

        // 2. AI 플랜 생성
        _logger.i('=== AI 플랜 생성 시작 ===');
        _logger.i('챌린지 ID: $challengeId, 이름: $challengeName');

        final plansResponse =
            await _challengeApi.generateAIPlans(challengeId, challengeName);

        _logger.i('AI 플랜 생성 응답 상태: ${plansResponse.statusCode}');
        _logger.i('AI 플랜 생성 결과: ${plansResponse.data}'); // 전체 응답 로깅
        // 생성된 플랜에서 planIds 추출
        List<int> planIds = [];
        if (plansResponse.statusCode == 201 && plansResponse.data != null) {
          final plansData = plansResponse.data;

          // AI 플랜 응답 구조에 따라 planIds 추출
          if (plansData is Map<String, dynamic> &&
              plansData.containsKey('plans')) {
            final plans = plansData['plans'] as List<dynamic>;
            planIds = plans.map((plan) => plan['id'] as int).toList();
          }

          _logger.i('추출된 planIds: $planIds');
        }

        // AI KPI 생성
        _logger.i('=== AI KPI 생성 시작 ===');
        final kpiResponse =
            await _challengeApi.generateAIKPIs(challengeId, planIds);
        final challengeDataWithKPIs = {
          'id': challengeId,
          'challenge_name': challengeName,
          'generated_kpis': kpiResponse.data['kpis'],
          'generated_plans': plansResponse.data['plans'], // 플랜도 함께 전달
        };

        _logger.i('AI KPI 생성 응답 상태: ${kpiResponse.statusCode}');
        _logger.i('AI KPI 생성 결과: ${kpiResponse.data}'); // 전체 응답 로깅
        _logger.i('========================');
        // 4. 모든 생성 완료 후 다음 화면으로
        if (mounted) {
          await Navigator.of(context).pushReplacementNamed(
            Routes.createChallengePlan,
            arguments: challengeDataWithKPIs,
          );
        }
      }
    } catch (e) {
      _logger.e('챌린지 생성 실패: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('챌린지 생성에 실패했습니다.'),
            backgroundColor: Colors.red,
          ),
        );
        Navigator.of(context).pop(); // 이전 화면으로 돌아가기
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final arguments = ModalRoute.of(context)?.settings.arguments;
    String challengeName = '새 챌린지'; // 기본값

    if (arguments is String) {
      challengeName = arguments;
    } else if (arguments is Map<String, dynamic>) {
      challengeName = arguments['challenge_name'] ?? '새 챌린지';
    }

    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: background,
        elevation: 0,
        automaticallyImplyLeading: false,
        leadingWidth: 52,
        leading: GestureDetector(
          onTap: () {
            Navigator.pop(context);
          },
          child: Container(
            margin: const EdgeInsets.only(left: 16),
            child: const Icon(
              TabBarIcon.leftArrow,
              size: 20,
              color: Colors.white,
            ),
          ),
        ),
      ),
      body: SafeArea(
        bottom: false,
        child: Stack(
          children: [
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 24.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(height: 16.h),
                  Text(
                    challengeName,
                    style: TextStyle(
                      color: fontColor,
                      fontSize: 26.sp,
                      fontWeight: FontWeight.w800,
                      fontFamily: 'Pretendard',
                    ),
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    '챌린지의 플랜 생성 중이에요!',
                    style: TextStyle(
                      color: fontColor,
                      fontSize: 22.sp,
                      fontWeight: FontWeight.w800,
                      fontFamily: 'Pretendard',
                    ),
                  ),
                  const Spacer(),
                  // 말풍선
                  Container(
                    width: 228.w,
                    alignment: Alignment.center,
                    margin: EdgeInsets.only(bottom: 20.h),
                    padding:
                        EdgeInsets.symmetric(horizontal: 22.w, vertical: 14.h),
                    decoration: BoxDecoration(
                      color: c900,
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(24.r),
                        topRight: Radius.circular(24.r),
                        bottomLeft: Radius.circular(24.r),
                        bottomRight: Radius.circular(5.r),
                      ),
                    ),
                    child: Text(
                      '조금만 기다려줘!',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 25.sp,
                        fontWeight: FontWeight.w700,
                        fontFamily: 'Pretendard',
                      ),
                    ),
                  ),
                  const Center(),
                  SizedBox(height: 350.h),
                ],
              ),
            ),
            // 캐릭터 이미지 (에러 방지)
            Positioned(
              right: 0.w,
              bottom: 0,
              child: Image.asset(
                'assets/img/character_attention.png',
                width: 260.w,
                fit: BoxFit.contain,
                errorBuilder: (context, error, stackTrace) {
                  debugPrint('이미지 로드 오류: $error');
                  return Container(
                    width: 260.w,
                    height: 260.h,
                    color: Colors.transparent,
                    alignment: Alignment.center,
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
