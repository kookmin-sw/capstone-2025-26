import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/routes.dart';
import 'package:get/get.dart';

class ChallengeList extends StatefulWidget {
  const ChallengeList({super.key});

  @override
  State<ChallengeList> createState() => _ChallengeListState();
}

class _ChallengeListState extends State<ChallengeList> {
  // 현재 선택된 카테고리 (0: 전체, 1: 개인, 2: 크루)
  int _selectedCategory = 0;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.maxFinite,
      height: 630.h,
      child: Stack(
        children: [
          Column(
            children: [
              // 카테고리 버튼 모음
              Padding(
                padding: const EdgeInsets.fromLTRB(21.0, 10.0, 30.0, 5.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _buildCategoryButton("전체", 0, height: 25),
                    const SizedBox(width: 15),
                    _buildCategoryButton("개인", 1, height: 25),
                    const SizedBox(width: 15),
                    _buildCategoryButton("크루", 2, height: 25),
                  ],
                ),
              ),

              // 챌린지 리스트
              _buildChallengeList(
                  type: _selectedCategory == 0
                      ? 'all'
                      : _selectedCategory == 1
                          ? 'personal'
                          : 'crew'),
            ],
          ),
          Positioned(
            left: 0,
            right: 0,
            bottom: 14.h,
            child: GestureDetector(
              onTap: () {
                print("챌린지 추가하기 버튼 누름");
                Get.toNamed(Routes.createChallengeName);
              },
              child: Center(
                child: Container(
                  padding: EdgeInsets.only(bottom: 10.h),
                  decoration: const BoxDecoration(
                    color: background,
                  ),
                  child: Container(
                    width: 372.w,
                    height: 38.h,
                    decoration: BoxDecoration(
                      color: c900,
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: Center(
                      child: Text(
                        "챌린지 추가하기",
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 16.sp,
                          fontWeight: FontWeight.w500,
                          color: fontColor,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
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
              isSelected ? const Color(0xFF1C398E) : boxBackgroundColor,
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

    return SizedBox(
      height: 500.h,
      child: SingleChildScrollView(
        child: Column(
          children: filteredChallenges.map((challenge) {
            final hasImage = challenge.containsKey('image');

            return Padding(
              padding:
                  const EdgeInsets.symmetric(vertical: 8.0, horizontal: 21.0),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
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
                                return Icon(
                                  challenge['icon'] as IconData,
                                  color: Colors.white,
                                  size: 20,
                                );
                              },
                            ),
                          )
                        : Icon(
                            challenge['icon'] as IconData,
                            color: Colors.white,
                            size: 20,
                          ),
                  ),
                  const SizedBox(width: 15),
                  Expanded(
                    child: Text(
                      challenge['title'] as String,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
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
        'title': '어그로 끌리는 체육 연구',
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
