import 'package:flutter/material.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/widgets/boxUserInfo.dart';
import 'package:reme/widgets/customListItem.dart';
import 'package:reme/widgets/widgetBox.dart';

class Feed extends StatefulWidget {
  const Feed({super.key});

  @override
  State<Feed> createState() => _FeedState();
}

class _FeedState extends State<Feed> {
  bool isTotal = true; // 전체인지 팔로우인지 판단하는 변수
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(10),
      child: Column(
        children: [
          Row(
            spacing: 10,
            children: [
              GestureDetector(
                onTap: (){
                  setState(() {
                    isTotal = true;
                  });
                },
                child: Container(
                  padding: EdgeInsets.fromLTRB(30, 6, 30, 6),
                  decoration: ShapeDecoration(
                    color: (isTotal)? c900: boxBackgroundColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                  ),
                  child: Text(
                    "전체 보기",
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w500,
                      color: fontColor
                    ),
                  ),
                ),
              ),
              GestureDetector(
                onTap: (){
                  setState(() {
                    isTotal = false;
                  });
                },
                child: Container(
                  padding: EdgeInsets.fromLTRB(30, 6, 30, 6),
                  decoration: ShapeDecoration(
                    color: (!isTotal)? c900: boxBackgroundColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                  ),
                  child: Text(
                    "팔로우",
                    style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w500,
                        color: fontColor
                    ),
                  ),
                ),
              ),
              Spacer(),
              Icon(
                TabBarIcon.search,
                size: 27,
                color: fontColor,
              )
            ],
          ), // 탭 메뉴. 고정 필요?
          Container(
            padding: EdgeInsets.only(top: 10),
            child: Column(
              children: [
                WidgetBox(
                    children: [
                      // 사용자 프로필사진, 이름, 팔로우 버튼 여기에
                      BoxUserInfo(
                        name: "웅성웅성",
                      ),
                      CustomListitem(
                          height: 46,
                          content: "모두를 위한 머신러닝 읽기"
                      ),
                      CustomListitem(
                          height: 46,
                          content: "매일 조깅하기"
                      ),
                      CustomListitem(
                          height: 46,
                          content: "용기내 챌린지하기"
                      ),
                      Container(
                        padding: EdgeInsets.fromLTRB(10, 17, 0, 0),
                        child: Row(
                          spacing: 14,
                          children: [
                            Icon(TabBarIcon.heart, color: fontColor, size: 20,),
                            Icon(TabBarIcon.comment, color: fontColor, size: 20,)
                          ],
                        ),
                      )
                    ],
                    isMore: false,
                    marginLTRB: EdgeInsets.only(bottom: 10)
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
