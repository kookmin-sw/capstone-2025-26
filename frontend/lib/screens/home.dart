import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import 'package:reme/routes.dart';
import 'package:reme/services/user_update.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/challenge_controller.dart';
import 'package:reme/utils/crew_controller.dart';
import 'package:reme/widgets/crewList.dart';
import 'package:reme/widgets/customListItem.dart';
import 'package:reme/widgets/widgetBox.dart';

class Home extends StatefulWidget {
  final VoidCallback? onCrewMoreTap;
  final VoidCallback? switchToRetrospect;
  const Home({super.key, this.onCrewMoreTap, this.switchToRetrospect});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  dynamic challengeList;
  dynamic joinedCrewList;
  final crewController = Get.put(CrewController());
  final challengeController = Get.put(ChallengeController());
  List<String> topBoxTitle = ["연속 32일째!", "오늘의 탬플릿", "크루를 찾아봐요"];
  List<String> topBoxContent = [
    "오늘도 함꼐 \n회고해요😉",
    "오늘 KPT로 \n회고 어때요?",
    "같은 목표를 가진\n사람들과 함께해요!"
  ];
  List<Image> topBoxImage = [
    Image.asset(
      "assets/img/3d_fire.png",
      width: 52.w,
      height: 67.h,
    ),
    Image.asset(
      "assets/img/3d_calendar.png",
      width: 52.w,
      height: 67.h,
    ),
    Image.asset(
      "assets/img/3d_glassMagnifier.png",
      width: 43.w,
      height: 57.h,
    ),
  ];
  late List<VoidCallback?> topBoxTap;

  @override
  void initState() {
    super.initState();
    challengeList = challengeController.challengeList;
    topBoxTap = [
      widget.switchToRetrospect, // 회고 목록 보는 페이지로 이동
      () {
        Navigator.pushNamed(context, Routes.retrospectChallenge);
      },
      widget.onCrewMoreTap, // 크루 페이지로 이동
    ];

    // 크루 목록이 있는지 확인하고 없다면 불러오기.
    joinedCrewList = crewController.getJoinedCrewList();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 414.w,
      padding: const EdgeInsets.fromLTRB(0, 15, 0, 20),
      margin: EdgeInsets.only(bottom: 80.h),
      child: Column(
        children: [
          SizedBox(
            height: 150.h,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: 3,
              itemBuilder: (context, index) {
                return GestureDetector(
                  onTap: topBoxTap[index],
                  child: Container(
                    width: 150.w,
                    height: 150.h,
                    margin: EdgeInsets.only(
                      left: index == 0 ? 24.w : 0,
                      right: index == 2 ? 24.w : 10.w,
                    ),
                    padding: EdgeInsets.fromLTRB(9.w, 7.h, 10.w, 10.h),
                    decoration: BoxDecoration(
                      color: boxBackgroundColor,
                      borderRadius: BorderRadius.circular(10.r),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          topBoxTitle[index],
                          style: TextStyle(
                            fontSize: 20.sp,
                            fontWeight: FontWeight.w700,
                            color: fontColor,
                          ),
                        ),
                        SizedBox(
                          width: double.maxFinite,
                          height: 100.h,
                          child: Stack(
                            children: [
                              Text(
                                topBoxContent[index],
                                style: TextStyle(
                                  fontSize: 16.sp,
                                  fontWeight: FontWeight.w600,
                                  color: fontColor,
                                ),
                              ),
                              Positioned(
                                bottom: 0,
                                right: 0,
                                child: topBoxImage[index],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          SizedBox(
            height: 15.h,
          ),
          WidgetBox(
            title: "오늘의 개인 챌린지",
            isMore: false,
            marginLTRB: EdgeInsets.only(left: 24.w, right: 24.w),
            children: [
              if (challengeController.challengeList != null &&
                  challengeController.challengeList.length == 0)
                Text(
                  "개인 챌린지가 없어요",
                  style: TextStyle(
                    fontSize: 26.sp,
                    fontWeight: FontWeight.w300,
                    color: fontColor,
                  ),
                )
              else if (challengeController.challengeList != null &&
                  challengeController.challengeList.length > 0)
                for (var i = 0;
                    i < challengeController.challengeList.length;
                    i++)
                  if (challengeController.challengeList[i]['owner_type'] ==
                      "USER")
                    GestureDetector(
                        onTap: () {
                          // TODO: 챌린지 상세 조회 페이지로 이동
                        },
                        child: CustomListitem(
                            height: 46.h,
                            content: challengeController.challengeList[i]
                                ['challenge_name'])),
            ],
          ),
          SizedBox(
            height: 15.h,
          ),
          WidgetBox(
            title: "내 크루",
            isMore: (joinedCrewList != null && joinedCrewList.length > 3)
                ? true
                : false,
            marginLTRB: EdgeInsets.only(left: 24.w, right: 24.w),
            onTap: widget.onCrewMoreTap,
            children: [
              SizedBox(
                height: 10.h,
              ),
              if (joinedCrewList != null && joinedCrewList.length > 0)
                for (var i = 0;
                    i < (joinedCrewList.length > 3 ? 3 : joinedCrewList.length);
                    i++)
                  Container(
                    margin: EdgeInsets.only(bottom: 10.h),
                    child: GestureDetector(
                      onTap: () {
                        Navigator.pushNamed(context, Routes.crew,
                            arguments: joinedCrewList[i]['id']);
                      },
                      child: CrewList(
                        crewId: joinedCrewList[i]['id'],
                        crewName: joinedCrewList[i]['crew_name'],
                        crewIntro: joinedCrewList[i]['crew_description'],
                        image: (joinedCrewList[i]['crew_image'] != null)
                            ? NetworkImage(joinedCrewList[i]['crew_image'])
                            : null,
                      ),
                    ),
                  )
              else
                Text(
                  "크루에 참여하세요",
                  style: TextStyle(
                    fontSize: 26.sp,
                    fontWeight: FontWeight.w300,
                    color: fontColor,
                  ),
                )
            ],
          )
        ],
      ),
    );
  }
}
