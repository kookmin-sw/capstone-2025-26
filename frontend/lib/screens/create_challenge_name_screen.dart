import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/create_challenge_waiting_screen.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';

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
                suffixIcon: _challengeName.isNotEmpty
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
                    onPressed: _challengeName.trim().isNotEmpty
                        ? () {
                            if (widget.onNext != null) {
                              widget.onNext!(_challengeName.trim());
                            } else {
                              Navigator.of(context).pushNamed(
                                Routes.createChallengeWaiting,
                                arguments: _challengeName.trim(),
                              );
                            }
                          }
                        : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: c900,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12.r),
                      ),
                      elevation: 0,
                    ),
                    child: Text(
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
