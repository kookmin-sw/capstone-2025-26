import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';

class GetInfo extends StatelessWidget {
  final int type; // 정보 입력 타임 (관심사(0), 닉네임(1), 이메일(2), 문의하기(3))
  const GetInfo({super.key, required this.type});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: MediaQuery.of(context).size.width * 0.9,
      height: 400.h,
      padding: EdgeInsets.all(30.r),
      decoration: BoxDecoration(
        color: Color(0xFF111111),
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (type == 0)
              Text.rich(
                TextSpan(
                  children: [
                    TextSpan(
                      text: "나의 관심사를 작성해주세요!\n",
                      style: TextStyle(
                        fontSize: 20.sp,
                        fontWeight: FontWeight.w800,
                        color: fontColor,
                      ),
                    ),
                    TextSpan(
                      text: "적어주신 관심사를 기반으로 추천 챌린지를 생성해드려요~",
                      style: TextStyle(
                        fontSize: 14.sp,
                        fontWeight: FontWeight.w400,
                        color: fontColor,
                      ),
                    ),
                  ],
                ),
              ),
            if (type == 1)
              Text(
                "사용할 닉네임을 입력해주세요!",
                style: TextStyle(
                  fontSize: 20.sp,
                  fontWeight: FontWeight.w800,
                  color: fontColor,
                ),
              ),
            if (type == 2)
              Text(
                "사용할 이메일을 입력해주세요!",
                style: TextStyle(
                  fontSize: 20.sp,
                  fontWeight: FontWeight.w800,
                  color: fontColor,
                ),
              ),
            if (type == 3)
              Text(
                "문의하실 내용을 입력해주세요!",
                style: TextStyle(
                  fontSize: 20.sp,
                  fontWeight: FontWeight.w800,
                  color: fontColor,
                ),
              ),
            SizedBox(
              height: 29.h,
            ),
            TextFormField(
              minLines: 1,
              maxLines: type == 0 || type == 3 ? 6 : 1,
              decoration: InputDecoration(
                labelText: type == 0
                    ? "관심사"
                    : type == 1
                        ? "닉네임"
                        : type == 2
                            ? "이메일"
                            : "문의하실 내용",
                labelStyle: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.w400,
                  color: fontColor,
                ),
                focusColor: c800,
                enabledBorder: UnderlineInputBorder(
                  borderSide: BorderSide(color: c800, width: 2.0),
                ),
                focusedBorder: UnderlineInputBorder(
                  borderSide: BorderSide(color: c800, width: 2.0),
                ),
              ),
              style: TextStyle(
                color: fontColor,
              ),
              cursorColor: c800,
            ),
            Spacer(),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                    },
                    child: Text("취소"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: boxBackgroundColor,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                SizedBox(width: 10.w),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      // TODO: type별로 서버로 보내는 방식 다르게 설정
                    },
                    child: Text("확인"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: c900,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
