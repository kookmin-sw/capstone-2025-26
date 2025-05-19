import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';

class ChallengePlanCompletedScreen extends StatelessWidget {
  const ChallengePlanCompletedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // 이전 화면에서 전달된 데이터
    final args =
        ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
    final challengeName = args?['challengeName'] as String? ?? '새 챌린지';
    final plans = args?['plans'] as List<String>? ?? [];
    final kpis = args?['kpis'] as List<String>? ?? [];

    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: background,
        elevation: 0,
        automaticallyImplyLeading: false,
        leadingWidth: 52,
        leading: GestureDetector(
          onTap: () {
            Navigator.pop(context);
          },
          child: Container(
            margin: const EdgeInsets.only(left: 16),
            child: const Icon(
              TabBarIcon.leftArrow,
              size: 20,
              color: Colors.white,
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: Stack(
          children: [
            // 스크롤 가능한 메인 내용
            SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 챌린지 이름
                  Padding(
                    padding:
                        EdgeInsets.symmetric(horizontal: 24.w, vertical: 8.h),
                    child: Text(
                      challengeName,
                      style: TextStyle(
                        color: textPrimary,
                        fontSize: 26.sp,
                        fontWeight: FontWeight.w800,
                        fontFamily: 'Pretendard',
                      ),
                    ),
                  ),
                  SizedBox(height: 16.h),
                  // 플랜 리스트 (타임라인 스타일)
                  ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: plans.isEmpty ? 0 : 100.h,
                      maxHeight: 400.h,
                    ),
                    child: plans.isEmpty
                        ? const Center(
                            child: Text('플랜이 없습니다.',
                                style: TextStyle(color: Colors.white)))
                        : ListView.builder(
                            physics: const NeverScrollableScrollPhysics(),
                            padding: EdgeInsets.only(
                                bottom: 16.h, left: 20.w, right: 20.w),
                            shrinkWrap: true,
                            itemCount: plans.length,
                            itemBuilder: (context, idx) {
                              return Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Row(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      // 파란색 원 (도넛 모양)과 세로선
                                      Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          // 파란색 원 (도넛 모양)
                                          Stack(
                                            alignment: Alignment.center,
                                            children: [
                                              // 바깥 파란색 원
                                              Container(
                                                width: 24.w,
                                                height: 24.w,
                                                decoration: const BoxDecoration(
                                                  color: c700,
                                                  shape: BoxShape.circle,
                                                ),
                                              ),
                                              // 안쪽 흰색 원
                                              Container(
                                                width: 14.w,
                                                height: 14.w,
                                                decoration: const BoxDecoration(
                                                  color: Colors.white,
                                                  shape: BoxShape.circle,
                                                ),
                                              ),
                                            ],
                                          ),
                                          // 세로선 (마지막 아이템이 아닌 경우에만 표시)
                                          if (idx < plans.length - 1)
                                            Container(
                                              width: 2.w,
                                              height: 25.h,
                                              color: const Color(0xFF848484),
                                            ),
                                        ],
                                      ),
                                      SizedBox(width: 12.w),
                                      // 플랜 텍스트
                                      Expanded(
                                        child: Container(
                                          padding: EdgeInsets.symmetric(
                                              horizontal: 16.w, vertical: 3.h),
                                          decoration: BoxDecoration(
                                            border: Border.all(
                                                color: c600, width: 1),
                                            borderRadius:
                                                BorderRadius.circular(30.r),
                                            color: boxBackgroundColor,
                                          ),
                                          child: Text(
                                            plans[idx],
                                            style: TextStyle(
                                              color: textPrimary,
                                              fontSize: 15.sp,
                                              fontWeight: FontWeight.w500,
                                              fontFamily: 'Pretendard',
                                            ),
                                            maxLines: 2,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 0),
                                ],
                              );
                            },
                          ),
                  ),
                  SizedBox(height: 8.h),
                  // KPI 리스트
                  Container(
                    height: 120.h,
                    padding: EdgeInsets.symmetric(horizontal: 20.w),
                    child: LayoutBuilder(
                      builder: (context, constraints) {
                        return ListView.builder(
                          scrollDirection: Axis.horizontal,
                          clipBehavior: Clip.none,
                          padding: EdgeInsets.zero,
                          itemCount: kpis.length,
                          itemExtent: constraints.maxWidth * 0.45,
                          itemBuilder: (context, idx) {
                            return Container(
                              margin: EdgeInsets.only(right: 10.w),
                              padding: EdgeInsets.all(12.w),
                              decoration: BoxDecoration(
                                color: boxBackgroundColor,
                                borderRadius: BorderRadius.circular(20.r),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    'KPI #${idx + 1}',
                                    style: TextStyle(
                                      color: textPrimary,
                                      fontWeight: FontWeight.w800,
                                      fontSize: 16.sp,
                                      fontFamily: 'Pretendard',
                                    ),
                                  ),
                                  SizedBox(height: 4.h),
                                  Expanded(
                                    child: Text(
                                      kpis[idx],
                                      style: TextStyle(
                                        color: textPrimary,
                                        fontSize: 12.sp,
                                        fontWeight: FontWeight.w500,
                                        fontFamily: 'Pretendard',
                                      ),
                                      maxLines: 3,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        );
                      },
                    ),
                  ),
                  SizedBox(height: 16.h),
                  // 말풍선 (Positioned가 아니라 Row로 배치)
                  Row(
                    children: [
                      SizedBox(width: 100.w),
                      Container(
                        width: 180.w,
                        alignment: Alignment.center,
                        margin: EdgeInsets.only(bottom: 20.h),
                        padding: EdgeInsets.symmetric(
                            horizontal: 22.w, vertical: 14.h),
                        decoration: BoxDecoration(
                          color: c900,
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(24.r),
                            topRight: Radius.circular(24.r),
                            bottomLeft: Radius.circular(5.r),
                            bottomRight: Radius.circular(24.r),
                          ),
                        ),
                        child: Text(
                          '앞으로 화이팅!',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 20.sp,
                            fontWeight: FontWeight.w700,
                            fontFamily: 'Pretendard',
                          ),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 24.h),
                  // 아래 여백 (버튼과 겹치지 않게)
                  SizedBox(height: 64.h),
                ],
              ),
            ),
            // 캐릭터 이미지를 항상 왼쪽 하단에 고정
            Align(
              alignment: Alignment.bottomLeft,
              child: Image.asset(
                'assets/img/character.png',
                width: 180.w,
                fit: BoxFit.contain,
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: Container(
          padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 16.h),
          color: background,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              SizedBox(
                width: 100.w,
                height: 48.h,
                child: ElevatedButton(
                  onPressed: () {
                    // 홈 화면으로 이동
                    Navigator.of(context).pushNamedAndRemoveUntil(
                      '/main',
                      (route) => false,
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: c900,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12.r),
                    ),
                    elevation: 0,
                  ),
                  child: Text(
                    '완료',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w600,
                      fontFamily: 'Pretendard',
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
