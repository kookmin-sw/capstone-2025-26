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
      color: Color(0xFF111111),
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
    return Container(
      margin: EdgeInsets.only(bottom: 15.h),
      padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 10.h),
      decoration: BoxDecoration(
        color: boxBackgroundColor,
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: CrewList(
        crewId: index,
        crewName: "캡스톤 26조 화이팅",
        crewIntro: "캡스톤 26조 화이팅을 위한 크루. 더 이상 어떤 말을 @해도 그 내용이 우리 크루를 설명할 수 없다.",
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
        crewId: index,
        crewName: "정릉동 건강인 모임",
        crewIntro: "정릉동 건강인 모임을 위한 크루. 더 이상 어떤 말을 해도 그 내용이 우리 크루를 설명할 수 없다.",
        isJoined: false,
        onJoinTap: () {
          print("${index}번째 크루 가입");
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
      decoration: BoxDecoration(
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
}
