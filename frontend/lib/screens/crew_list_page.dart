import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import 'package:reme/services/crew_api.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/crew_controller.dart';
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
  bool joinCrewHeaderPinned = true;

  late final ScrollController _scrollController;

  final crewController = Get.put(CrewController());
  Widget _buildJoinedCrew(int index) {
    return Container(
      margin: EdgeInsets.only(bottom: 15.h),
      padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 10.h),
      decoration: BoxDecoration(
        color: boxBackgroundColor,
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: CrewList(
          crewId: crewController.joinedCrew[index]['id'],
          crewName: crewController.joinedCrew[index]['crew_name'],
          crewIntro: crewController.joinedCrew[index]['crew_description'],
          image: crewController.joinedCrew[index]['crew_image'] != null
              ? NetworkImage(crewController.joinedCrew[index]['crew_image'])
              : null,
          isJoined: true,
          afterCardClicked: () {
            setState(() {});
          }),
    );
  }

  Widget _buildNonJoinedCrew(int index) {
    dynamic crew_id = crewController.notJoinedCrew[index]['id'];
    return Container(
      margin: EdgeInsets.only(bottom: 15.h),
      padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 10.h),
      decoration: BoxDecoration(
        color: boxBackgroundColor,
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: CrewList(
          crewId: crewController.notJoinedCrew[index]['id'],
          crewName: crewController.notJoinedCrew[index]['crew_name'],
          crewIntro: crewController.notJoinedCrew[index]['crew_description'],
          isJoined: false,
          onJoinTap: () {
            joinCrew(crewController.notJoinedCrew[index]['id'].toString());
            getMyCrewMembership().then((value) {
              crewController.setMyCrewMembership(value.data);
            });
            print("아이디: ${crewController.notJoinedCrew[index]['id']} 크루 가입");
          },
          joinClicked: (crewController.myCrewMembership[crew_id]?['status'] ==
              "PENDING"),
          image: crewController.notJoinedCrew[index]['crew_image'] != null
              ? NetworkImage(crewController.notJoinedCrew[index]['crew_image'])
              : null,
          afterCardClicked: () {
            setState(() {});
          }),
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
          (boxHeight + boxPadding + bottomMargin) *
              crewController.joinedCrew.length;

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
      child: Obx(() => CustomScrollView(
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
                    childCount: crewController.joinedCrew.length,
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
                    childCount: crewController.notJoinedCrew.length,
                  ),
                ),
              ),
            ],
          )),
    );
  }
}
