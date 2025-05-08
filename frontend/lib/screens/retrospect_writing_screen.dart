import 'package:flutter/material.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/screens/retrospect_completion_screen.dart';
import 'package:reme/routes.dart';

class RetrospectWritingScreen extends StatefulWidget {
  final String methodName;
  final List<Map<String, dynamic>> selectedChallenges;

  const RetrospectWritingScreen({
    super.key,
    required this.methodName,
    required this.selectedChallenges,
  });

  @override
  State<RetrospectWritingScreen> createState() =>
      _RetrospectWritingScreenState();
}

class _RetrospectWritingScreenState extends State<RetrospectWritingScreen> {
  int _currentChallengeIndex = 0;
  final bool _isExpanded = false;
  final List<Map<String, dynamic>> _retrospectEntries = [];

  @override
  void initState() {
    super.initState();

    // Initialize entries for each challenge
    for (var challenge in widget.selectedChallenges) {
      _retrospectEntries.add({
        'challengeId': challenge['id'],
        'keepText': '',
        'problemText': '',
        'tryText': '',
        'isCompleted': false,
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentChallenge = widget.selectedChallenges[_currentChallengeIndex];
    final currentEntry = _retrospectEntries[_currentChallengeIndex];

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: false,
        title: null,
        leadingWidth: 52,
        leading: GestureDetector(
          onTap: () {
            Navigator.pop(context);
          },
          child: Container(
            margin: const EdgeInsets.only(top: 1, left: 16),
            child: const Icon(
              TabBarIcon.leftArrow,
              size: 20,
              color: Colors.white,
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          // 챌린지 제목
          Padding(
            padding: const EdgeInsets.fromLTRB(21.0, 27.0, 21.0, 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    // 현재 챌린지 번호
                    Text(
                      "${_currentChallengeIndex + 1}/${widget.selectedChallenges.length}",
                      style: const TextStyle(
                        color: Colors.white,
                        fontFamily: 'Pretendard',
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                  ],
                ),
                const SizedBox(height: 16),

                // 챌린지 제목
                Text(
                  currentChallenge['title'],
                  style: const TextStyle(
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

          // 챌린지 진행 상태 표시
          Container(
            margin: const EdgeInsets.fromLTRB(21.0, 0, 21.0, 16.0),
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(
              color: const Color(0xFF1A1A1A),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // 모든 챌린지에 대한 진행 상태 표시
                for (int i = 0; i < widget.selectedChallenges.length; i++)
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        _currentChallengeIndex = i;
                      });
                    },
                    child: Container(
                      margin: const EdgeInsets.symmetric(horizontal: 8.0),
                      width: 40,
                      child: Column(
                        children: [
                          // 언더바 또는 깃발
                          _retrospectEntries[i]['isCompleted']
                              ? const Icon(
                                  Icons.flag,
                                  color: Colors.green,
                                  size: 24,
                                )
                              : Container(
                                  height: 4,
                                  width: 30,
                                  decoration: BoxDecoration(
                                    color: i == _currentChallengeIndex
                                        ? Colors.blue
                                        : Colors.grey,
                                    borderRadius: BorderRadius.circular(2),
                                  ),
                                ),
                          const SizedBox(height: 8),

                          // 챌린지 번호
                          Text(
                            "${i + 1}",
                            style: TextStyle(
                              color: i == _currentChallengeIndex
                                  ? Colors.blue
                                  : Colors.grey,
                              fontFamily: 'Pretendard',
                              fontSize: 14,
                              fontWeight: i == _currentChallengeIndex
                                  ? FontWeight.bold
                                  : FontWeight.normal,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),

          // 회고 양식 (KPT 방식)
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(21.0, 10.0, 21.0, 10.0),
                child: Column(
                  children: [
                    // Keep 항목
                    _buildRetrospectField(
                      index: 0,
                      title: "Keep, 오늘 하루동안 유지하고 싶은 내용을 적어주세요",
                      hintText: "회고를 작성해 주세요",
                      value: currentEntry['keepText'],
                      onChanged: (value) {
                        setState(() {
                          currentEntry['keepText'] = value;
                        });
                      },
                    ),

                    const SizedBox(height: 16),

                    // Problem 항목
                    _buildRetrospectField(
                      index: 1,
                      title: "Problem, 오늘 어떤 문제가 있었죠?",
                      hintText: "회고를 작성해 주세요",
                      value: currentEntry['problemText'],
                      onChanged: (value) {
                        setState(() {
                          currentEntry['problemText'] = value;
                        });
                      },
                    ),

                    const SizedBox(height: 16),

                    // Try 항목
                    _buildRetrospectField(
                      index: 2,
                      title: "Try, 오늘 있었던 문제를 개선하기 위해 무엇을 시도해 볼까요?",
                      hintText: "회고를 작성해 주세요",
                      value: currentEntry['tryText'],
                      onChanged: (value) {
                        setState(() {
                          currentEntry['tryText'] = value;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.fromLTRB(16.0, 0, 16.0, 16.0),
        child: Row(
          children: [
            // 이전 챌린지 버튼
            Expanded(
              child: InkWell(
                onTap: () {
                  if (_currentChallengeIndex > 0) {
                    setState(() {
                      _currentChallengeIndex--;
                    });
                  }
                },
                child: Container(
                  height: 60,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A1A),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Center(
                    child: Text(
                      '이전 챌린지',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),

            // 다음 챌린지 버튼
            Expanded(
              child: InkWell(
                onTap: () {
                  // 현재 입력을 완료 처리
                  setState(() {
                    _retrospectEntries[_currentChallengeIndex]['isCompleted'] =
                        true;
                  });

                  // 다음 챌린지로 이동하거나, 모두 완료되었으면 결과 페이지로 이동
                  if (_currentChallengeIndex <
                      widget.selectedChallenges.length - 1) {
                    setState(() {
                      _currentChallengeIndex++;
                    });
                  } else {
                    // 모든 챌린지의 회고가 완료됨 - 애니메이션 화면으로 이동
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            const RetrospectCompletionScreen(),
                      ),
                    );
                  }
                },
                child: Container(
                  height: 60,
                  decoration: BoxDecoration(
                    color: const Color(0xFF223990),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Center(
                    child: Text(
                      _currentChallengeIndex ==
                              widget.selectedChallenges.length - 1
                          ? '완료'
                          : '다음 챌린지',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRetrospectField({
    required int index,
    required String title,
    required String hintText,
    required String value,
    required Function(String) onChanged,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1A),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 항목 제목
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontFamily: 'Pretendard',
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),

            // 입력 필드
            TextField(
              controller: TextEditingController(text: value)
                ..selection = TextSelection.fromPosition(
                    TextPosition(offset: value.length)),
              onChanged: onChanged,
              style: const TextStyle(
                color: Colors.white,
                fontFamily: 'Pretendard',
                fontSize: 16,
              ),
              decoration: InputDecoration(
                hintText: hintText,
                hintStyle: TextStyle(
                  color: Colors.white.withOpacity(0.5),
                  fontFamily: 'Pretendard',
                  fontSize: 16,
                ),
                border: InputBorder.none,
                contentPadding: EdgeInsets.zero,
              ),
              maxLines: 4,
              minLines: 3,
            ),
          ],
        ),
      ),
    );
  }
}
