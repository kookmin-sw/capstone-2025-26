import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/routes.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';

class CreateChallengeWaitingScreen extends StatefulWidget {
  const CreateChallengeWaitingScreen({super.key});

  @override
  State<CreateChallengeWaitingScreen> createState() =>
      _CreateChallengeWaitingScreenState();
}

class _CreateChallengeWaitingScreenState
    extends State<CreateChallengeWaitingScreen> {
  @override
  void initState() {
    super.initState();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      startTimer();
    });
  }

  void startTimer() {
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        try {
          final challengeName =
              ModalRoute.of(context)?.settings.arguments as String?;

          Navigator.of(context).pushReplacementNamed(
            Routes.createChallengePlan,
            arguments: challengeName ?? '새 챌린지',
          );
        } catch (e) {
          // 오류 발생시 디버그 메시지 표시
          debugPrint('오류 발생: $e');
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final challengeName =
        ModalRoute.of(context)?.settings.arguments as String? ?? '새 챌린지';

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
        bottom: false,
        child: Stack(
          children: [
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 24.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(height: 16.h),
                  Text(
                    challengeName,
                    style: TextStyle(
                      color: fontColor,
                      fontSize: 26.sp,
                      fontWeight: FontWeight.w800,
                      fontFamily: 'Pretendard',
                    ),
                  ),
                  SizedBox(height: 8.h),
                  Text(
                    '챌린지의 플랜 생성 중이에요!',
                    style: TextStyle(
                      color: fontColor,
                      fontSize: 22.sp,
                      fontWeight: FontWeight.w800,
                      fontFamily: 'Pretendard',
                    ),
                  ),
                  const Spacer(),
                  // 말풍선
                  Container(
                    width: 228.w,
                    alignment: Alignment.center,
                    margin: EdgeInsets.only(bottom: 20.h),
                    padding:
                        EdgeInsets.symmetric(horizontal: 22.w, vertical: 14.h),
                    decoration: BoxDecoration(
                      color: c900,
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(24.r),
                        topRight: Radius.circular(24.r),
                        bottomLeft: Radius.circular(24.r),
                        bottomRight: Radius.circular(5.r),
                      ),
                    ),
                    child: Text(
                      '조금만 기다려줘!',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 25.sp,
                        fontWeight: FontWeight.w700,
                        fontFamily: 'Pretendard',
                      ),
                    ),
                  ),
                  const Center(),
                  SizedBox(height: 350.h),
                ],
              ),
            ),
            // 캐릭터 이미지 (에러 방지)
            Positioned(
              right: 0.w,
              bottom: 0,
              child: Image.asset(
                'assets/img/character_attention.png',
                width: 260.w,
                fit: BoxFit.contain,
                errorBuilder: (context, error, stackTrace) {
                  debugPrint('이미지 로드 오류: $error');
                  return Container(
                    width: 260.w,
                    height: 260.h,
                    color: Colors.transparent,
                    alignment: Alignment.center,
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
