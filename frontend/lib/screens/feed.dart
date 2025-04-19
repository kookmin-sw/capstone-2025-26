import 'package:flutter/material.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
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
  @override
  Widget build(BuildContext context) {
    return Container(
      child: Column(
        children: [
          Row(
            children: [

            ],
          ), // 탭 메뉴. 고정 필요?
          Container(
            padding: EdgeInsets.all(10),
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
                          content: "모두를 위한 머신러닝 읽기"
                      ),
                      CustomListitem(
                          height: 46,
                          content: "모두를 위한 머신러닝 읽기"
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
