import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:get/get.dart';
import 'package:reme/services/crew_api.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/crew_controller.dart';

class CrewAdminPage extends StatefulWidget {
  const CrewAdminPage({super.key});

  @override
  State<CrewAdminPage> createState() => _CrewAdminPageState();
}

class _CrewAdminPageState extends State<CrewAdminPage> {
  final crewController = Get.put(CrewController());
  late final int crew_index;
  late int pendingMemberCount; // 가입 대기중인 사람 수
  late int alreadyMemberCount; // 이미 크루 멤버인 사람 수

  int? crew_id;
  bool _isLoaded = false;
  List<dynamic> pendingMemberList = [];
  List<dynamic> alreadyMemberList = [];

  bool joinCrewHeaderPinned = true;
  late final ScrollController _scrollController;

  void showConfirmDialog({
    required String title,
    required String content,
    required VoidCallback onConfirm,
  }) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: boxBackgroundColor,
        title: Text(
          title,
          style: TextStyle(
            color: fontColor,
            fontSize: 18.sp,
            fontWeight: FontWeight.w700,
          ),
        ),
        content: Text(
          content,
          style: TextStyle(
            color: fontColor,
            fontSize: 16.sp,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              '아니오',
              style: TextStyle(
                color: fontColor,
                fontSize: 16.sp,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              onConfirm();
            },
            child: Text(
              '예',
              style: TextStyle(
                color: c700,
                fontSize: 16.sp,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_isLoaded) {
      crew_id = ModalRoute.of(context)?.settings.arguments as int;
      // crew_id = 2;
      crew_index = crewController.joinedCrew
          .indexWhere((element) => element['id'] == crew_id);
      getAllCrewMemberships(crew_id!).then((value) {
        if (!mounted) return;

        pendingMemberList.clear();
        alreadyMemberList.clear();

        for (var member in value.data['results']) {
          if (member['crew'] == crew_id && member['role'] != 'CREATOR') {
            if (member['status'] == 'PENDING') {
              pendingMemberList.add(member['user_details']);
            } else if (member['status'] == 'ACCEPTED') {
              alreadyMemberList.add(member['user_details']);
            }
          }
        }

        pendingMemberCount = pendingMemberList.length;
        alreadyMemberCount = alreadyMemberList.length;

        setState(() {
          _isLoaded = true;
        });
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isLoaded) {
      return Scaffold(
        backgroundColor: background,
        body: Center(
          child: CircularProgressIndicator(
            color: c700,
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: background,
      resizeToAvoidBottomInset: true,
      appBar: AppBar(
        backgroundColor: background,
        scrolledUnderElevation: 0,
        title: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8.r),
              child: crewController.joinedCrew[crew_index]['crew_image'] != null
                  ? Image.network(
                      crewController.joinedCrew[crew_index]['crew_image'],
                      width: 37.w,
                      height: 37.h,
                      fit: BoxFit.cover,
                    )
                  : Container(
                      width: 37.w,
                      height: 37.h,
                      color: Colors.white,
                      child: Icon(Icons.group, size: 37.w * 0.7, color: c100)),
            ),
            SizedBox(width: 10.w),
            Text(
              crewController.joinedCrew[crew_index]['crew_name'],
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
                        if (pendingMemberCount > 0)
                          Container(
                            height: 30.h,
                            margin: EdgeInsets.only(top: 5.h),
                            child: ElevatedButton(
                              onPressed: () {
                                showConfirmDialog(
                                    title: "모두 승인",
                                    content: "모든 가입 신청을 승인하시겠습니까?",
                                    onConfirm: () {
                                      for (var member in pendingMemberList) {
                                        acceptJoinRequest(crew_id!.toString(),
                                                member['id'].toString())
                                            .then((_) {
                                          setState(() {
                                            pendingMemberList.remove(member);
                                            pendingMemberCount--;
                                            alreadyMemberList.add(member);
                                            alreadyMemberCount++;
                                          });
                                        });
                                      }
                                    });
                              },
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
            image: pendingMemberList[index]['profile_image'] != null
                ? NetworkImage(pendingMemberList[index]['profile_image'])
                : Svg('assets/img/account_circle.svg'),
            width: 40.w,
            height: 40.h,
            color: c100,
          ),
          SizedBox(width: 16.w),
          Text(
            pendingMemberList[index]['username'],
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
              onTap: () {
                showConfirmDialog(
                  title: '가입 거절',
                  content:
                      '${pendingMemberList[index]['username']}님의 가입 신청을 거절하시겠습니까?',
                  onConfirm: () {
                    rejectJoinRequest(crew_id!.toString(),
                            pendingMemberList[index]['id'].toString())
                        .then((_) {
                      setState(() {
                        pendingMemberList.removeAt(index);
                        pendingMemberCount--;
                      });
                    });
                  },
                );
              },
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
            onTap: () {
              showConfirmDialog(
                title: '가입 승인',
                content:
                    '${pendingMemberList[index]['username']}님의 가입 신청을 승인하시겠습니까?',
                onConfirm: () {
                  acceptJoinRequest(crew_id!.toString(),
                          pendingMemberList[index]['id'].toString())
                      .then((_) {
                    setState(() {
                      pendingMemberList.removeAt(index);
                      pendingMemberCount--;
                      alreadyMemberList.add(pendingMemberList[index]);
                      alreadyMemberCount++;
                    });
                  });
                },
              );
            },
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
