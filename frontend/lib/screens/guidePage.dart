import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:introduction_screen/introduction_screen.dart';
import 'package:reme/routes.dart';
import 'package:reme/themes/color.dart';
import 'package:shared_preferences/shared_preferences.dart';

class GuidePage extends StatefulWidget {
  const GuidePage({super.key});

  @override
  State<GuidePage> createState() => _GuidePageState();
}

class _GuidePageState extends State<GuidePage> {
  final introKey = GlobalKey<IntroductionScreenState>();
  int _currentPage = 0;
  final int _lastPage = 2; // 페이지 개수 - 1

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IntroductionScreen(
        key: introKey,
        globalBackgroundColor: c950,
        bodyPadding: EdgeInsets.only(bottom: 26.h),
        pages: [_FirstPage(), _FirstPage(), _FirstPage()],
        showNextButton: false,
        showDoneButton: false,
        showSkipButton: false,
        controlsPadding: EdgeInsets.zero,
        dotsDecorator: DotsDecorator(
          activeColor: Colors.transparent,
          color: Colors.transparent,
          size: Size(0, 0),
          activeSize: Size(0, 0),
          spacing: EdgeInsets.zero,
        ),
        onChange: (idx) => setState(() => _currentPage = idx),
        globalFooter: Container(
          color: c950,
          padding: EdgeInsets.only(
              bottom: 30.3.h, left: 20.w, right: 20.w, top: 10.h),
          child: _currentPage == _lastPage
              ? Center(
                  child: SizedBox(
                    width: double.infinity,
                    child: TextButton(
                      style: TextButton.styleFrom(
                          padding: EdgeInsets.only(bottom: 10.h)),
                      onPressed: () async {
                        SharedPreferences prefs =
                            await SharedPreferences.getInstance();
                        prefs.setBool("first_install", true);
                        Navigator.pushReplacementNamed(context, Routes.login);
                      },
                      child: Text("시작하기",
                          style: TextStyle(
                              color: fontColor,
                              fontSize: 16.sp,
                              fontWeight: FontWeight.w600)),
                    ),
                  ),
                )
              : Container(
                  width: double.maxFinite,
                  margin: EdgeInsets.only(bottom: 7.h),
                  padding: EdgeInsets.only(left: 21.w),
                  child: Center(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.start,
                      children: [
                        (_currentPage == 0)
                            ? Container(
                                width: 115.w,
                                padding:
                                    EdgeInsets.fromLTRB(8.r, 8.r, 10.r, 12.r),
                                child: GestureDetector(
                                  onTap: () async {
                                    SharedPreferences prefs =
                                        await SharedPreferences.getInstance();
                                    prefs.setBool("logined", true);
                                    Navigator.pushReplacementNamed(
                                        context, Routes.login);
                                  },
                                  child: Text("건너뛰기",
                                      style: TextStyle(
                                          color: fontColor,
                                          fontSize: 16.sp,
                                          letterSpacing: 0.02)),
                                ),
                              )
                            : Container(
                                width: 115.w,
                                padding:
                                    EdgeInsets.fromLTRB(23.r, 8.r, 10.r, 12.r),
                                child: GestureDetector(
                                  onTap: () async {
                                    introKey.currentState?.previous();
                                  },
                                  child: Text("이전",
                                      style: TextStyle(
                                          color: fontColor,
                                          fontSize: 16.sp,
                                          letterSpacing: 0.02)),
                                ),
                              ),
                        SizedBox(
                          width: 21.w,
                        ),
                        Container(
                          margin: EdgeInsets.only(right: 20.w, bottom: 5.h),
                          child: Row(
                            children: List.generate(
                                3,
                                (idx) => Container(
                                      margin:
                                          EdgeInsets.symmetric(horizontal: 4),
                                      width: 10,
                                      height: 10,
                                      decoration: BoxDecoration(
                                        color: _currentPage == idx
                                            ? Colors.white
                                            : Colors.white30,
                                        shape: BoxShape.circle,
                                      ),
                                    )),
                          ),
                        ),
                        SizedBox(
                          width: 53.w,
                        ),
                        Container(
                          padding: EdgeInsets.fromLTRB(10.r, 8.r, 10.r, 12.r),
                          child: GestureDetector(
                            onTap: () {
                              introKey.currentState?.next();
                            },
                            child: Text("다음",
                                style: TextStyle(
                                    color: fontColor, fontSize: 16.sp)),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
        ),
      ),
    );
  }

  PageViewModel _FirstPage() {
    return PageViewModel(
        titleWidget: Align(
          alignment: Alignment.topLeft,
          child: Container(
            width: 300.w,
            margin: EdgeInsets.only(top: 63.h, left: 3.w),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "내가 찾던 동아리가 한 곳에.",
                  style: TextStyle(
                      color: fontColor,
                      fontSize: 24.sp,
                      fontWeight: FontWeight.w600),
                ),
                SizedBox(height: 15.h),
                Text(
                  "지역별, 학교별, 관심사별로\n다양한 주제의 동아리를 쉽게 탐색할 수 있어요.",
                  style: TextStyle(
                      color: fontColor,
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w400,
                      letterSpacing: 0.02),
                )
              ],
            ),
          ),
        ),
        bodyWidget: SizedBox.shrink(),
        decoration: PageDecoration(pageColor: background));
  }
}
