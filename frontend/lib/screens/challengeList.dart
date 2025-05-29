import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/routes.dart';
import 'package:get/get.dart';
import 'package:logger/logger.dart';
import 'package:reme/services/challenge_api.dart';

class ChallengeList extends StatefulWidget {
  const ChallengeList({super.key});

  @override
  State<ChallengeList> createState() => _ChallengeListState();
}

class _ChallengeListState extends State<ChallengeList> {
  final _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 0,
      errorMethodCount: 5,
      lineLength: 50,
      colors: true,
      printEmojis: true,
      printTime: true,
    ),
  );
  final _challengeApi = ChallengeApi();
  // 현재 선택된 카테고리 (0: 전체, 1: 개인, 2: 크루)
  int _selectedCategory = 0;
  List<Map<String, dynamic>> _challenges = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchChallenges();
  }

  Future<void> _fetchChallenges() async {
    setState(() {
      _isLoading = true;
    });
    try {
      final response = await _challengeApi.getChallenges();

      // _logger.i('API 응답 상태 코드: ${response.statusCode}');
      // _logger.i('API 응답 데이터: ${response.data}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseBody =
            response.data as Map<String, dynamic>;

        if (responseBody.containsKey('results') &&
            responseBody['results'] is List) {
          final List<dynamic> challengesFromServer =
              responseBody['results'] as List<dynamic>;

          // .map의 결과를 List<Map<String, dynamic>>으로 명확히 하기 위한 처리
          final List<Map<String, dynamic>> processedChallenges =
              challengesFromServer
                  .map<Map<String, dynamic>>((challenge) {
                    // map의 반환 타입을 명시적으로 지정
                    if (challenge is Map<String, dynamic>) {
                      // 반환되는 맵의 키가 String이고 값이 dynamic임을 보장
                      return <String, dynamic>{
                        // 리터럴 맵에도 타입 명시
                        'id': challenge['id'],
                        'icon': Icons.flash_on,
                        'title': challenge['challenge_name'] ?? '이름 없음',
                        'type': challenge['owner_type'] == 'USER'
                            ? 'personal'
                            : 'crew',
                        'iconBgColor': const Color(0xFFE75C3C)
                      };
                    }
                    // 조건에 맞지 않는 경우 빈 Map<String, dynamic> 반환 또는 필터링
                    // 여기서는 필터링을 위해 null을 반환하고 나중에 제거하는 방식을 사용할 수도 있습니다.
                    // 또는 로깅 후 빈 맵 반환
                    _logger.w('올바르지 않은 챌린지 데이터 형식: $challenge');
                    return <String, dynamic>{}; // 빈 맵도 타입 명시
                  })
                  .where((challengeMap) => challengeMap
                      .containsKey('id')) // 유효한 챌린지만 필터링 (id가 있는 경우)
                  .toList(); // 최종적으로 List<Map<String, dynamic>> 타입이 됨

          setState(() {
            _challenges = processedChallenges; // 이제 타입이 일치함
            _isLoading = false;
          });
        } else {
          throw Exception("챌린지 목록 데이터 형식이 올바르지 않습니다. 'results' 키를 확인하세요.");
        }
      } else {
        throw Exception('챌린지 목록을 불러오는데 실패했습니다. 상태 코드: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _logger.e('챌린지 목록을 불러오는 중 오류가 발생했습니다: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('챌린지 목록을 불러오는 중 오류가 발생했습니다.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

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
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final filteredChallenges = type == 'all'
        ? _challenges
        : _challenges.where((c) => c['type'] == type).toList();

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
}
