import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/routes.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/iconToImage.dart';
import 'package:reme/widgets/challengeTypeItem.dart';
import 'package:reme/widgets/crewBox.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:reme/screens/retrospect_completion_screen.dart';

class RetroPage extends StatefulWidget {
  const RetroPage({super.key});

  @override
  State<RetroPage> createState() => _RetroPageState();
}

class _RetroPageState extends State<RetroPage>
    with SingleTickerProviderStateMixin {
  ImageProvider? plusIcon;
  late TabController _tabController;
  int _selectedIndex = 0;
  DateTime _focusedDay = DateTime.now();
  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    // TODO: implement dispose
    super.dispose();
    _tabController.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TableCalendar(
          headerStyle: HeaderStyle(
            titleCentered: true,
            titleTextStyle: TextStyle(
              fontSize: 20.sp,
              fontWeight: FontWeight.w600,
              color: fontColor,
            ),
            leftChevronIcon: Icon(
              Icons.chevron_left,
              color: fontColor,
            ),
            rightChevronIcon: Icon(
              Icons.chevron_right,
              color: fontColor,
            ),
          ),
          calendarStyle: const CalendarStyle(
            defaultTextStyle: TextStyle(color: fontColor),
            // weekend
            weekendTextStyle: TextStyle(color: Colors.red),
            weekendDecoration: BoxDecoration(
              color: Colors.transparent,
              shape: BoxShape.circle,
            ),
            // selected
            selectedDecoration: BoxDecoration(
              color: c700,
              shape: BoxShape.circle,
            ),
            // today
            todayDecoration: BoxDecoration(
              color: Colors.transparent,
              shape: BoxShape.circle,
            ),
          ),
          locale: "ko_KR",
          focusedDay: _focusedDay,
          firstDay: DateTime(2025, 01, 01),
          lastDay: DateTime(2030, 12, 31),
          availableCalendarFormats: {
            CalendarFormat.month: "월",
          },
          selectedDayPredicate: (day) {
            return isSameDay(_focusedDay, day);
          },
          onDaySelected: (selectedDay, focusedDay) {
            setState(() {
              _focusedDay = focusedDay;
            });
          },
          onPageChanged: (focusedDay) {
            setState(() {
              _focusedDay = focusedDay;
            });
          },
        ),
        Container(
          margin: EdgeInsets.symmetric(horizontal: 20.w),
          child: Container(
            height: 1,
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.centerLeft,
                end: Alignment.centerRight,
                colors: [
                  Color(0xFF1C1B20),
                  Color(0xFF2C2C34),
                  Color(0xFF1C1B20),
                ],
              ),
            ),
          ),
        ),
        Container(
          height: 300.h,
          child: Stack(
            children: [
              SingleChildScrollView(
                child: Column(
                  children: [
                    ChallengeTypeItem(
                      title: "1일 1포스팅 및 핫게 댓글 달기",
                      description:
                          "오늘 성공적으로 포스팅을 업로드 했어요! 지금 사회 이슈를 다루어 좋은 반응을 보였다니 축하해요!",
                      score: 90,
                      hasSuccess: true,
                      imagePath: 'assets/img/lightning.png',
                    ),
                    ChallengeTypeItem(
                      title: "저속노화 식단하기",
                      description: "오늘은 저속노화 식단을 하지 않았어요. 내일은 꼭 한번 도전해 봐요",
                      score: 0,
                      hasSuccess: false,
                      imagePath: 'assets/img/food.png',
                    ),
                    ChallengeTypeItem(
                      title: "15분 페이스 3k 달리기",
                      description: "오늘은 3k 달리기를 20분 페이스에 달렸어요. 조금만 더 빨리 뛰어봐요",
                      score: 60,
                      hasSuccess: false,
                      imagePath: 'assets/img/running.png',
                    ),
                    SizedBox(
                      height: 38.h,
                    )
                  ],
                ),
              ),
              Positioned(
                left: 21.w,
                bottom: 0,
                child: GestureDetector(
                  onTap: () {
                    Navigator.pushNamed(context, Routes.retrospectChallenge);
                  },
                  child: Center(
                    child: Container(
                      width: 372.w,
                      height: 38.h,
                      decoration: BoxDecoration(
                        color: c900,
                        borderRadius: BorderRadius.circular(8.r),
                      ),
                      child: Center(
                        child: Text(
                          "오늘 회고 시작하기",
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
              )
            ],
          ),
        ),
      ],
    );
  }
}
