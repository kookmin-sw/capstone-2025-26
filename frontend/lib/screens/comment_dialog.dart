import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/screens/crewDetail.dart';
import 'package:reme/themes/color.dart';

class CommentDialog extends StatefulWidget {
  final String postId;
  const CommentDialog({super.key, required this.postId});

  @override
  State<CommentDialog> createState() => _CommentDialogState();
}

class _CommentDialogState extends State<CommentDialog> {
  final TextEditingController _commentController = TextEditingController();
  @override
  Widget build(BuildContext context) {
    return Container(
      color: background,
      width: MediaQuery.of(context).size.width,
      height: MediaQuery.of(context).size.height * 0.8,
      child: Column(
        children: [
          PostCard(
            nickname: "다욤둥",
            date: "25.04.12",
            title: "다음주까지 식단 짜서 올려주세요",
            content: "저속 노화 유튜브 영상 보고 \n최대한 건강하게 식단 짜서 공유 부탁드립니다 \n게시글로 남겨주세요!",
            isComment: true,
          ),
          Container(
            height: 1,
            decoration: const BoxDecoration(
                gradient: LinearGradient(
                    begin: Alignment.centerLeft,
                    end: Alignment.centerRight,
                    colors: [
                  Color(0xFF1C1B20),
                  Color(0xFF2C2C34),
                  Color(0xFF1C1B20),
                ])),
          ),
          SizedBox(height: 10.h),
          Expanded(
            child: ListView.builder(
              itemCount: 3,
              itemBuilder: (context, index) {
                return CommentCard(
                  username: "롱기스트",
                  date: "25.04.13",
                  content: "알겠습니다. 내일까지 업로드하겠습니다.",
                );
              },
            ),
          ),
          Padding(
            padding: EdgeInsets.all(16.w),
            child: TextField(
              controller: _commentController,
              style: TextStyle(
                color: fontColor,
                fontSize: 14.sp,
              ),
              decoration: InputDecoration(
                suffixIcon: GestureDetector(
                    onTap: () {
                      print(_commentController.text);
                      _commentController.clear();
                    },
                    child: Icon(Icons.send)),
                suffixIconColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10.r),
                  borderSide: BorderSide(color: c800),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10.r),
                  borderSide: BorderSide(color: c800),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10.r),
                  borderSide: BorderSide(color: c800),
                ),
                filled: true,
                fillColor: boxBackgroundColor,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class CommentCard extends StatelessWidget {
  final String username;
  final String date;
  final String content;
  const CommentCard(
      {super.key,
      required this.username,
      required this.date,
      required this.content});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: boxBackgroundColor,
      padding: EdgeInsets.symmetric(horizontal: 10.w, vertical: 5.h),
      margin: EdgeInsets.only(bottom: 10.h),
      child: Row(
        children: [
          Image(
            image: Svg('assets/img/account_circle.svg'),
            width: 40.w,
            height: 40.w,
            color: c100,
          ),
          SizedBox(width: 12.w),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    username,
                    style: TextStyle(
                        fontSize: 14.sp,
                        fontWeight: FontWeight.w800,
                        color: fontColor),
                  ),
                  SizedBox(width: 12.w),
                  Text(
                    date,
                    style: TextStyle(
                        fontSize: 12.sp,
                        fontWeight: FontWeight.w400,
                        color: grey),
                  )
                ],
              ),
              Text(content,
                  style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w500,
                      color: fontColor))
            ],
          )
        ],
      ),
    );
  }
}
