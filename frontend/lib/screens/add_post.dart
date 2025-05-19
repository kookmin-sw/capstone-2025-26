import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';

class AddPost extends StatelessWidget {
  AddPost({super.key});

  final TextEditingController titleController = TextEditingController();
  final TextEditingController contentController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    var type = ModalRoute.of(context)!.settings.arguments;
    return Scaffold(
      backgroundColor: background,
      resizeToAvoidBottomInset: true,
      appBar: AppBar(
        backgroundColor: background,
        scrolledUnderElevation: 0,
        title: Row(
          children: [
            Image.asset('assets/img/food.png', width: 37.w, height: 37.h),
            SizedBox(width: 10.w),
            Text(
              "저속노화 따라가기",
              style: TextStyle(
                fontSize: 19.sp,
                color: fontColor,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
        leading: IconButton(
            onPressed: () {
              Navigator.pop(context);
            },
            icon: Icon(
              Icons.arrow_back_ios_new,
              color: fontColor,
            )),
      ),
      body: SafeArea(
        child: Container(
          padding: EdgeInsets.symmetric(horizontal: 21.w, vertical: 10.h),
          child: Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      TextFormField(
                        controller: titleController,
                        style: TextStyle(
                          color: fontColor,
                        ),
                        decoration: InputDecoration(
                          labelText: "제목",
                          labelStyle: TextStyle(
                            color: fontColor,
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide: BorderSide(color: c700),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide: BorderSide(color: c700),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide: BorderSide(color: c700),
                          ),
                        ),
                      ),
                      SizedBox(height: 20.h),
                      TextFormField(
                        controller: contentController,
                        maxLines: 20,
                        style: TextStyle(
                          color: fontColor,
                        ),
                        decoration: InputDecoration(
                          labelText: "내용",
                          labelStyle: TextStyle(
                            color: fontColor,
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide: BorderSide(color: c700),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide: BorderSide(color: c700),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                            borderSide: BorderSide(color: c700),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              Container(
                margin: EdgeInsets.only(top: 10.h, bottom: 10.h),
                child: Center(
                  child: Row(
                    children: [
                      Container(
                        width: 174.w,
                        margin: EdgeInsets.only(right: 10.w),
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.pop(context);
                          },
                          child: Text(
                            "취소",
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: boxBackgroundColor,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                        ),
                      ),
                      Container(
                        width: 174.w,
                        child: ElevatedButton(
                          onPressed: () {
                            // TODO: 게시글 저장하기 위한 백엔드 코드 연결
                            print(type);
                          },
                          child: Text(
                            "완료",
                            style: TextStyle(
                              color: fontColor,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: c800,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
