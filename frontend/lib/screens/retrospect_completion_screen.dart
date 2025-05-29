import 'package:flutter/material.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/screens/animation_test.dart';
import 'package:reme/services/retrospect_api.dart';
import 'package:reme/themes/color.dart';
import 'dart:async';
import 'package:reme/routes.dart';
import 'package:reme/widgets/challengeTypeItem.dart';

class RetrospectCompletionScreen extends StatefulWidget {
  final List<Map<String, dynamic>> retrospectEntries;
  const RetrospectCompletionScreen(
      {super.key, required this.retrospectEntries});

  @override
  State<RetrospectCompletionScreen> createState() =>
      _RetrospectCompletionScreenState();
}

class _RetrospectCompletionScreenState
    extends State<RetrospectCompletionScreen> {
  bool _isDataReceived = false;
  Timer? _mockAITimer;

  @override
  void initState() {
    super.initState();

    if (mounted) {
      Future.wait(widget.retrospectEntries.map((currentRetrospect) =>
          createRetrospect(
              challenge_id: currentRetrospect['challengeId'],
              template_id: currentRetrospect['templateId'],
              content: currentRetrospect['content'],
              crew_id: currentRetrospect['crew_id'] ?? null))).then((value) {
        // Value로 받은 값들을 다시 kpi-result로 요청.
        // 그래서 받은 값을 _navigateToAnalysisScreen에 넘기기.

        setState(() {
          _isDataReceived = true;
        });
        // Navigate to the analysis screen
        _navigateToAnalysisScreen();
      });
    }
  }

  @override
  void dispose() {
    _mockAITimer?.cancel();
    super.dispose();
  }

  void _navigateToAnalysisScreen() {
    // Navigate to the reflection analysis page after receiving data
    List<dynamic> kpiResult = [];
    Future.wait(widget.retrospectEntries.map((currentRetrospect) =>
        getKpiResult(
                challenge_id: currentRetrospect['challengeId'],
                date: DateTime.now(),
                count: 0)
            .then((value) {
          kpiResult.add(value);
        }))).then((_) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => ReflectionAnalysisScreen(data: kpiResult),
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      // 뒤로가기 버튼 처리
      onWillPop: () async {
        // 홈 화면으로 이동
        Navigator.pushNamedAndRemoveUntil(
            context, Routes.splash, (route) => false);
        return false; // WillPopScope의 기본 동작 방지
      },
      child: const Scaffold(
        backgroundColor: background,
        body: SafeArea(
          child: Stack(
            children: [
              // 기존 컨텐츠
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 상단 여백 (뒤로가기 버튼 높이만큼)
                  SizedBox(height: 40),

                  // 메시지
                  Padding(
                    padding: EdgeInsets.fromLTRB(21.0, 27.0, 21.0, 40.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "오늘 회고가 마무리 되었습니다.",
                          style: TextStyle(
                            color: Colors.white,
                            fontFamily: 'Pretendard',
                            fontSize: 27,
                            fontWeight: FontWeight.w800,
                            height: 1.50,
                            letterSpacing: 0.54,
                          ),
                        ),
                        SizedBox(height: 8),
                        Text(
                          "잠시만 기다려 주세요...",
                          style: TextStyle(
                            color: Colors.white,
                            fontFamily: 'Pretendard',
                            fontSize: 27,
                            fontWeight: FontWeight.w800,
                            height: 1.50,
                            letterSpacing: 0.54,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // 애니메이션
                  Expanded(
                    child: Stack(
                      children: [
                        // StaggeredBoxAnimation 위젯 사용
                        StaggeredBoxAnimation(),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// This is a temporary implementation based on the image
// Replace this with your actual reflection analysis screen implementation
class ReflectionAnalysisScreen extends StatefulWidget {
  bool fromMyPage;
  dynamic data;
  ReflectionAnalysisScreen({super.key, this.fromMyPage = false, this.data});

  @override
  State<ReflectionAnalysisScreen> createState() =>
      _ReflectionAnalysisScreenState();
}

class _ReflectionAnalysisScreenState extends State<ReflectionAnalysisScreen> {
  int _selectedTabIndex = 0;
  late String month;
  late String day;

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    month = widget.data[0][0]['created_at'].split('T')[0].split('-')[1];
    day = widget.data[0][0]['created_at'].split('T')[0].split('-')[2];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      body: SafeArea(
        child: Stack(
          children: [
            // 뒤로가기 버튼
            Positioned(
              top: 1,
              left: 13,
              child: GestureDetector(
                onTap: () {
                  if (widget.fromMyPage) {
                    Navigator.pop(context);
                  } else {
                    Navigator.pushNamedAndRemoveUntil(
                        context, Routes.splash, (route) => false);
                  }
                },
                child: Container(
                    margin: const EdgeInsets.only(left: 16),
                    child: const Icon(
                      TabBarIcon.leftArrow,
                      size: 20,
                      color: Colors.white,
                    )),
              ),
            ),

            // 기존 컨텐츠
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 상단 여백 (뒤로가기 버튼 높이만큼)
                const SizedBox(height: 40),

                // 타이틀 텍스트
                Padding(
                  padding: EdgeInsets.fromLTRB(21.0, 0.0, 21.0, 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "${month}/${day}일 오늘도 수고하셨어요!",
                        style: const TextStyle(
                          color: Colors.white,
                          fontFamily: 'Pretendard',
                          fontSize: 27,
                          fontWeight: FontWeight.w800,
                          height: 1.50,
                          letterSpacing: 0.54,
                        ),
                      ),
                      const Text(
                        "내일도 잊지말고 같이 회고해요",
                        style: TextStyle(
                          color: Colors.white,
                          fontFamily: 'Pretendard',
                          fontSize: 27,
                          fontWeight: FontWeight.w800,
                          height: 1.50,
                          letterSpacing: 0.54,
                        ),
                      ),
                    ],
                  ),
                ),

                // 탭 바
                Container(
                  decoration: const BoxDecoration(
                    border: Border(
                      bottom: BorderSide(
                        color: boxBackgroundColor,
                        width: 1.0,
                      ),
                    ),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: GestureDetector(
                          onTap: () {
                            setState(() {
                              _selectedTabIndex = 0;
                            });
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 12.0),
                            decoration: BoxDecoration(
                              border: Border(
                                bottom: BorderSide(
                                  color: _selectedTabIndex == 0
                                      ? Colors.white
                                      : Colors.transparent,
                                  width: 2.0,
                                ),
                              ),
                            ),
                            child: Center(
                              child: Text(
                                "오늘 회고 분석",
                                style: TextStyle(
                                  color: Colors.white,
                                  fontFamily: 'Pretendard',
                                  fontSize: 16,
                                  fontWeight: _selectedTabIndex == 0
                                      ? FontWeight.w600
                                      : FontWeight.w400,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      Expanded(
                        child: GestureDetector(
                          onTap: () {
                            setState(() {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('준비중입니다'),
                                  duration: Duration(seconds: 1),
                                ),
                              );
                              // _selectedTabIndex = 1;
                            });
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 12.0),
                            decoration: BoxDecoration(
                              border: Border(
                                bottom: BorderSide(
                                  color: _selectedTabIndex == 1
                                      ? Colors.white
                                      : background,
                                  width: 2.0,
                                ),
                              ),
                            ),
                            child: Center(
                              child: Text(
                                "주간 회고 분석",
                                style: TextStyle(
                                  color: Colors.white,
                                  fontFamily: 'Pretendard',
                                  fontSize: 16,
                                  fontWeight: _selectedTabIndex == 1
                                      ? FontWeight.w600
                                      : FontWeight.w400,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // 탭 내용
                Expanded(
                  child: SingleChildScrollView(
                    child: _selectedTabIndex == 0
                        ? _buildDailyAnalysis(widget.data)
                        : _buildWeeklyAnalysis(),
                  ),
                ),

                // 하단 버튼
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: ElevatedButton(
                    onPressed: () {
                      // 만약 크루에서 시작된 회고라면
                      // setVisibility(retrospect_id: retrospect_id, visibility: "CREW", crew_id: crew_id);
                      // 개인 회고 라면
                      // setVisibility(retrospect_id: retrospect_id, visibility: "PUBLIC");
                      Navigator.pushNamedAndRemoveUntil(
                          context, Routes.splash, (route) => false);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF223990),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      minimumSize: const Size(double.infinity, 60),
                    ),
                    child: const Text(
                      "오늘 회고 공유하기",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDailyAnalysis(dynamic data) {
    return Column(
      children: [
        for (var item in data)
          ChallengeTypeItem(
            title: '건강하게 운동하기', // TODO: 챌린지 아이디 가지고 이름 가져오기
            description: '${item[0]['comment']}',
            score: item[0]['score'],
            hasSuccess: item[0]['score'] > 50 ? true : false,
            imagePath: '',
          )
      ],
    );
  }

  Widget _buildWeeklyAnalysis() {
    return Column(
      children: [
        _buildTimeBasedChallengeItem(
          period: "3월 23일 ~ 3월 29일",
          description: "이번주에는 총 25km를 달렸어요! 놀라운 성과에요. 예사비라는 새로운 저칼로리식단도 시도했네요.",
          score: 78,
          hasSuccess: true,
        ),
        _buildTimeBasedChallengeItem(
          period: "3월 21일 ~ 3월 28일",
          description: "이번주엔 별로 달리지 않았군요. 포스팅도 1번만 달았어요. 다음주에는 분발해 보도록 해요!",
          score: 13,
          hasSuccess: false,
        ),
        _buildTimeBasedChallengeItem(
          period: "3월 13일 ~ 3월 20일",
          description: "이번주엔 별로 달리지 않았군요. 포스팅도 1번만 달았어요. 다음주에는 분발해 보도록 해요!",
          score: 13,
          hasSuccess: false,
        ),
      ],
    );
  }

  Widget _buildTimeBasedChallengeItem({
    required String period,
    required String description,
    required int score,
    required bool hasSuccess,
  }) {
    return Container(
      margin: const EdgeInsets.fromLTRB(21.0, 0.0, 21.0, 0),
      padding: const EdgeInsets.all(16.0),
      decoration: const BoxDecoration(
        color: background,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: Colors.blue,
                  borderRadius: BorderRadius.circular(18),
                ),
                child: const Icon(
                  Icons.person,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                period,
                style: const TextStyle(
                  color: Colors.white,
                  fontFamily: 'Pretendard',
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            description,
            style: const TextStyle(
              color: Colors.white,
              fontFamily: 'Pretendard',
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(
                hasSuccess ? Icons.local_fire_department : Icons.warning,
                color: hasSuccess ? Colors.orange : Colors.yellow,
                size: 24,
              ),
              const SizedBox(width: 4),
              Text(
                "$score/100",
                style: TextStyle(
                  color: hasSuccess ? Colors.orange : Colors.yellow,
                  fontFamily: 'Pretendard',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
