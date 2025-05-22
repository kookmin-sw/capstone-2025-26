import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import 'package:reme/screens/get_info.dart';
import 'package:reme/services/user_update.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/user_info_controller.dart';

class AccountInfoPage extends StatefulWidget {
  AccountInfoPage({
    super.key,
  });

  @override
  State<AccountInfoPage> createState() => _AccountInfoPageState();
}

class _AccountInfoPageState extends State<AccountInfoPage> {
  final UserInfoController userController = Get.find<UserInfoController>();

  @override
  void initState() {
    super.initState();
  }

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
        title: Obx(() => Text.rich(
              TextSpan(
                style: TextStyle(
                  fontSize: 19.sp,
                  fontWeight: FontWeight.w800,
                ),
                children: [
                  TextSpan(
                    text: userController.userInfo['username'],
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
            )),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          children: [
            SizedBox(height: 32.h),
            GestureDetector(
              onTap: () {
                XFile? image;
                ImagePicker()
                    .pickImage(source: ImageSource.gallery)
                    .then((pickedFile) {
                  if (pickedFile != null) {
                    // 이미지를 선택했다면?
                    image = pickedFile;
                    print(pickedFile.path);
                    updateUser(
                            id: userController.userInfo['id'],
                            profile_image: File(pickedFile.path))
                        .then((value) {
                      print("upload 완료 후 리턴 값 $value");
                      userController.updateUserInfo(
                          'profile_image', value.data['profile_image']);
                    });
                  }
                });
              },
              child: Container(
                width: 120.w,
                height: 120.h,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(30.r),
                ),
                child: Obx(() => CircleAvatar(
                      backgroundImage:
                          userController.userInfo['profile_image'] != null
                              ? NetworkImage(
                                  userController.userInfo['profile_image'])
                              : Svg('assets/img/account_circle.svg'),
                    )),
              ),
            ),
            SizedBox(height: 35.h),
            GestureDetector(
              onTap: () {
                showDialog(
                    context: context,
                    builder: (context) => Dialog(
                          child: GetInfo(
                              type: 1,
                              content: userController.userInfo['username']),
                        )).then((value) {
                  userController.getUserInfo();
                });
              },
              child: Padding(
                padding: EdgeInsets.only(left: 21.w, right: 21.w),
                child: Obx(() =>
                    _buildInfo("닉네임", userController.userInfo['username'])),
              ),
            ),
            SizedBox(height: 29.h),
            GestureDetector(
              onTap: () {
                showDialog(
                    context: context,
                    builder: (context) => Dialog(
                          child: GetInfo(
                              type: 2,
                              content: userController.userInfo['email']),
                        )).then((value) {
                  userController.getUserInfo();
                });
              },
              child: Padding(
                padding: EdgeInsets.only(left: 21.w, right: 21.w),
                child: Obx(
                    () => _buildInfo("이메일", userController.userInfo['email'])),
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
