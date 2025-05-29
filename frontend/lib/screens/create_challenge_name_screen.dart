import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/create_challenge_waiting_screen.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/services/challenge_api.dart';
import 'package:logger/logger.dart'; // 로거 추가
import 'package:dio/dio.dart'; // DioException 사용을 위해

class CreateChallengeNameScreen extends StatefulWidget {
  final void Function(String name)? onNext;
  const CreateChallengeNameScreen({super.key, this.onNext});

  @override
  State<CreateChallengeNameScreen> createState() =>
      _CreateChallengeNameScreenState();
}

class _CreateChallengeNameScreenState extends State<CreateChallengeNameScreen> {
  final TextEditingController _controller = TextEditingController();
  String _challengeName = '';
  final _challengeApi = ChallengeApi();

  // 추가된 변수들
  final _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 1,
      errorMethodCount: 5,
      lineLength: 80,
      colors: true,
      printEmojis: true,
      printTime: false,
    ),
  );
  bool _isLoading = false; // 로딩 상태 변수 추가

  Future<void> _createChallengeAndProceed(String name) async {
    if (_isLoading) return; // 이미 로딩 중이면 중복 실행 방지

    setState(() {
      _isLoading = true;
    });

    // API 명세에 따른 deadline 형식 (ISO 8601)
    final String deadlineValue =
        DateTime.now().add(const Duration(days: 7)).toIso8601String();
    const String ownerTypeValue = 'USER'; // 개인 챌린지로 가정
    const String statusValue = 'LIVE'; // 활성 상태로 생성

    try {
      _logger.i(
          '챌린지 생성 시도: 이름="$name", 마감일="$deadlineValue", 타입="$ownerTypeValue", 상태="$statusValue"');

      final response = await _challengeApi.createChallenge(
        name,
        deadlineValue,
        ownerTypeValue,
        statusValue,
      );

      if (response.statusCode == 201) {
        _logger.i('챌린지 성공적으로 생성됨: ${response.data}');
        final createdChallengeData = response.data as Map<String, dynamic>?;

        if (widget.onNext != null) {
          widget.onNext!(name);
        } else {
          Navigator.of(context).pushReplacementNamed(
            Routes.createChallengeWaiting,
            arguments: createdChallengeData ?? {'challenge_name': name},
          );
        }
      } else {
        _logger.w('챌린지 생성 실패 (상태 코드 ${response.statusCode}): ${response.data}');
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          message: '챌린지 생성 실패 (상태 코드 ${response.statusCode})',
        );
      }
    } on DioException catch (e) {
      _logger.e('챌린지 생성 DioException: ${e.message}');
      if (e.response != null) {
        _logger.e('오류 응답 데이터: ${e.response?.data}');
        _logger.e('오류 응답 상태 코드: ${e.response?.statusCode}');
      }
      String errorMessage = '챌린지 생성 중 오류가 발생했습니다.';
      if (e.response?.data != null && e.response!.data is Map) {
        errorMessage = '오류: ${e.response!.data.toString()}';
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      _logger.e('챌린지 생성 중 알 수 없는 오류: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('챌린지 생성 중 알 수 없는 오류가 발생했습니다: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
      body: Padding(
        padding: EdgeInsets.symmetric(horizontal: 24.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 16.h),
            Text(
              '어떤 챌린지에 도전해 볼까요?',
              style: TextStyle(
                color: Colors.white,
                fontSize: 26.sp,
                fontWeight: FontWeight.w800,
                fontFamily: 'Pretendard',
              ),
            ),
            SizedBox(height: 40.h),
            Text(
              '챌린지 이름',
              style: TextStyle(
                color: c500,
                fontSize: 15.sp,
                fontWeight: FontWeight.w500,
                fontFamily: 'Pretendard',
              ),
            ),
            SizedBox(height: 8.h),
            TextFormField(
              controller: _controller,
              enabled: !_isLoading, // 로딩 중일 때 입력 비활성화
              style: TextStyle(
                color: Colors.white,
                fontSize: 22.sp,
                fontWeight: FontWeight.w700,
                fontFamily: 'Pretendard',
              ),
              cursorColor: c500,
              maxLength: 50,

              decoration: InputDecoration(
                counterText: '',
                enabledBorder: const UnderlineInputBorder(
                  borderSide: BorderSide(color: c500, width: 1.5),
                ),
                focusedBorder: const UnderlineInputBorder(
                  borderSide: BorderSide(color: c500, width: 2),
                ),
                suffixIcon: _challengeName.isNotEmpty && !_isLoading
                    ? IconButton(
                        icon: const Icon(Icons.clear, color: Colors.white),
                        onPressed: () {
                          setState(() {
                            _controller.clear();
                            _challengeName = '';
                          });
                        },
                      )
                    : null,
              ),
              onChanged: (value) {
                setState(() {
                  _challengeName = value;
                });
              },
            ),
            SizedBox(height: 4.h),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                '${_challengeName.length}/50',
                style: TextStyle(
                  color: const Color(0xFF226BEF),
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w400,
                  fontFamily: 'Pretendard',
                ),
              ),
            ),
            const Spacer(),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                SizedBox(
                  width: 100.w,
                  height: 48.h,
                  child: ElevatedButton(
                    onPressed: _challengeName.trim().isNotEmpty && !_isLoading
                        ? () {
                            // API 호출 제거, 단순히 이름만 전달
                            Navigator.of(context).pushNamed(
                              Routes.createChallengeWaiting,
                              arguments:
                                  _challengeName.trim(), // String으로 이름만 전달
                            );
                          }
                        : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: c900,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12.r),
                      ),
                      elevation: 0,
                    ),
                    child: _isLoading
                        ? SizedBox(
                            // 로딩 인디케이터
                            width: 20.w,
                            height: 20.h,
                            child: const CircularProgressIndicator(
                              strokeWidth: 2.0,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : Text(
                            '다음',
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
            SizedBox(height: 24.h),
          ],
        ),
      ),
    );
  }
}
