import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/screens/get_info.dart';
import 'package:reme/themes/color.dart';

class AccountInfoPage extends StatefulWidget {
  final String username;
  AccountInfoPage({super.key, required this.username});

  @override
  State<AccountInfoPage> createState() => _AccountInfoPageState();
}

class _AccountInfoPageState extends State<AccountInfoPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        leading: IconButton(
          onPressed: () {
            Navigator.pop(context);
          },
          icon: Icon(
            Icons.arrow_back_ios,
            color: fontColor,
          ),
        ),
        title: Text.rich(
          TextSpan(
            style: TextStyle(
              fontSize: 19.sp,
              fontWeight: FontWeight.w800,
            ),
            children: [
              TextSpan(
                text: widget.username,
                style: TextStyle(
                  color: c800,
                ),
              ),
              TextSpan(
                text: "님의 정보",
                style: TextStyle(
                  color: fontColor,
                ),
              )
            ],
          ),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          children: [
            SizedBox(height: 32.h),
            GestureDetector(
              onTap: () {
                // Todo: 변경할 이미지 선택하는 화면.
                print("프로필 이미지 클릭");
              },
              child: Container(
                width: 120.w,
                height: 120.h,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10.r),
                ),
                child: Image.asset(
                  'assets/img/food.png',
                  fit: BoxFit.fill,
                ),
              ),
            ),
            SizedBox(height: 35.h),
            GestureDetector(
              onTap: () {
                showDialog(
                    context: context,
                    builder: (context) => Dialog(
                          child: GetInfo(type: 1, content: widget.username),
                        ));
              },
              child: Padding(
                padding: EdgeInsets.only(left: 21.w, right: 21.w),
                child: _buildInfo("닉네임", widget.username),
              ),
            ),
            SizedBox(height: 29.h),
            GestureDetector(
              onTap: () {
                showDialog(
                    context: context,
                    builder: (context) => Dialog(
                          child: GetInfo(type: 2, content: "email@example.com"),
                        ));
              },
              child: Padding(
                padding: EdgeInsets.only(left: 21.w, right: 21.w),
                child: _buildInfo("이메일", "email@example.com"),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfo(String title, String content) {
    return Row(
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 17.sp,
            color: Color(0xFFC3C3C3),
            fontWeight: FontWeight.w400,
            height: 1.5,
          ),
        ),
        Spacer(),
        Text(
          content,
          style: TextStyle(
            fontSize: 17.sp,
            color: Color(0xFFC3C3C3),
            fontWeight: FontWeight.w400,
          ),
        ),
        SizedBox(width: 10.w),
        Icon(Icons.arrow_forward_ios, color: Color(0xFFC3C3C3), size: 17.sp),
      ],
    );
  }
}
