import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/comment_dialog.dart';
import 'package:reme/services/crew_api.dart';
import 'package:reme/services/user_update.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/utils/crew_controller.dart';
import 'package:table_calendar/table_calendar.dart';

class CrewDetail extends StatefulWidget {
  const CrewDetail({super.key});

  @override
  State<CrewDetail> createState() => _CrewDetailState();
}

class _CrewDetailState extends State<CrewDetail>
    with SingleTickerProviderStateMixin {
  TabController? _tabController;
  ScrollController? _scrollController;
  final double _expandedHeight = 240.h + 178.h;
  int _selectIndex = 0;
  bool _isCollapsed = false;
  bool _isLoading = true;
  bool _isUploaded = true;

  // 초기 위치 설정 변수들
  final double _iconInitialTop = 227.h; // 아이콘 초기 세로 위치 (하단에서부터)
  final double _iconInitialLeft = 20.0; // 아이콘 초기 가로 위치
  final double _nameInitialTop = 150.h; // 크루명 초기 세로 위치 (하단에서부터)
  final double _nameInitialLeft = 20.0; // 크루명 초기 가로 위치

  // 최종 위치 설정 변수들
  final double _iconFinalTop = 50.0; // 아이콘 최종 세로 위치 (앱바)
  final double _iconFinalLeft = 52.0; // 아이콘 최종 가로 위치 (앱바)
  final double _nameFinalTop = 53.0; // 크루명 최종 세로 위치 (앱바)
  final double _nameFinalLeft = 94.0; // 크루명 최종 가로 위치 (앱바)

  // 아이콘 및 텍스트 크기 설정
  final double _iconInitialSize = 70.0.r;
  final double _iconFinalSize = 32.0.r;
  final double _nameInitialSize = 19.0;
  final double _nameFinalSize = 16.0;

  DateTime _focusedDay = DateTime.now();

  final _challengeList = [
    "저속 노화 식단하기",
    "저속 노화에 대한 포스팅 올리기",
  ];
  String _selectChallenge = '';

  dynamic crew_id;
  String crew_name = '';
  String crew_description = '';
  String? crew_image = null;
  int crew_member_count = 0;

  final crewController = Get.put(CrewController());

  bool isCreator = false;
  int member_status = 0; // 0: 가입 안함, 1: 가입대기중, 2: 가입됨.

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _tabController!.addListener(() {
      if (!_tabController!.indexIsChanging) {
        setState(() {
          _selectIndex = _tabController!.index;
        });
      }
    });

    _scrollController = ScrollController();

    setState(() {
      _selectChallenge = _challengeList[0];
    });

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        crew_id = ModalRoute.of(context)!.settings.arguments;
        getCrewDetail(crew_id).then((value) {
          if (mounted) {
            setState(() {
              crew_name = value.data['crew_name'];
              crew_description = value.data['crew_description'];
              crew_image = value.data['crew_image'];
              crew_member_count = value.data['member_count'];
              isCreator = crewController.myCrewMembership[crew_id]?['role'] ==
                  'CREATOR';
              switch (crewController.myCrewMembership[crew_id]?['status']) {
                case 'PENDING':
                  member_status = 1;
                  break;
                case 'ACCEPTED':
                  member_status = 2;
                  break;
                default:
                  member_status = 0;
                  break;
              }
              _isLoading = false;
            });
          }
        });
      }
    });
  }

  @override
  void dispose() {
    _tabController!.dispose();
    _scrollController!.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: background,
        body: Center(
          child: CircularProgressIndicator(
            color: c700,
          ),
        ),
      );
    }

    return Scaffold(
      floatingActionButton: (_selectIndex == 1 || _selectIndex == 3)
          ? FloatingActionButton(
              backgroundColor: c900,
              shape: CircleBorder(),
              onPressed: () {
                Navigator.pushNamed(context, Routes.addPost,
                    arguments: _selectIndex);
              },
              child: const Icon(
                Icons.add,
                color: Colors.white,
              ),
            )
          : null,
      backgroundColor: background,
      body: NestedScrollView(
        controller: _scrollController,
        headerSliverBuilder: (context, innerBoxIsScrolled) {
          return [
            SliverAppBar(
              toolbarHeight: 84.h,
              primary: false,
              leadingWidth: 52,
              leading: GestureDetector(
                onTap: () {
                  Navigator.pop(context);
                },
                child: Container(
                    margin: const EdgeInsets.only(top: 43, left: 16),
                    child: const Icon(
                      TabBarIcon.leftArrow,
                      size: 20,
                      color: Colors.white,
                    )),
              ),
              expandedHeight: _expandedHeight,
              pinned: true,
              floating: false,
              backgroundColor: _isCollapsed ? background : Colors.transparent,
              scrolledUnderElevation: 0, // 스크롤시 appbar 색상 변경 안되게
              iconTheme: const IconThemeData(color: Colors.white),
              title: null,
              flexibleSpace: LayoutBuilder(
                builder: (context, constraints) {
                  final double currentHeight = constraints.biggest.height;
                  final double statusBar = MediaQuery.of(context).padding.top;
                  final bool isCollapsed =
                      currentHeight <= kToolbarHeight + statusBar + 5;

                  if (_isCollapsed != isCollapsed) {
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                      if (mounted) setState(() => _isCollapsed = isCollapsed);
                    });
                  }

                  // 애니메이션 진행 상태 계산 (0: 펼쳐짐, 1: 접힘)
                  double progress = 1.0 -
                      ((currentHeight - kToolbarHeight - statusBar) /
                          (_expandedHeight - kToolbarHeight - statusBar));
                  progress = progress.clamp(0.0, 1.0);

                  // 크루 아이콘 크기 계산
                  final double iconSize = _iconInitialSize -
                      (_iconInitialSize - _iconFinalSize) * progress;

                  // 크루 아이콘 위치 계산
                  final double startTop = _expandedHeight - _iconInitialTop;
                  final double endTop = _iconFinalTop;
                  final double iconTop =
                      startTop - (startTop - endTop) * progress;

                  final double iconLeft = _iconInitialLeft +
                      (_iconFinalLeft - _iconInitialLeft) * progress;

                  // 크루명 위치 계산
                  final double nameStartTop = _expandedHeight - _nameInitialTop;
                  final double nameEndTop = _nameFinalTop;
                  final double nameTop =
                      nameStartTop - (nameStartTop - nameEndTop) * progress;

                  final double nameLeft = _nameInitialLeft +
                      (_nameFinalLeft - _nameInitialLeft) * progress;

                  // 크루명 크기 계산
                  final double nameSize = _nameInitialSize -
                      (_nameInitialSize - _nameFinalSize) * progress;

                  return Stack(
                    fit: StackFit.expand,
                    children: [
                      // 1. 배경 이미지
                      Opacity(
                        opacity: 1 - progress,
                        child: Image.network(
                          'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
                          fit: BoxFit.cover,
                        ),
                      ),
                      // 2. 하단 배경 컨테이너와 컨텐츠
                      Positioned(
                        left: 0,
                        right: 0,
                        bottom: 0,
                        child: Opacity(
                          opacity: 1 - progress,
                          child: Stack(
                            clipBehavior: Clip.none,
                            children: [
                              Container(
                                width: double.maxFinite,
                                height: 178.h,
                                margin: EdgeInsets.only(top: 31.h),
                                color: boxBackgroundColor,
                                padding: EdgeInsets.fromLTRB(21.w, 0, 21.w, 0),
                                child: Stack(
                                  children: [
                                    Positioned(
                                      right: -10.w,
                                      top: 18.h,
                                      child: GestureDetector(
                                        onTap: () {
                                          showModalBottomSheet(
                                            context: context,
                                            backgroundColor: boxBackgroundColor,
                                            shape: RoundedRectangleBorder(
                                              borderRadius:
                                                  BorderRadius.vertical(
                                                top: Radius.circular(20.r),
                                              ),
                                            ),
                                            builder: (context) {
                                              return Container(
                                                padding: EdgeInsets.symmetric(
                                                    vertical: 20.h),
                                                child: Column(
                                                  mainAxisSize:
                                                      MainAxisSize.min,
                                                  children: [
                                                    // 크루 관리자일 경우만 관리하기 버튼 띄우기
                                                    if (isCreator)
                                                      ListTile(
                                                        leading: const Icon(
                                                          Icons
                                                              .admin_panel_settings,
                                                          color: fontColor,
                                                        ),
                                                        title: const Text(
                                                            '관리하기',
                                                            style: TextStyle(
                                                                color:
                                                                    fontColor)),
                                                        onTap: () {
                                                          Navigator.pop(
                                                              context);
                                                          Navigator.pushNamed(
                                                              context,
                                                              Routes.crewAdmin,
                                                              arguments:
                                                                  crew_id);
                                                        },
                                                      ),
                                                    ListTile(
                                                      leading: const Icon(
                                                          Icons
                                                              .report_problem_outlined,
                                                          color: fontColor),
                                                      title: const Text('신고하기',
                                                          style: TextStyle(
                                                              color:
                                                                  fontColor)),
                                                      onTap: () {
                                                        Navigator.pop(context);
                                                        // TODO: 신고하기 기능 구현
                                                      },
                                                    ),
                                                  ],
                                                ),
                                              );
                                            },
                                          );
                                        },
                                        child: const Icon(Icons.more_vert,
                                            color: Colors.white),
                                      ),
                                    ),
                                    Container(
                                      padding: EdgeInsets.only(top: 32.h),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              Container(
                                                child: Row(
                                                  children: [
                                                    SizedBox(
                                                        width:
                                                            142.w), // 크루명 공간 확보
                                                    // SizedBox(width: 13.w),
                                                    const Icon(
                                                      Icons
                                                          .person_outline_outlined,
                                                      color: Color(0xFF898989),
                                                      size: 15,
                                                    ),
                                                    SizedBox(width: 1.w),
                                                    Text(
                                                      '${crew_member_count}명',
                                                      style: TextStyle(
                                                        fontSize: 13.sp,
                                                        color:
                                                            Color(0xFFA3A3A3),
                                                      ),
                                                    ),
                                                    const Spacer(),
                                                  ],
                                                ),
                                              ),
                                              Container(
                                                padding:
                                                    EdgeInsets.only(top: 10.h),
                                                child: Text(
                                                  '${crew_description}',
                                                  style: TextStyle(
                                                      fontSize: 14.sp,
                                                      fontWeight:
                                                          FontWeight.w500,
                                                      color: fontColor,
                                                      height: 1.70.h,
                                                      letterSpacing: 0.01),
                                                  maxLines: 2,
                                                  overflow: TextOverflow.clip,
                                                ),
                                              ),
                                              Container(
                                                margin:
                                                    EdgeInsets.only(top: 15.h),
                                                height: 41.h,
                                                width: double.maxFinite,
                                                child: ElevatedButton(
                                                  style:
                                                      ElevatedButton.styleFrom(
                                                    backgroundColor:
                                                        (member_status == 1)
                                                            ? grey
                                                            : c800,
                                                    shape:
                                                        RoundedRectangleBorder(
                                                      borderRadius:
                                                          BorderRadius.circular(
                                                              10),
                                                    ),
                                                    padding:
                                                        const EdgeInsets.only(
                                                            top: 8, bottom: 8),
                                                  ),
                                                  onPressed: () {
                                                    if (member_status == 0) {
                                                      // 크루 가입하기
                                                      joinCrew(crew_id!
                                                              .toString())
                                                          .then((value) {
                                                        setState(() {
                                                          member_status++;
                                                        });
                                                      });
                                                    } else if (member_status ==
                                                        2) {
                                                      // 크루 회고하기.
                                                      Navigator.pushNamed(
                                                          context,
                                                          Routes
                                                              .retrospectChallenge);
                                                    }
                                                  },
                                                  child: Text(
                                                    (member_status == 2)
                                                        ? "크루 회고 하기"
                                                        : (member_status == 1)
                                                            ? "가입 대기중"
                                                            : "크루 가입하기",
                                                    style: TextStyle(
                                                      fontSize: 16.sp,
                                                      color: fontColor,
                                                      fontWeight:
                                                          FontWeight.w700,
                                                      height: 1.5.h,
                                                    ),
                                                  ),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              // 아이콘만 따로 위로 올림
                              Positioned(
                                top: -18.h,
                                left: 21.w,
                                child: Opacity(
                                  opacity: 1 - progress,
                                  child: const SizedBox(), // 아이콘 자리 빈공간으로 대체
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      // 7. 애니메이션되는 크루 아이콘 (앱바에 고정)
                      Positioned(
                        top: progress < 0.01
                            ? _expandedHeight - _iconInitialTop
                            : iconTop,
                        left: progress < 0.01 ? _iconInitialLeft : iconLeft,
                        child: GestureDetector(
                          onTap: () {
                            if (isCreator) {
                              // 관리자의 경우 크루 프로필 클릭했을 때 크루 프로필 이미지 수정.
                              setState(() {
                                _isUploaded = false;
                              });
                              ImagePicker()
                                  .pickImage(source: ImageSource.gallery)
                                  .then((pickedFile) async {
                                if (pickedFile != null) {
                                  final response = await uploadProfileImage(
                                      File(pickedFile.path), 1, crew_id);
                                  if (mounted) {
                                    setState(() {
                                      crew_image = response;
                                    });
                                  }
                                  // joinedCrew 업데이트
                                  int joinedIndex = crewController.joinedCrew
                                      .indexWhere((element) =>
                                          element['id'] == crew_id);
                                  if (joinedIndex != -1) {
                                    crewController.joinedCrew[joinedIndex]
                                        ['crew_image'] = response;
                                  }
                                  updateCrewProfileImage(crew_id, response)
                                      .then((value) {
                                    setState(() {
                                      _isUploaded = true;
                                    });
                                  });
                                } else {
                                  setState(() {
                                    _isUploaded = true;
                                  });
                                }
                              });
                              // TODO: 크루 프로필 업데이트 후 크루 리스트 페이지 이동했을 때 바로 반영 안되는 문제 수정 필요
                            }
                          },
                          child: Container(
                            width: iconSize,
                            height: iconSize,
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              // TODO: 크루 프로필 이미지 네트워크로 추가
                              child: !_isUploaded
                                  ? Container(
                                      width: iconSize,
                                      height: iconSize,
                                      color: boxBackgroundColor,
                                      child: const Center(
                                        child: CircularProgressIndicator(
                                          color: c700,
                                        ),
                                      ),
                                    )
                                  : crew_image != null
                                      ? Image.network(crew_image!,
                                          fit: BoxFit.cover)
                                      : Icon(
                                          Icons.group,
                                          size: iconSize * 0.7,
                                          color: Colors.grey,
                                        ),
                            ),
                          ),
                        ),
                      ),
                      // 8. 애니메이션되는 크루명
                      Positioned(
                        left: progress < 0.01 ? _nameInitialLeft : nameLeft,
                        top: progress < 0.01
                            ? _expandedHeight - _nameInitialTop
                            : nameTop,
                        child: Container(
                          width: 142.w,
                          child: Text(
                            '${crew_name}',
                            style: TextStyle(
                              letterSpacing: 0.01,
                              fontSize: nameSize.sp,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
            // 탭 메뉴
            SliverPersistentHeader(
              key: ValueKey<int>(_selectIndex),
              delegate: _SliverAppBarDelegate(
                TabBar(
                  tabAlignment: TabAlignment.start,
                  controller: _tabController,
                  labelColor: Colors.white,
                  unselectedLabelColor: Colors.white70,
                  indicatorColor: Colors.transparent,
                  dividerColor: Colors.transparent,
                  isScrollable: true,
                  padding: EdgeInsets.zero,
                  labelPadding: const EdgeInsets.only(left: 5, right: 5),
                  onTap: (index) {
                    setState(() {
                      _selectIndex = index;
                    });
                  },
                  tabs: [
                    _buildTab('전체', _selectIndex == 0),
                    _buildTab('공지', _selectIndex == 1),
                    _buildTab('회고', _selectIndex == 2),
                    _buildTab('게시판', _selectIndex == 3),
                  ],
                ),
              ),
              pinned: true,
            ),
          ];
        },
        body: TabBarView(
          controller: _tabController,
          children: [
            _buildPostList(),
            _buildPostList(),
            _buildRetrospectList(),
            _buildPostList(),
          ],
        ),
      ),
    );
  }

  Widget _buildTab(String label, bool selected) {
    return Tab(
      child: Container(
        width: 101.w,
        decoration: ShapeDecoration(
          color: selected ? c900 : boxBackgroundColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
        child: Container(
          padding: const EdgeInsets.fromLTRB(20, 9, 20, 9),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
                fontSize: 15.sp, fontWeight: FontWeight.w500, color: fontColor),
          ),
        ),
      ),
    );
  }

  Widget _buildPostList() {
    return ListView(
      padding: EdgeInsets.zero,
      children: const [
        PostCard(
          nickname: '다욤둥',
          date: '25.04.12 15:32',
          title: '다음주까지 식단 짜서 올려주세요',
          content: '저속 노화 유튜브 영상 보고\n최대한 건강하게 식단 짜서 공유 부탁드립니다\n게시글로 남겨주세요!',
        ),
        PostCard(
          nickname: '롱기스트',
          date: '25.04.10 12:02',
          title: '이다현 보다 오래살기 크루에 오신 것을 환영합니다',
          content: '아무리 일찍 죽어도\n이다현 보다는 늦게 죽어봅시다\n파이팅!',
        ),
        PostCard(
          nickname: '공지사항',
          date: '25.04.10 12:02',
          title: '여기는 이다현보다 오래살기 크루입니다',
          content: '저속 노화 위주의 식사와 규칙적인 생활을 통해 삶을 재정비하고 이다현보다 오래 살기 위해 노력합니다',
        ),
      ],
    );
  }

  Widget _buildRetrospectList() {
    return SizedBox(
      height: 300.h,
      child: Column(
        children: [
          TableCalendar(
            headerStyle: HeaderStyle(
              titleCentered: true,
              titleTextStyle: TextStyle(
                fontSize: 20.sp,
                fontWeight: FontWeight.w600,
                color: fontColor,
              ),
              leftChevronIcon: Icon(
                Icons.chevron_left,
                color: fontColor,
              ),
              rightChevronIcon: Icon(
                Icons.chevron_right,
                color: fontColor,
              ),
              formatButtonVisible: false,
            ),
            calendarFormat: CalendarFormat.week,
            calendarStyle: const CalendarStyle(
              defaultTextStyle: TextStyle(color: fontColor),
              // weekend
              weekendTextStyle: TextStyle(color: Colors.red),
              weekendDecoration: BoxDecoration(
                color: Colors.transparent,
                shape: BoxShape.circle,
              ),
              // selected
              selectedDecoration: BoxDecoration(
                color: c700,
                shape: BoxShape.circle,
              ),
              // today
              todayDecoration: BoxDecoration(
                color: Colors.transparent,
                shape: BoxShape.circle,
              ),
            ),
            locale: "ko_KR",
            focusedDay: _focusedDay,
            firstDay: DateTime(2025, 01, 01),
            lastDay: DateTime(2030, 12, 31),
            selectedDayPredicate: (day) {
              return isSameDay(_focusedDay, day);
            },
            onDaySelected: (selectedDay, focusedDay) {
              setState(() {
                _focusedDay = focusedDay;
              });
            },
            onPageChanged: (focusedDay) {
              setState(() {
                _focusedDay = focusedDay;
              });
            },
          ),
          Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(horizontal: 21.w, vertical: 10.h),
            child: DropdownButton(
              alignment: Alignment.topLeft,
              focusColor: c800,
              value: _selectChallenge,
              dropdownColor: boxBackgroundColor,
              isExpanded: true,
              underline: Container(
                height: 2,
                color: c800,
              ),
              style: TextStyle(
                color: Colors.white,
                fontSize: 16.sp,
                fontWeight: FontWeight.w500,
              ),
              items: _challengeList
                  .map((e) => DropdownMenuItem(
                        child: Text(e),
                        value: e,
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  _selectChallenge = value!;
                });
              },
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  GestureDetector(
                    onTap: () {
                      Navigator.pushNamed(context, Routes.retrospectDetail);
                    },
                    child: PostCard(
                      nickname: '롱기스트',
                      date:
                          '${_focusedDay.year}.${_focusedDay.month}.${_focusedDay.day}',
                      title: _selectChallenge,
                      content: '오늘은 3k 달리기를 20분 페이스에 달렸어요. 조금만 더 빨리 뛰어봐요',
                      isRetrospect: true,
                      hasSuccess: false,
                      score: '60',
                    ),
                  ),
                  GestureDetector(
                    onTap: () {
                      Navigator.pushNamed(context, Routes.retrospectDetail);
                    },
                    child: PostCard(
                      nickname: '다욤둥',
                      date:
                          '${_focusedDay.year}.${_focusedDay.month}.${_focusedDay.day}',
                      title: _selectChallenge,
                      content: '3k 달리기를 16분 페이스에 달렸어요. 거의다 왔어요! 조금만 더 화이팅',
                      isRetrospect: true,
                      hasSuccess: true,
                      score: '90',
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

// 탭바를 고정시키기 위한 Delegate
class _SliverAppBarDelegate extends SliverPersistentHeaderDelegate {
  final TabBar _tabBar;

  _SliverAppBarDelegate(this._tabBar);

  @override
  double get minExtent => _tabBar.preferredSize.height + 9;

  @override
  double get maxExtent => _tabBar.preferredSize.height + 9;

  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      width: double.infinity,
      margin: EdgeInsets.zero,
      padding: const EdgeInsets.fromLTRB(16, 5, 0, 4),
      color: background,
      child: SizedBox(
        height: _tabBar.preferredSize.height,
        child: _tabBar,
      ),
    );
  }

  @override
  bool shouldRebuild(_SliverAppBarDelegate oldDelegate) {
    return true;
  }
}

// 게시글 카드 위젯
class PostCard extends StatelessWidget {
  final String nickname;
  final String date;
  final String title;
  final String content;
  final bool? isRetrospect;
  final String? score;
  final bool hasSuccess;
  final bool isComment;
  const PostCard({
    super.key,
    required this.nickname,
    required this.date,
    required this.title,
    required this.content,
    this.isRetrospect = false,
    this.score,
    this.hasSuccess = false,
    this.isComment = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: boxBackgroundColor,
      margin: EdgeInsets.only(bottom: 10.h),
      child: Padding(
        padding: EdgeInsets.fromLTRB(21.w, 16.h, 13.w, 11.h),
        // padding: EdgeInsets.symmetric(horizontal: 21.w, vertical: 14.h),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 20.r,
                  foregroundImage: const Svg('assets/img/account_circle.svg',
                      color: Colors.white),
                ),
                SizedBox(width: 12.w),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      nickname,
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 12.sp),
                    ),
                    Text(
                      date,
                      style: TextStyle(
                          color: const Color(0xFFC3C3C3), fontSize: 12.sp),
                    ),
                  ],
                ),
                const Spacer(),
                const Icon(Icons.more_vert, color: Color(0xFFD9D9D9), size: 20),
              ],
            ),
            SizedBox(height: 10.h),
            Text(
              title,
              style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 20.sp,
                  letterSpacing: 0.1.r),
            ),
            SizedBox(height: 5.h),
            Text(
              content,
              style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w400,
                  fontSize: 15.sp,
                  height: 1.5,
                  letterSpacing: 0.1.r),
            ),
            SizedBox(height: 15.h),
            if (isRetrospect == false)
              Row(
                children: [
                  SizedBox(
                    width: 1.w,
                  ),
                  Icon(TabBarIcon.heart, color: Colors.white, size: 16.sp),
                  SizedBox(width: 19.w),
                  if (isComment == false)
                    GestureDetector(
                        onTap: () {
                          showDialog(
                              context: context,
                              builder: (context) => Dialog(
                                    child: CommentDialog(postId: '1'),
                                  ));
                        },
                        child: Icon(TabBarIcon.comment,
                            color: Colors.white, size: 19.sp)),
                ],
              ),
            if (isRetrospect == true)
              Row(
                children: [
                  SizedBox(
                    width: 1.w,
                  ),
                  Icon(
                    hasSuccess ? Icons.local_fire_department : Icons.warning,
                    color: hasSuccess ? Colors.orange : Colors.yellow,
                    size: 24,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    "$score/100",
                    style: TextStyle(
                      color: hasSuccess ? Colors.orange : Colors.yellow,
                      fontFamily: 'Pretendard',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            SizedBox(
              height: 10.h,
            )
          ],
        ),
      ),
    );
  }
}
