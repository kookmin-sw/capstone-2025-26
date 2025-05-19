import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';
import 'package:table_calendar/table_calendar.dart';

class RetrospectDetail extends StatefulWidget {
  const RetrospectDetail({super.key});

  @override
  State<RetrospectDetail> createState() => _RetrospectDetailState();
}

class _RetrospectDetailState extends State<RetrospectDetail> {
  List<String> _challengeList = [
    "물 1L 마시기, 커피 줄이기",
    "어그로 끌리는 제목 연구",
    "1일 1포스팅 및 핫게 댓글달기",
  ];
  late String selectedChallenge;

  int _stepCount = 3; // 회고 단계 수

  List<String> _stepList = [
    "Keep, 지속하고 싶은 내용을 적어주세요",
    "Problem, 어떤 문제가 있었나요?",
    "Try, 문제를 어떻게 개선해볼까요?",
  ];

  List<String> _stepContentList = [
    "물을 평소보다 많이 마셨다. 기존에 커피 5잔씩 마시던 것을 3잔으로 줄였다",
    "친구랑 카페를 갔을 때 습관적으로 아이스 아메리카노를 눌러 결제를 해버렸다.",
    "카페에 가서도 의식적으로 커피가 아닌 음료를 마시고 텀블러를 들고 다니면서 많은 물을 마셔야 겠다."
  ];

  DateTime _focusedDay = DateTime.now();

  @override
  void initState() {
    super.initState();
    selectedChallenge = _challengeList[0];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: background,
        title: Row(
          children: [
            Image(
              image: Svg('assets/img/account_circle.svg'),
              width: 37.w,
              height: 37.h,
              color: c100,
            ),
            SizedBox(width: 10.w),
            Text.rich(
              style: TextStyle(
                fontSize: 18.sp,
                fontWeight: FontWeight.w800,
              ),
              TextSpan(
                children: [
                  TextSpan(text: "웅성웅성 ", style: TextStyle(color: c600)),
                  TextSpan(
                      text: "님의 회고 기록", style: TextStyle(color: fontColor)),
                ],
              ),
            )
          ],
        ),
        leading: IconButton(
          onPressed: () {
            Navigator.pop(context);
          },
          icon: Icon(
            Icons.arrow_back_ios_new,
            color: fontColor,
          ),
        ),
      ),
      body: SafeArea(
        child: Container(
          padding: EdgeInsets.symmetric(horizontal: 21.w),
          child: Column(
            children: [
              Row(
                children: [
                  Container(
                    width: 40.w,
                    height: 40.h,
                    decoration: BoxDecoration(
                      color: boxBackgroundColor,
                      borderRadius: BorderRadius.circular(10.r),
                    ),
                    child: Image(
                      image: AssetImage('assets/img/lightning.png'),
                    ),
                  ),
                  SizedBox(width: 10.w),
                  DropdownButton(
                    dropdownColor: boxBackgroundColor,
                    style: TextStyle(
                      color: fontColor,
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w500,
                    ),
                    items: _challengeList
                        .map((e) => DropdownMenuItem(
                              value: e,
                              child: Text(e),
                            ))
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedChallenge = value!;
                      });
                    },
                    value: selectedChallenge,
                    underline: Container(),
                    icon: Icon(
                      Icons.keyboard_arrow_down_outlined,
                      color: fontColor,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 10.h),
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
                  formatButtonVisible: false,
                ),
                calendarFormat: CalendarFormat.week,
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
              SizedBox(height: 10.h),
              Expanded(
                child: ListView.builder(
                  itemCount: _stepCount,
                  itemBuilder: (context, index) {
                    return _buildStep(index);
                  },
                ),
              )
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStep(int step) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 21.w, vertical: 16.h),
      margin: EdgeInsets.only(bottom: 10.h),
      decoration: BoxDecoration(
        color: boxBackgroundColor,
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _stepList[step],
            style: TextStyle(
              color: fontColor,
              fontSize: 21.sp,
              fontWeight: FontWeight.w700,
            ),
          ),
          SizedBox(height: 4.h),
          Text(
            _stepContentList[step],
            style: TextStyle(
              color: Color(0xFFD6D6D6),
              fontSize: 16.sp,
              fontWeight: FontWeight.w400,
            ),
          )
        ],
      ),
    );
  }
}
