import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/widgets/crewList.dart';

class CrewListPage extends StatefulWidget {
  const CrewListPage({super.key});

  @override
  State<CrewListPage> createState() => _CrewListPageState();
}

class _HeaderDelegate extends SliverPersistentHeaderDelegate {
  final String title;
  final double height;

  _HeaderDelegate({required this.title, required this.height});

  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: const Color(0xFF111111),
      height: height,
      alignment: Alignment.centerLeft,
      child: Text(
        title,
        style: TextStyle(
          color: fontColor,
          fontSize: 24.sp,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  @override
  double get maxExtent => height;

  @override
  double get minExtent => height;

  @override
  bool shouldRebuild(_HeaderDelegate oldDelegate) {
    return title != oldDelegate.title || height != oldDelegate.height;
  }
}

class _CrewListPageState extends State<CrewListPage> {
  final int joinedCrewCount = 3;
  final int notJoinedCrewCount = 20;

  bool joinCrewHeaderPinned = true;

  late final ScrollController _scrollController;

  Widget _buildJoinedCrew(int index) {
    final joinedCrews = [
      {
        'name': '캡스톤 26조 파이팅',
        'intro': '국민대학교 캡스톤 26조의 프로젝트를 위한 크루입니다. 회고를 통한 지속적인 개선과 성장을 목표로 합니다.',
      },
      {
        'name': '은성 캉의 영어 회화 교실',
        'intro':
            '원어민 강사와 함께하는 실전 영어 회화 스터디입니다. 매주 화, 목 저녁 7시에 진행되며, 다양한 주제로 자유로운 대화를 나눕니다.',
      },
      {
        'name': '정릉동 우주최강 조깅 모임',
        'intro':
            '정릉동 주변에서 함께 뛰는 조깅 모임입니다. 매일 아침 6시 정릉천에서 시작하며, 초보자부터 마라톤러까지 모두 환영합니다.',
      },
    ];

    return Container(
      margin: EdgeInsets.only(bottom: 15.h),
      padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 10.h),
      decoration: BoxDecoration(
        color: boxBackgroundColor,
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: CrewList(
        crewId: index,
        crewName: joinedCrews[index]['name']!,
        crewIntro: joinedCrews[index]['intro']!,
        isJoined: true,
      ),
    );
  }

  Widget _buildNonJoinedCrew(int index) {
    return Container(
      margin: EdgeInsets.only(bottom: 15.h),
      padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 10.h),
      decoration: BoxDecoration(
        color: boxBackgroundColor,
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: CrewList(
        image: (index == 0) ? AssetImage('assets/img/food.png') : null,
        crewId: index,
        crewName: _getCrewData(index)['name'],
        crewIntro: _getCrewData(index)['intro'],
        isJoined: _getCrewData(index)['isJoined'],
        onJoinTap: () {
          print("$index번째 크루 가입");
        },
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
    _scrollController.addListener(() {
      // 크루 섹션 전환 위치 계산
      final double headerHeight = 50.h;
      final double bottomMargin = 15.h;
      final double boxHeight = 50.h;
      final double boxPadding = 10.h;

      // 가입한 크루 섹션의 총 높이
      final double joinedCrewSectionHeight = headerHeight +
          bottomMargin +
          (boxHeight + boxPadding + bottomMargin) * joinedCrewCount;

      // 현재 스크롤 위치가 가입한 크루 섹션을 넘어섰는지 확인
      final bool shouldUnpin =
          _scrollController.offset > joinedCrewSectionHeight;

      if (shouldUnpin != !joinCrewHeaderPinned) {
        setState(() {
          joinCrewHeaderPinned = !shouldUnpin;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 690.h,
      padding: EdgeInsets.symmetric(horizontal: 21.w),
      decoration: const BoxDecoration(
        color: Color(0xFF111111),
      ),
      child: CustomScrollView(
        controller: _scrollController,
        slivers: [
          SliverPersistentHeader(
            pinned: joinCrewHeaderPinned,
            delegate: _HeaderDelegate(
              title: "가입한 크루",
              height: 50.h,
            ),
          ),
          SliverPadding(
            padding: EdgeInsets.only(top: 10.h),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) => _buildJoinedCrew(index),
                childCount: joinedCrewCount,
              ),
            ),
          ),
          SliverPersistentHeader(
            pinned: true,
            delegate: _HeaderDelegate(
              title: "크루 찾아보기",
              height: 50.h,
            ),
          ),
          SliverPadding(
            padding: EdgeInsets.only(top: 10.h),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) => _buildNonJoinedCrew(index),
                childCount: notJoinedCrewCount,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Map<String, dynamic> _getCrewData(int index) {
    final crews = [
      {
        'name': '저속 노화 따라가기',
        'intro': '저속 노화 위주의 식사와 규칙적인 생활을 통해 삶을 재정비하고 이다현보다 오래 살기 위해 노력합니다.',
        'isJoined': false,
      },
      {
        'name': '서울대입구 러닝 크루',
        'intro': '서울대입구역 주변 러닝 크루입니다. 매주 화, 목 아침 6시 정릉천에서 함께 뛰어요! 초보자도 환영합니다.',
        'isJoined': false,
      },
      {
        'name': '건대 맛집 탐방단',
        'intro': '건대 맛집을 함께 탐방하고 리뷰를 작성하는 크루입니다. 주 1회 정기 모임과 맛집 투어를 진행합니다.',
        'isJoined': false,
      },
      {
        'name': '독서 토론 모임',
        'intro': '매주 한 권의 책을 읽고 토론하는 모임입니다. 다양한 분야의 책을 함께 읽으며 생각을 나눕니다.',
        'isJoined': false,
      },
      {
        'name': '코딩 스터디 그룹',
        'intro': '프로그래밍 학습과 프로젝트를 함께하는 스터디 그룹입니다. 주 2회 온라인 미팅과 코드 리뷰를 진행합니다.',
        'isJoined': false,
      },
      {
        'name': '요가 & 명상 클럽',
        'intro': '요가와 명상을 통해 마음의 평화를 찾는 모임입니다. 주말 정기 클래스와 명상 워크숍을 운영합니다.',
        'isJoined': false,
      },
      {
        'name': '영어 회화 스터디',
        'intro': '자연스러운 영어 회화 실력 향상을 위한 스터디입니다. 원어민 선생님과 함께하는 주 2회 수업을 진행합니다.',
        'isJoined': false,
      },
      {
        'name': '사진 동호회',
        'intro': '사진 촬영과 편집을 배우고 공유하는 동호회입니다. 정기적인 외부 촬영과 작품 전시회를 개최합니다.',
        'isJoined': false,
      },
    ];

    return crews[index % crews.length];
  }
}
