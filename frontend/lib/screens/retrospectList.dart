import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import 'package:reme/routes.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/retrospect_controller.dart';
import 'package:reme/widgets/challengeTypeItem.dart';
import 'package:table_calendar/table_calendar.dart';

class RetroSpectList extends StatefulWidget {
  const RetroSpectList({super.key});

  @override
  State<RetroSpectList> createState() => _RetroSpectListState();
}

class _RetroSpectListState extends State<RetroSpectList> {
  DateTime _focusedDay = DateTime.now();
  final RetrospectController retrospectController =
      Get.put(RetrospectController());

  // 날짜별로 한 번만 표시되는 Map 만들기
  Map<DateTime, List> getEventMap(List retrospectList) {
    final Map<DateTime, List> eventMap = {};
    for (var item in retrospectList) {
      final date = DateTime.parse(item['created_at'].split('T')[0]);
      final day = DateTime(date.year, date.month, date.day);
      eventMap[day] = [true]; // 여러개여도 그냥 하나만 넣음
    }
    return eventMap;
  }

  @override
  Widget build(BuildContext context) {
    final eventMap = getEventMap(retrospectController.retrospectList);
    final todayList = retrospectController.retrospectList
        .where((item) =>
            item['created_at'].split('T')[0] ==
            _focusedDay.toString().split(' ')[0])
        .toList();
    return SafeArea(
      child: Column(
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
            eventLoader: (day) {
              final d = DateTime(day.year, day.month, day.day);
              return eventMap[d] ?? [];
            },
            calendarBuilders: CalendarBuilders(
              markerBuilder: (context, day, events) {
                if (events.isNotEmpty) {
                  return Positioned(
                    bottom: 1,
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: Colors.blue, // 점 색상
                        shape: BoxShape.circle,
                      ),
                    ),
                  );
                }
                return null;
              },
            ),
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
            child: Column(
              children: [
                Flexible(
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        if (todayList.isEmpty)
                          Padding(
                            padding: EdgeInsets.symmetric(vertical: 32.h),
                            child: Text(
                              "오늘 진행한 회고가 없습니다",
                              style: TextStyle(
                                color: fontColor,
                                fontSize: 24.sp,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          )
                        else
                          ...todayList.map((item) => ChallengeTypeItem(
                                title: "챌린지 이름",
                                description: item['comment'],
                                score: item['score'] * 100,
                                hasSuccess: true,
                                imagePath: 'assets/img/lightning.png',
                              )),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          GestureDetector(
            onTap: () {
              Navigator.pushNamed(context, Routes.retrospectChallenge);
            },
            child: Center(
              child: Container(
                decoration: BoxDecoration(
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
          ),
        ],
      ),
    );
  }
}
