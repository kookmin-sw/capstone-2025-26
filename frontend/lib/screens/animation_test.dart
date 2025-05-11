import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';

class StaggeredBoxAnimation extends StatefulWidget {
  const StaggeredBoxAnimation({super.key});

  @override
  State<StaggeredBoxAnimation> createState() => _StaggeredBoxAnimationState();
}

class _StaggeredBoxAnimationState extends State<StaggeredBoxAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  final List<Animation<Offset>> _downAnimations = [];
  final List<Animation<Offset>> _upAnimation = [];
  bool _isReversing = false;

  final List<double> _yposInit = [
    -0.4,
    -0.3,
    -0.2,
    -0.1,
  ]; // 위에서부터 흰색, 파란색, 흰색, 파란색 순. 값이 클수록 아래로
  final List<double> _yposFin = [0.1, 0.2, 0.3, 0.4];

  final List<Widget> _blocks = [
    Image.asset(
      'assets/img/whitebox.png',
      width: 370.w,
    ),
    Image.asset(
      'assets/img/blueBox.png',
      width: 370.w,
    ),
  ];

  @override
  void initState() {
    super.initState();

    // 1. 애니메이션 컨트롤러 설정
    _controller = AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 3000),
        reverseDuration: const Duration(milliseconds: 1500));

    for (int i = 0; i < 4; i++) {
      // 2. 내려오는 애니메이션 - 박스별로 다른 시간에 시작
      _downAnimations.add(
        Tween(
          begin: Offset(0, _yposInit[i]), // 시작 위치 (상단 밖)
          end: Offset(0, _yposFin[i]), // 최종 위치
        ).animate(
          CurvedAnimation(
            parent: _controller,
            curve: Interval(
                (3 - i) * 0.18, // 하단 박스부터 먼저 시작
                (3 - i) * 0.18 + 0.35,
                curve: Curves.easeInOutCubic),
          ),
        ),
      );

      // 3. 올라가는 애니메이션 - 모든 박스가 동시에 시작
      _upAnimation.add(Tween<Offset>(
        begin: Offset(0, _yposInit[i]), // 현재위치
        end: Offset(0, _yposFin[i]), // 최종위치
      ).animate(
        CurvedAnimation(
          parent: _controller,
          curve: const Interval(0.0, 0.5, curve: Curves.easeInOutCubic),
        ),
      ));
    }

    // 4. 애니메이션 상태 리스너 추가
    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        // 모든 박스가 내려왔을 때 약간의 지연 후 모두 동시에 올라감
        if (mounted) {
          setState(() {
            _isReversing = true;
          });
          _controller.reverse();
        }
      } else if (status == AnimationStatus.dismissed) {
        // 모든 박스가 올라갔을 때 약간의 지연 후 다시 내려옴
        if (mounted) {
          setState(() {
            _isReversing = false;
          });
          _controller.forward();
        }
      }
    });

    // 5. 애니메이션 시작
    _controller.forward();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      body: Stack(
        children: [
          for (int i = 3; i >= 0; i--)
            Center(
              child: SlideTransition(
                position: _isReversing ? _upAnimation[i] : _downAnimations[i],
                child: _blocks[i % 2],
              ),
            )
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
