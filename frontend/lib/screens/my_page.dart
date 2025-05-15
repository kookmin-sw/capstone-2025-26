import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/screens/account_info_page.dart';
import 'package:reme/screens/get_info.dart';
import 'package:reme/screens/guidePage.dart';
import 'package:reme/screens/retrospect_completion_screen.dart';
import 'package:reme/themes/color.dart';

class MyPage extends StatelessWidget {
  const MyPage({super.key});

  @override
  Widget build(BuildContext context) {
    var userName = ModalRoute.of(context)!.settings.arguments;
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
          backgroundColor: background,
          elevation: 0,
          leading: IconButton(
            onPressed: () {
              Navigator.pop(context);
            },
            icon: Icon(Icons.arrow_back_ios_new),
            color: Colors.white,
          )),
      body: Center(
        child: Column(
          children: [
            SizedBox(height: 32.h),
            Text.rich(
              TextSpan(
                style: TextStyle(
                  fontSize: 27.sp,
                  letterSpacing: 0.54,
                  fontWeight: FontWeight.w800,
                ),
                children: [
                  TextSpan(
                    text: userName.toString(),
                    style: TextStyle(
                      color: c600,
                    ),
                  ),
                  TextSpan(
                    text: "님\n환영합니다 👀",
                    style: TextStyle(
                      color: fontColor,
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: 55.h),
            Row(children: [
              GestureDetector(
                onTap: () {
                  showDialog(
                      context: context,
                      builder: (context) {
                        return Dialog(
                          child: GetInfo(type: 0),
                        );
                      });
                },
                child: Container(
                  width: 112.w,
                  height: 112.h,
                  margin: EdgeInsets.only(left: 18.w),
                  decoration: BoxDecoration(
                    color: boxBackgroundColor,
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Center(
                        child: Image(
                          image: Svg('assets/img/my_interest.svg'),
                          width: 64.w,
                          height: 64.h,
                        ),
                      ),
                      Center(
                        child: Text(
                          "내 관심사",
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: fontColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              GestureDetector(
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) =>
                              AccountInfoPage(username: userName.toString())));
                },
                child: Container(
                  width: 112.w,
                  height: 112.h,
                  margin: EdgeInsets.only(left: 18.w),
                  decoration: BoxDecoration(
                    color: boxBackgroundColor,
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Center(
                        child: Image(
                          image: Svg('assets/img/account_info.svg'),
                          width: 64.w,
                          height: 64.h,
                        ),
                      ),
                      Center(
                        child: Text(
                          "계정 정보",
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: fontColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              Container(
                width: 112.h,
                height: 112.h,
              )
            ]),
            SizedBox(height: 18.h),
            Row(children: [
              GestureDetector(
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => GuidePage(fromMyPage: true)));
                },
                child: Container(
                  width: 112.w,
                  height: 112.h,
                  margin: EdgeInsets.only(left: 18.w),
                  decoration: BoxDecoration(
                    color: boxBackgroundColor,
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Center(
                        child: Image(
                          image: Svg(
                            'assets/img/info_circle.svg',
                            size: Size(60.w, 60.h),
                            scale: 6,
                          ),
                          color: c600,
                        ),
                      ),
                      Center(
                        child: Text(
                          "가이드",
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: fontColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              GestureDetector(
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => ReflectionAnalysisScreen(
                                fromMyPage: true,
                              )));
                },
                child: Container(
                  width: 112.w,
                  height: 112.h,
                  margin: EdgeInsets.only(left: 18.w),
                  decoration: BoxDecoration(
                    color: boxBackgroundColor,
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Center(
                        child: Image(
                          image: Svg(
                            'assets/img/retrospect_content.svg',
                            size: Size(60.w, 60.h),
                            scale: 6,
                          ),
                          color: c600,
                        ),
                      ),
                      Center(
                        child: Text(
                          "회고 내용",
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: fontColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              GestureDetector(
                onTap: () {
                  showDialog(
                      context: context,
                      builder: (context) {
                        return Dialog(
                          child: GetInfo(type: 3),
                        );
                      });
                },
                child: Container(
                  width: 112.w,
                  height: 112.h,
                  margin: EdgeInsets.only(left: 18.w),
                  decoration: BoxDecoration(
                    color: boxBackgroundColor,
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Center(
                        child: Image(
                          image: Svg(
                            'assets/img/qna_icon.svg',
                            size: Size(58.w, 58.h),
                            scale: 6,
                          ),
                          color: c600,
                        ),
                      ),
                      Center(
                        child: Text(
                          "문의하기",
                          style: TextStyle(
                            fontSize: 14.sp,
                            color: fontColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ])
          ],
        ),
      ),
    );
  }
}
