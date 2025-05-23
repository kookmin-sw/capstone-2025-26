import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';

class CrewAdminPage extends StatefulWidget {
  const CrewAdminPage({super.key});

  @override
  State<CrewAdminPage> createState() => _CrewAdminPageState();
}

class _CrewAdminPageState extends State<CrewAdminPage> {
  final int pendingMemberCount = 3;
  final int alreadyMemberCount = 10;

  bool joinCrewHeaderPinned = true;
  late final ScrollController _scrollController;

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _scrollController = ScrollController();
  }

  @override
  Widget build(BuildContext context) {
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
          padding: EdgeInsets.symmetric(horizontal: 21.w),
          decoration: BoxDecoration(
            color: Color(0xFF111111),
          ),
          child: ListView(
            controller: _scrollController,
            children: [
              Container(
                height: 106.h,
                color: Color(0xFF111111),
                alignment: Alignment.centerLeft,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "가입신청",
                      style: TextStyle(
                        color: fontColor,
                        fontSize: 24.sp,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    Row(
                      children: [
                        Spacer(),
                        Container(
                          height: 30.h,
                          margin: EdgeInsets.only(top: 5.h),
                          child: ElevatedButton(
                            onPressed: () {},
                            child: Text(
                              "모두 승인",
                              style: TextStyle(
                                color: fontColor,
                                fontSize: 16.sp,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: c900,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10.r),
                              ),
                            ),
                          ),
                        ),
                      ],
                    )
                  ],
                ),
              ),
              SizedBox(height: 10.h),
              ...List.generate(
                  pendingMemberCount, (index) => _buildPendingMember(index)),
              Container(
                height: 50.h,
                color: Color(0xFF111111),
                alignment: Alignment.centerLeft,
                child: Text(
                  "크루 멤버",
                  style: TextStyle(
                    color: fontColor,
                    fontSize: 24.sp,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              SizedBox(height: 10.h),
              ...List.generate(
                  alreadyMemberCount, (index) => _buildAlreadyMember(index)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPendingMember(int index) {
    return Container(
      margin: EdgeInsets.only(bottom: 15.h),
      //padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 10.h),
      padding: EdgeInsets.only(left: 11.w, top: 10.h, bottom: 10.h),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: Row(
        children: [
          Image(
            image: Svg('assets/img/account_circle.svg'),
            width: 40.w,
            height: 40.h,
            color: c100,
          ),
          SizedBox(width: 16.w),
          Text(
            "롱기스트",
            style: TextStyle(
              color: fontColor,
              fontSize: 20.sp,
              fontWeight: FontWeight.w800,
            ),
          ),
          Spacer(),
          Container(
            width: 56.w,
            height: 30.h,
            child: GestureDetector(
              onTap: () {},
              child: Container(
                child: Center(
                  child: Text(
                    "거절",
                    style: TextStyle(
                      color: fontColor,
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10.r),
                  color: boxBackgroundColor,
                ),
              ),
            ),
          ),
          SizedBox(width: 4.w),
          GestureDetector(
            onTap: () {},
            child: Container(
              width: 56.w,
              height: 30.h,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10.r),
                color: c900,
              ),
              child: Center(
                child: Text(
                  "승인",
                  style: TextStyle(
                    color: fontColor,
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlreadyMember(int index) {
    return Container(
      margin: EdgeInsets.only(bottom: 15.h),
      padding: EdgeInsets.symmetric(horizontal: 11.w, vertical: 10.h),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10.r),
      ),
      child: Row(
        children: [
          Image(
            image: Svg('assets/img/account_circle.svg'),
            width: 40.w,
            height: 40.h,
            color: c100,
          ),
          SizedBox(width: 16.w),
          Text(
            "다욤둥",
            style: TextStyle(
              color: fontColor,
              fontSize: 20.sp,
              fontWeight: FontWeight.w800,
            ),
          ),
          Spacer(),
          Container(
            width: 96.w,
            height: 30.h,
            child: GestureDetector(
              onTap: () {},
              child: Container(
                child: Center(
                  child: Text(
                    "내보내기",
                    style: TextStyle(
                      color: fontColor,
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10.r),
                  color: c900,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
