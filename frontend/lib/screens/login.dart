import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:get/get.dart';
import 'package:reme/models/user_info.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/socialLoginWebView.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/user_info_controller.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LoginPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    Get.put(UserInfoController());
    return Scaffold(
        backgroundColor: background,
        body: Container(
          margin: EdgeInsets.only(left: 21.w, top: 97.h),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "의미 없는 하루는 없다",
                style: TextStyle(
                  fontSize: 24.sp,
                  fontWeight: FontWeight.w500,
                  color: fontColor,
                  letterSpacing: 0.02,
                ),
              ),
              SizedBox(
                height: 1.5.h,
              ),
              Row(
                children: [
                  Text(
                    "더 나은 내일을 위한 회고 ",
                    style: TextStyle(
                      fontSize: 24.sp,
                      fontWeight: FontWeight.w700,
                      color: fontColor,
                      letterSpacing: 0.02,
                    ),
                  ),
                  Text(
                    "To-Go",
                    style: TextStyle(
                      fontSize: 24.sp,
                      fontWeight: FontWeight.w700,
                      color: c600,
                      letterSpacing: 0.02,
                    ),
                  )
                ],
              ),
              SizedBox(height: 56.h),
              Image.asset(width: 385.w, 'assets/img/character.png'),
              SizedBox(
                height: 45.h,
              ),
              GestureDetector(
                onTap: () => _login(context, "kakao"),
                child: SvgPicture.asset(
                  'assets/img/kakao_login.svg',
                  width: 372.w,
                  height: 56.h,
                ),
              ),
              SizedBox(height: 14.h),
              GestureDetector(
                onTap: () => _login(context, "naver"),
                child: Image.asset(
                  'assets/img/naver_login.png',
                  width: 372.w,
                ),
              ),
              SizedBox(
                height: 50.h,
              ),
              Container(
                margin: EdgeInsets.only(left: 67.w),
                child: RichText(
                  textAlign: TextAlign.center,
                  text: TextSpan(
                    style: TextStyle(
                      color: Color(0xFF505050),
                      fontSize: 13.sp,
                      fontWeight: FontWeight.w400,
                      height: 1.5,
                      letterSpacing: 0.01,
                    ),
                    children: [
                      TextSpan(text: "인증 진행 시 "),
                      TextSpan(
                        text: "이용약관",
                        style: TextStyle(
                          decoration: TextDecoration.underline,
                        ),
                        recognizer: TapGestureRecognizer()
                          ..onTap = () {
                            print("이용약관 클릭");
                          },
                      ),
                      TextSpan(text: " 및 "),
                      TextSpan(
                        text: "개인정보 처리 방침",
                        style: TextStyle(
                          decoration: TextDecoration.underline,
                        ),
                        recognizer: TapGestureRecognizer()
                          ..onTap = () {
                            print("개인정보 처리 방침 클릭");
                          },
                      ),
                      TextSpan(text: "에\n동의하는 것으로 간주합니다"),
                    ],
                  ),
                ),
              )
            ],
          ),
        ));
  }

  void _login(BuildContext context, String provider) {
    Navigator.push(
            context,
            MaterialPageRoute(
                builder: (context) => SocialLoginWebView(social: provider)))
        .then((data) async {
      // 데이터가 넘어오지 않을 때 1초간 SnackBar 띄움.
      if (data != null && data.runtimeType == UserInfo) {
        // data가 null이 아니고 Tokens 타입일 때
        final prefs = await SharedPreferences.getInstance();
        prefs.setBool("logined", true);
        const storage =
            FlutterSecureStorage(); // accessToken과 refreshToken을 저장하는 SecrueStorage
        await storage.write(key: 'AccessToken', value: data.accessToken);
        await storage.write(key: 'RefreshToken', value: data.refreshToken);
        await storage.write(key: 'Id', value: data.id);
        Get.find<UserInfoController>()
            .setUserInfo(data.id, data.userName, data.email, data.profileImage);

        if (data.needSignup == true) {
          // 사용자 명이 없을 때 회원가입 페이지로 이동.
          Navigator.pushNamed(context, Routes.signup, arguments: data);
        } else {
          // username이 있으면 flutter_secure_storage에 저장 후 메인페이지로 이동.
          await storage.write(key: 'UserName', value: data.userName);
          Navigator.pushNamedAndRemoveUntil(
              context, Routes.splash, (route) => false);
        }
      } else {
        // Toast Message
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Login Canceled or Failed"),
          duration: Duration(seconds: 1),
        ));
      }
    });
  }
}
