import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/routes.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/widgets/crewList.dart';
import 'package:reme/widgets/customListItem.dart';
import 'package:reme/widgets/widgetBox.dart';

class Home extends StatefulWidget {
  final VoidCallback? onCrewMoreTap;
  const Home({super.key, this.onCrewMoreTap});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
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
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 414.w,
      padding: const EdgeInsets.fromLTRB(0, 15, 0, 20),
      child: Column(
        children: [
          SizedBox(
            height: 150.h,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: 3,
              itemBuilder: (context, index) {
                return Container(
                  width: 150.r,
                  height: 150.r,
                  margin: EdgeInsets.only(
                    left: index == 0 ? 24.w : 0,
                    right: index == 2 ? 24.w : 10.w,
                  ),
                  padding: EdgeInsets.fromLTRB(11.w, 8.h, 10.w, 10.h),
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
                );
              },
            ),
          ),
          SizedBox(
            height: 15.h,
          ),
          GestureDetector(
            child: Container(
              width: 372.w,
              height: 65.h,
              margin: EdgeInsets.only(left: 24.w, right: 24.w),
              decoration: BoxDecoration(
                color: c900,
                borderRadius: BorderRadius.circular(10.r),
              ),
              child: Center(
                child: Text(
                  "오늘 회고하러 하기",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: fontColor,
                    fontSize: 20.sp,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
            onTap: () {
              Navigator.pushNamed(context, Routes.retrospectChallenge);
            },
          ),
          SizedBox(
            height: 15.h,
          ),
          WidgetBox(
            height: 225.h,
            title: "오늘의 개인 챌린지",
            isMore: false,
            marginLTRB: EdgeInsets.only(left: 24.w, right: 24.w),
            children: [
              CustomListitem(height: 46.h, content: "모두를 위한 머신러닝 읽기"),
              CustomListitem(height: 46.h, content: "모두를 위한 머신러닝 읽기"),
              CustomListitem(height: 46.h, content: "모두를 위한 머신러닝 읽기"),
            ],
          ),
          SizedBox(
            height: 15.h,
          ),
          WidgetBox(
            title: "내 크루",
            isMore: true,
            marginLTRB: EdgeInsets.only(left: 24.w, right: 24.w),
            onTap: widget.onCrewMoreTap,
            children: [
              SizedBox(
                height: 10.h,
              ),
              CrewList(
                crewName: "캡스톤 26조 파이팅",
                crewIntro: "크루에 대한 설명칸. 길어진다면 다음과 같이 마무리 하는게 좋을거 같긴 한데",
              ),
              SizedBox(
                height: 15.h,
              ),
              CrewList(
                crewName: "은성 캉의 영어 회화 교실",
                crewIntro: "크루에 대한 설명칸. 길어진다면 다음과 같이 마무리 하는게 좋을거 같긴 한데",
              ),
              SizedBox(
                height: 15.h,
              ),
              CrewList(
                crewName: "정릉동 우주최강 조깅 모임",
                crewIntro: "크루에 대한 설명칸. 길어진다면 다음과 같이 마무리 하는게 좋을거 같긴 한데",
              ),
            ],
          )
        ],
      ),
    );
  }
}
