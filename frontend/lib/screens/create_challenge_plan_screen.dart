import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/routes.dart';

class CreateChallengePlanScreen extends StatefulWidget {
  const CreateChallengePlanScreen({super.key});

  @override
  State<CreateChallengePlanScreen> createState() =>
      _CreateChallengePlanScreenState();
}

class _CreateChallengePlanScreenState extends State<CreateChallengePlanScreen> {
  late List<String> plans;
  late List<String> kpis;
  int? editingPlanIdx;
  int? editingKpiIdx;
  final TextEditingController _planEditController = TextEditingController();
  final TextEditingController _kpiEditController = TextEditingController();

  @override
  void initState() {
    super.initState();

    plans = List.generate(5, (i) => '5분 3분 인터벌 트레이닝 10회 실시');
    kpis = List.generate(3, (i) => 'kpi 설명설명설명설명설명 설명설명설명설명설명 설명설명설명설명설명');
  }

  @override
  void dispose() {
    _planEditController.dispose();
    _kpiEditController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final challengeName = ModalRoute.of(context)?.settings.arguments as String?;
    // 키보드 높이 가져오기
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;

    return Scaffold(
      backgroundColor: background,
      resizeToAvoidBottomInset: true,
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
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: EdgeInsets.symmetric(horizontal: 20.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(height: 8.h),
                  Text(
                    '이런 플랜 어때요?',
                    style: TextStyle(
                      color: fontColor, // fontColor로 변경
                      fontSize: 27.sp,
                      fontWeight: FontWeight.w800,
                      fontFamily: 'Pretendard',
                    ),
                  ),
                  SizedBox(height: 16.h),
                  // 플랜 리스트 (타임라인)
                  ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: plans.isEmpty ? 0 : 100.h,
                      maxHeight: 400.h,
                    ),
                    child: plans.isEmpty
                        ? const SizedBox(height: 0)
                        : ListView.builder(
                            physics: const NeverScrollableScrollPhysics(),
                            padding: EdgeInsets.only(bottom: 16.h),
                            shrinkWrap: true,
                            itemCount: plans.length,
                            itemBuilder: (context, idx) {
                              final isEditing = editingPlanIdx == idx;
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
                                              height: 52.h,
                                              color: const Color(0xFF848484),
                                            ),
                                        ],
                                      ),
                                      SizedBox(width: 12.w),
                                      // 플랜 텍스트/수정 + 수정 아이콘
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
                                          child: Row(
                                            children: [
                                              Expanded(
                                                child: isEditing
                                                    ? TextField(
                                                        controller:
                                                            _planEditController,
                                                        autofocus: true,
                                                        style: TextStyle(
                                                          color: fontColor,
                                                          fontSize: 15.sp,
                                                          fontWeight:
                                                              FontWeight.w500,
                                                          fontFamily:
                                                              'Pretendard',
                                                        ),
                                                        minLines: 1,
                                                        maxLines: 2,
                                                        decoration:
                                                            const InputDecoration(
                                                          isDense: true,
                                                          border:
                                                              InputBorder.none,
                                                          contentPadding:
                                                              EdgeInsets.zero,
                                                        ),
                                                        onSubmitted: (value) {
                                                          setState(() {
                                                            plans[idx] = value;
                                                          });
                                                        },
                                                      )
                                                    : Text(
                                                        plans[idx],
                                                        style: TextStyle(
                                                          color: fontColor,
                                                          fontSize: 15.sp,
                                                          fontWeight:
                                                              FontWeight.w500,
                                                          fontFamily:
                                                              'Pretendard',
                                                        ),
                                                        maxLines: 2,
                                                        overflow: TextOverflow
                                                            .ellipsis,
                                                      ),
                                              ),
                                              IconButton(
                                                padding: EdgeInsets.zero,
                                                constraints:
                                                    const BoxConstraints(),
                                                icon: Image.asset(
                                                  'assets/img/edit.png',
                                                  width: 20,
                                                  height: 20,
                                                  color: isEditing
                                                      ? c700
                                                      : Colors.white,
                                                ),
                                                onPressed: () {
                                                  setState(() {
                                                    editingPlanIdx = idx;
                                                    _planEditController.text =
                                                        plans[idx];
                                                  });
                                                },
                                              ),
                                              SizedBox(width: 8.w),
                                            ],
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
                  SizedBox(
                    height: 120.h,
                    child: LayoutBuilder(
                      builder: (context, constraints) {
                        return ListView.builder(
                          scrollDirection: Axis.horizontal,
                          clipBehavior: Clip.none,
                          padding: EdgeInsets.zero,
                          itemCount: kpis.length,
                          itemExtent: constraints.maxWidth * 0.45,
                          itemBuilder: (context, idx) {
                            final isEditing = editingKpiIdx == idx;
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
                                  Row(
                                    children: [
                                      Text(
                                        'KPI #${idx + 1}',
                                        style: TextStyle(
                                          color: fontColor,
                                          fontWeight: FontWeight.w800,
                                          fontSize: 20.sp,
                                          fontFamily: 'Pretendard',
                                        ),
                                      ),
                                      const Spacer(),
                                      IconButton(
                                        padding: EdgeInsets.zero,
                                        constraints: const BoxConstraints(),
                                        icon: Image.asset(
                                          'assets/img/edit.png',
                                          width: 18,
                                          height: 18,
                                          color: isEditing ? c500 : greyColor,
                                        ),
                                        onPressed: () {
                                          setState(() {
                                            editingKpiIdx = idx;
                                            _kpiEditController.text = kpis[idx];
                                          });
                                        },
                                      ),
                                    ],
                                  ),
                                  SizedBox(height: 4.h),
                                  Expanded(
                                    child: isEditing
                                        ? TextField(
                                            controller: _kpiEditController,
                                            autofocus: true,
                                            style: TextStyle(
                                              color: fontColor,
                                              fontSize: 15.sp,
                                              fontWeight: FontWeight.w500,
                                              fontFamily: 'Pretendard',
                                            ),
                                            minLines: 2,
                                            maxLines: 3,
                                            decoration: const InputDecoration(
                                              isDense: true,
                                              border: InputBorder.none,
                                              contentPadding: EdgeInsets.zero,
                                            ),
                                            onSubmitted: (value) {
                                              setState(() {
                                                kpis[idx] = value;
                                              });
                                            },
                                          )
                                        : Text(
                                            kpis[idx],
                                            style: TextStyle(
                                              color: fontColor,
                                              fontSize: 15.sp,
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
                  SizedBox(height: 24.h),
                ],
              ),
            ),
          ),
          SafeArea(
            top: false,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 16.h),
              color: background,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // 플랜 추가 버튼
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        plans.add('새로운 플랜');
                      });
                    },
                    child: Container(
                        // padding:
                        //     EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
                        // decoration: BoxDecoration(
                        //   color: boxBackgroundColor,
                        //   borderRadius: BorderRadius.circular(12.r),
                        //   border: Border.all(color: c900),
                        // ),

                        //테스트 플랜추가 코드임. 괜찮으면 써도 되고, 별로다 하면 지우면 됨
                        // child: Row(
                        //   children: [
                        //     const Icon(Icons.add, color: c900, size: 20),
                        //     SizedBox(width: 4.w),
                        //     Text(
                        //       '플랜 추가',
                        //       style: TextStyle(
                        //         color: fontColor,
                        //         fontSize: 14.sp,
                        //         fontWeight: FontWeight.w500,
                        //         fontFamily: 'Pretendard',
                        //       ),
                        //     ),
                        //   ],
                        // ),
                        ),
                  ),
                  // 확인/다음 버튼
                  SizedBox(
                    width: 100.w,
                    height: 48.h,
                    child: ElevatedButton(
                      onPressed: () {
                        // 수정 중인 상태라면 수정 완료 처리
                        if (editingPlanIdx != null) {
                          setState(() {
                            plans[editingPlanIdx!] = _planEditController.text;
                            editingPlanIdx = null;
                          });
                        } else if (editingKpiIdx != null) {
                          setState(() {
                            kpis[editingKpiIdx!] = _kpiEditController.text;
                            editingKpiIdx = null;
                          });
                        } else {
                          // 다음 단계로 이동 - 플랜 생성 완료 페이지
                          Navigator.pushNamed(
                            context,
                            Routes.challengePlanCompleted,
                            arguments: {
                              'plans': plans,
                              'kpis': kpis,
                              'challengeName': challengeName,
                            },
                          );
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: c900,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8.r),
                        ),
                        elevation: 0,
                      ),
                      child: Text(
                        editingPlanIdx != null || editingKpiIdx != null
                            ? '확인'
                            : '다음',
                        style: TextStyle(
                          color: fontColor,
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
        ],
      ),
    );
  }
}
