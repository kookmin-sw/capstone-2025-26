import 'package:flutter/material.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/screens/retrospect_method_selection.dart';

class RetrospectChallengeList extends StatefulWidget {
  const RetrospectChallengeList({super.key});

  @override
  State<RetrospectChallengeList> createState() =>
      _RetrospectChallengeListState();
}

class _RetrospectChallengeListState extends State<RetrospectChallengeList> {
  // 선택된 챌린지들을 추적하기 위한 Set
  final Set<int> _selectedChallenges = {};

  // 현재 선택된 카테고리 (0: 전체, 1: 개인, 2: 크루)
  int _selectedCategory = 0;

  @override
  Widget build(BuildContext context) {
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
          // 타이틀 텍스트
          const Padding(
            padding: EdgeInsets.fromLTRB(21.0, 27.0, 16.0, 27.0),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '오늘 회고할 챌린지를',
                    style: TextStyle(
                      color: Colors.white,
                      fontFamily: 'Pretendard',
                      fontSize: 27,
                      fontWeight: FontWeight.w800,
                      height: 1.50,
                      letterSpacing: 0.54,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    '선택해 주세요!',
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
          ),

          // 분리된 버튼들
          Padding(
            padding: const EdgeInsets.fromLTRB(21.0, 0.0, 30.0, 0.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildCategoryButton("전체", 0, height: 25),
                const SizedBox(width: 20),
                _buildCategoryButton("개인", 1, height: 25),
                const SizedBox(width: 20),
                _buildCategoryButton("크루", 2, height: 25),
              ],
            ),
          ),

          // 챌린지 리스트
          Expanded(
            child: _buildChallengeList(
                type: _selectedCategory == 0
                    ? 'all'
                    : _selectedCategory == 1
                        ? 'personal'
                        : 'crew'),
          ),
        ],
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.fromLTRB(16.0, 0, 16.0, 16.0),
        child: InkWell(
          onTap: () {
            // Navigate to the retrospective method selection screen
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const RetrospectMethodSelection(),
              ),
            );
          },
          child: Container(
            height: 60,
            decoration: BoxDecoration(
              color: const Color(0xFF223990),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Center(
              child: Text(
                '선택완료',
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
    );
  }

  Widget _buildCategoryButton(String text, int index, {double? height}) {
    bool isSelected = _selectedCategory == index;

    return Expanded(
      child: ElevatedButton(
        onPressed: () {
          setState(() {
            _selectedCategory = index;
          });
        },
        style: ElevatedButton.styleFrom(
          backgroundColor:
              isSelected ? const Color(0xFF223990) : const Color(0xFF171717),
          foregroundColor: Colors.white,
          elevation: 0,
          padding:
              EdgeInsets.symmetric(vertical: height != null ? height / 5 : 18),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
            side: BorderSide.none,
          ),
        ),
        child: SizedBox(
          height: height,
          child: Text(
            text,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildChallengeList({String type = 'all'}) {
    // 챌린지 목록 데이터
    final challenges = _getChallenges();
    final filteredChallenges = type == 'all'
        ? challenges
        : challenges.where((c) => c['type'] == type).toList();

    return ListView.builder(
      padding: const EdgeInsets.only(top: 16.0, bottom: 80.0),
      itemCount: filteredChallenges.length + 1, // +1 for the 모두 선택 button
      itemBuilder: (context, index) {
        // 마지막 아이템인 경우 모두 선택 버튼 표시
        if (index == filteredChallenges.length) {
          return Padding(
            padding:
                const EdgeInsets.symmetric(vertical: 16.0, horizontal: 16.0),
            child: Align(
              alignment: Alignment.centerRight,
              child: SizedBox(
                width: 120,
                height: 45,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF223990),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                  ),
                  onPressed: () {
                    setState(() {
                      // 현재 카테고리에 맞는 챌린지 목록 가져오기
                      final challenges = _getChallenges();
                      final filteredChallenges = _selectedCategory == 0
                          ? challenges
                          : challenges
                              .where((c) =>
                                  c['type'] ==
                                  (_selectedCategory == 1
                                      ? 'personal'
                                      : 'crew'))
                              .toList();

                      // 현재 탭에 맞는 챌린지들의 ID를 가져옴
                      final tabChallengeIds =
                          filteredChallenges.map((c) => c['id'] as int).toSet();

                      // 이미 모두 선택되어 있으면 모두 해제, 아니면 모두 선택
                      final allSelected = tabChallengeIds
                          .every((id) => _selectedChallenges.contains(id));

                      if (allSelected) {
                        _selectedChallenges.removeAll(tabChallengeIds);
                      } else {
                        _selectedChallenges.addAll(tabChallengeIds);
                      }
                    });
                  },
                  child: const Text('모두 선택', style: TextStyle(fontSize: 16)),
                ),
              ),
            ),
          );
        }

        final challenge = filteredChallenges[index];
        final hasImage = challenge.containsKey('image');
        final id = challenge['id'] as int;
        final isSelected = _selectedChallenges.contains(id);

        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 16.0),
          child: Row(
            children: [
              Container(
                width: 45,
                height: 45,
                decoration: BoxDecoration(
                  color: challenge['iconBgColor'] as Color,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: hasImage
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.asset(
                          challenge['image'] as String,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            // 이미지 로드 실패시 아이콘 표시
                            return Icon(
                              challenge['icon'] as IconData,
                              color: Colors.white,
                              size: 24,
                            );
                          },
                        ),
                      )
                    : Icon(
                        challenge['icon'] as IconData,
                        color: Colors.white,
                        size: 24,
                      ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Text(
                  challenge['title'] as String,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                  ),
                ),
              ),
              SizedBox(
                height: 38,
                width: 70,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1A1A1A),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    padding: EdgeInsets.zero,
                  ),
                  onPressed: () {
                    setState(() {
                      if (isSelected) {
                        _selectedChallenges.remove(id);
                      } else {
                        _selectedChallenges.add(id);
                      }
                    });
                  },
                  child: Text(isSelected ? '선택됨' : '선택',
                      style: const TextStyle(fontSize: 16)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  // 챌린지 데이터 가져오기
  List<Map<String, dynamic>> _getChallenges() {
    return [
      {
        'id': 1,
        'icon': Icons.flash_on,
        'title': '물 1L 마시기, 커피 줄이기',
        'type': 'personal',
        'iconBgColor': const Color(0xFFE75C3C)
      },
      {
        'id': 2,
        'icon': Icons.flash_on,
        'title': '어크로 끌리는 체육 연구',
        'type': 'personal',
        'iconBgColor': const Color(0xFFE75C3C)
      },
      {
        'id': 3,
        'icon': Icons.flash_on,
        'title': '1일 1포스팅 및 핫게 댓글 달기',
        'type': 'personal',
        'iconBgColor': const Color(0xFFE75C3C)
      },
      {
        'id': 4,
        'icon': Icons.nature_people,
        'title': '저속노화 식단하기',
        'type': 'crew',
        'image': 'assets/images/health_food.png',
        'iconBgColor': const Color(0xFF3F51B5)
      },
      {
        'id': 5,
        'icon': Icons.nature_people,
        'title': '저속노화에 대한 포스팅 올리기',
        'type': 'crew',
        'image': 'assets/images/health_post.png',
        'iconBgColor': const Color(0xFF3F51B5)
      },
      {
        'id': 6,
        'icon': Icons.directions_run,
        'title': '15분 페이스 3k 달리기',
        'type': 'crew',
        'image': 'assets/images/running.png',
        'iconBgColor': const Color(0xFF00BCD4)
      },
      {
        'id': 7,
        'icon': Icons.directions_run,
        'title': '마라톤 같이 할 러너 구하기',
        'type': 'crew',
        'image': 'assets/images/running_friends.png',
        'iconBgColor': const Color(0xFF00BCD4)
      },
    ];
  }
}
