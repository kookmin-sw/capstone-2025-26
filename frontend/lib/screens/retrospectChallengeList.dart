import 'package:flutter/material.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/screens/retrospect_method_selection.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/services/challenge_api.dart';
import 'package:reme/models/retrospect_challenge_model.dart';
import 'package:logger/logger.dart';

class RetrospectChallengeList extends StatefulWidget {
  int? crewId;
  RetrospectChallengeList({super.key, this.crewId});

  @override
  State<RetrospectChallengeList> createState() =>
      _RetrospectChallengeListState();
}

class _RetrospectChallengeListState extends State<RetrospectChallengeList> {
  final _challengeApi = ChallengeApi();
  final _logger = Logger();

  // 선택된 챌린지
  final Set<int> _selectedChallenges = {};

  // 현재 선택된 카테고리 (0: 전체, 1: 개인, 2: 크루)

  int _selectedCategory = 0;

  // API에서 가져온 챌린지 데이터
  List<Map<String, dynamic>> _allChallenges = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchRetrospectChallenges();
  }

  /// 회고할 챌린지 목록 API에서 가져오기
  Future<void> _fetchRetrospectChallenges() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await _challengeApi.getChallenges();

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseBody =
            response.data as Map<String, dynamic>;

        if (responseBody.containsKey('results') &&
            responseBody['results'] is List) {
          final List<dynamic> challengesFromServer =
              responseBody['results'] as List<dynamic>;

          final List<Map<String, dynamic>> processedChallenges =
              challengesFromServer
                  .map<Map<String, dynamic>>((challenge) {
                    if (challenge is Map<String, dynamic>) {
                      return <String, dynamic>{
                        'id': challenge['id'],
                        'icon': Icons.flash_on, // 기본 아이콘
                        'title': challenge['challenge_name'] ?? '이름 없음',
                        'type': challenge['owner_type'] == 'USER'
                            ? 'personal'
                            : 'crew',
                        'iconBgColor': challenge['owner_type'] == 'USER'
                            ? const Color(0xFFE75C3C)
                            : const Color(0xFF3F51B5),
                        'status': challenge['status'] ?? 'ACTIVE',
                        'description': challenge['description'],
                        'created_at': challenge['created_at'],
                        // 원본 데이터도 저장
                        'original_data': challenge,
                      };
                    }
                    return <String, dynamic>{};
                  })
                  .where((challengeMap) => challengeMap.containsKey('id'))
                  .toList();

          setState(() {
            _allChallenges = processedChallenges;
            _isLoading = false;
          });

          _logger.i('회고 챌린지 ${_allChallenges.length}개 로드됨');
        }
      } else {
        throw Exception('서버 응답 오류: ${response.statusCode}');
      }
    } catch (e) {
      _logger.e('회고 챌린지 조회 실패: $e');
      setState(() {
        _errorMessage = '챌린지 목록을 불러오는데 실패했습니다: $e';
        _isLoading = false;
      });
    }
  }

  /// 새로고침
  Future<void> _onRefresh() async {
    await _fetchRetrospectChallenges();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: background,
        elevation: 0,
        centerTitle: false,
        title: null,
        toolbarHeight: 40,
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
      body: Column(
        children: [
          // 타이틀 텍스트
          const Padding(
            padding: EdgeInsets.fromLTRB(21.0, 0.0, 16.0, 15.0),
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
                  SizedBox(height: 2),
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

          // 카테고리 버튼 모음
          Padding(
            padding: const EdgeInsets.fromLTRB(21.0, 0.0, 30.0, 5.0),
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
            // 선택한 챌린지들 가져오기
            final List<Map<String, dynamic>> selectedChallenges = [];
            for (var id in _selectedChallenges) {
              final challenge = _allChallenges.firstWhere((c) => c['id'] == id);
              selectedChallenges.add(challenge);
            }

            if (selectedChallenges.isEmpty) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('최소 하나 이상의 챌린지를 선택해주세요'),
                  duration: Duration(seconds: 1),
                ),
              );
              return;
            }

            // Navigate to the retrospective method selection screen
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => RetrospectMethodSelection(
                  selectedChallenges: selectedChallenges,
                  retrospectType: widget.crewId == null ? "COMMON" : "CREW",
                  crewId: widget.crewId,
                ),
              ),
            );
          },
          child: Container(
            height: 60,
            decoration: BoxDecoration(
              color: const Color(0xFF1C398E),
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
            // 카테고리 변경 시 선택된 챌린지 초기화
            _selectedChallenges.clear();
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
      return const Center(
        child: CircularProgressIndicator(color: c900),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: const TextStyle(
                color: fontColor,
                fontSize: 16,
                fontFamily: 'Pretendard',
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _fetchRetrospectChallenges,
              style: ElevatedButton.styleFrom(
                backgroundColor: c900,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                '다시 시도',
                style: TextStyle(
                  color: Colors.white,
                  fontFamily: 'Pretendard',
                ),
              ),
            ),
          ],
        ),
      );
    }

    if (_allChallenges.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.assignment_outlined,
              size: 64,
              color: greyColor,
            ),
            SizedBox(height: 16),
            Text(
              '회고할 챌린지가 없습니다',
              style: TextStyle(
                color: fontColor,
                fontSize: 18,
                fontWeight: FontWeight.w600,
                fontFamily: 'Pretendard',
              ),
            ),
          ],
        ),
      );
    }

    // API 데이터 사용
    final filteredChallenges = _getFilteredChallenges();

    return ListView.builder(
      padding: const EdgeInsets.only(top: 12.0, bottom: 60.0),
      itemCount: filteredChallenges.length + 1,
      itemBuilder: (context, index) {
        // 마지막 아이템인 경우 모두 선택 버튼 표시
        if (index == filteredChallenges.length) {
          return Padding(
            padding:
                const EdgeInsets.symmetric(vertical: 20.0, horizontal: 16.0),
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
                      borderRadius: BorderRadius.circular(10),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                  ),
                  onPressed: () {
                    setState(() {
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
          padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 21.0),
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
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      challenge['title'] as String,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(
                height: 34,
                width: 65,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: isSelected
                        ? const Color(0xFF1C398E)
                        : boxBackgroundColor,
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
                  child: Text(isSelected ? '회고' : '선택',
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
  List<Map<String, dynamic>> _getFilteredChallenges() {
    final type = _selectedCategory == 0
        ? 'all'
        : _selectedCategory == 1
            ? 'personal'
            : 'crew';

    return type == 'all'
        ? _allChallenges
        : _allChallenges.where((c) => c['type'] == type).toList();
  }
}
