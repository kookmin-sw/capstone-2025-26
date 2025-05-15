import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/widgets/categoryButton.dart';

class NotificationListPage extends StatefulWidget {
  const NotificationListPage({super.key});

  @override
  State<NotificationListPage> createState() => _NotificationListPageState();
}

class _NotificationListPageState extends State<NotificationListPage> {
  int selectedIndex = 0;

  // 임시 데이터
  List<int> notificationCategory = [3, 1, 2, 3];
  List<String> notificationContent = [
    "OOO가 팔로우 하기 시작했어요",
    "오늘 회고 내용 분석이 완료되었어요!",
    "(크루명)가입이 승인되었어요~",
    "OOO가 좋아요를 눌렀어요!",
  ];
  List<Image?> notificationImage = [
    Image(image: Svg('assets/img/account_circle.svg')),
    null,
    Image.asset('assets/img/running.png'),
    Image(image: Svg('assets/img/account_circle.svg')),
  ];
  List<DateTime> notificationDate = [
    DateTime.now().subtract(Duration(days: 1)),
    DateTime.now().subtract(Duration(days: 3)),
    DateTime.now().subtract(Duration(days: 4)),
    DateTime.now().subtract(Duration(days: 5)),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: background,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_new),
          color: Colors.white,
          onPressed: () {
            Navigator.pop(context);
          },
        ),
        title: Text(
          "알림",
          style: TextStyle(
            color: Colors.white,
            fontSize: 24.sp,
            fontWeight: FontWeight.w700,
          ),
        ),
        bottom: PreferredSize(
          preferredSize: Size.fromHeight(55.h),
          child: Padding(
            padding: EdgeInsets.only(left: 21.w, right: 21.w),
            child: Row(
              children: [
                CategoryButton(
                  height: 34.28.h,
                  text: "전체",
                  index: 0,
                  onTap: () {
                    setState(() {
                      selectedIndex = 0;
                    });
                  },
                  isSelected: (selectedIndex == 0),
                ),
                SizedBox(width: 10.w),
                CategoryButton(
                  height: 34.28.h,
                  text: "회고",
                  index: 1,
                  onTap: () {
                    setState(() {
                      selectedIndex = 1;
                    });
                  },
                  isSelected: (selectedIndex == 1),
                ),
                SizedBox(width: 10.w),
                CategoryButton(
                  height: 34.28.h,
                  text: "크루",
                  index: 2,
                  onTap: () {
                    setState(() {
                      selectedIndex = 2;
                    });
                  },
                  isSelected: (selectedIndex == 2),
                ),
                SizedBox(width: 10.w),
                CategoryButton(
                  height: 34.28.h,
                  text: "커뮤니티",
                  index: 3,
                  onTap: () {
                    setState(() {
                      selectedIndex = 3;
                    });
                  },
                  isSelected: (selectedIndex == 3),
                ),
              ],
            ),
          ),
        ),
        centerTitle: false,
      ),
      body: Padding(
        padding: EdgeInsets.only(left: 21.w, right: 21.w),
        child: Column(
          children: [
            SizedBox(height: 15.h),
            Flexible(
              child: ListView.builder(
                itemCount: notificationCategory.length,
                itemBuilder: (context, index) {
                  if (selectedIndex == 0 ||
                      selectedIndex == notificationCategory[index]) {
                    return Container(
                      height: 70.h,
                      margin: EdgeInsets.only(bottom: 10.h),
                      padding: EdgeInsets.symmetric(
                          horizontal: 15.w, vertical: 10.h),
                      decoration: BoxDecoration(
                        color: boxBackgroundColor,
                        borderRadius: BorderRadius.circular(10.r),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 40.w,
                            height: 40.h,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                            ),
                            child: (notificationCategory[index] == 1)
                                ? Icon(Icons.article, color: Color(0xFF2196F3))
                                : notificationImage[
                                    index], // 크루프로필사진 or 상대프로필사진
                          ),
                          SizedBox(width: 15.w),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Row(
                                  children: [
                                    Text(
                                      notificationCategory[index] == 1
                                          ? "회고"
                                          : notificationCategory[index] == 2
                                              ? "크루"
                                              : "커뮤니티",
                                      style: TextStyle(
                                        fontSize: 12.sp,
                                        color: fontColor,
                                      ),
                                    ),
                                    SizedBox(width: 10.w),
                                    Text(
                                      _getTimeAgo(notificationDate[index]),
                                      style: TextStyle(
                                        fontSize: 10.sp,
                                        color: Colors.grey,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ),
                                SizedBox(height: 4.h),
                                Text(
                                  notificationContent[index],
                                  style: TextStyle(
                                    fontSize: 16.sp,
                                    fontWeight: FontWeight.w500,
                                    color: fontColor,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  }
                  return Container(height: 0);
                },
              ),
            )
          ],
        ),
      ),
    );
  }

  String _getTimeAgo(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays >= 5) {
      return '${date.month}월 ${date.day}일';
    } else if (difference.inDays > 0) {
      return '${difference.inDays}일 전';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}시간 전';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}분 전';
    } else {
      return '방금 전';
    }
  }
}
