import 'package:flutter/material.dart';
import 'package:flutter_native_splash/flutter_native_splash.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/crew_list_page.dart';
import 'package:reme/screens/feed.dart';
import 'package:reme/screens/home.dart';
import 'package:reme/screens/retrospectPage.dart';
import 'package:reme/services/crew_api.dart';
import 'package:reme/services/retrospect_api.dart';
import 'package:reme/services/user_update.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';
import 'package:reme/utils/crew_controller.dart';
import 'package:reme/utils/retrospect_controller.dart';
import 'package:reme/utils/user_info_controller.dart';

class Initialpage extends StatefulWidget {
  const Initialpage({super.key});

  @override
  State<Initialpage> createState() => _InitialpageState();
}

class _InitialpageState extends State<Initialpage>
    with TickerProviderStateMixin {
  TabController? tabController;
  TabController? retroTabController;
  ScrollController scrollController = ScrollController();
  int _selectIndex = 0;
  int _retroSelectIndex = 0;
  dynamic userInfo;

  @override
  void initState() {
    super.initState();
    Get.put(UserInfoController());
    Get.put(CrewController());
    Get.put(RetrospectController());
    tabController = TabController(length: 4, vsync: this);
    retroTabController = TabController(length: 2, vsync: this);
    int loadingCount = 0;

    tabController!.addListener(() => setState(() {
          scrollController.jumpTo(0);
          retroTabController!.index = 0;
          _selectIndex = tabController!.index;
        }));
    retroTabController!.addListener(() => setState(() {
          _retroSelectIndex = retroTabController!.index;
        }));

    // 사용자 정보 저장
    Future.wait<dynamic>([
      getUserInfo().then((value) {
        Get.find<UserInfoController>().setUserInfo(value['id'].toString(),
            value['username'], value['email'], value['profile_image']);
        setState(() {
          userInfo = Get.find<UserInfoController>().getUserInfo();
        });
      }),
      getJoinedCrewList().then((value) {
        Get.find<CrewController>().setJoinedCrewList(value);
      }),
      getCrewList().then((value) {
        Get.find<CrewController>().setNotJoinedCrewList(value.data['results']);
      }),
      getChallengeList(filter: 0).then((value) {
        // TODO: 챌린지 리스트 상태관리
      }),
      getMyCrewMembership().then((value) {
        Get.find<CrewController>().setMyCrewMembership(value.data);
      }),
      getAllRetrospectList().then((value) {
        Get.find<RetrospectController>().setRetrospectList(value);
      }),
    ]).then((_) {
      FlutterNativeSplash.remove();
      setState(() {}); // Home 위젯을 다시 렌더링
    });
  }

  @override
  void dispose() {
    tabController!.dispose();
    retroTabController!.dispose();
    scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> pageOptions = [
      Home(onCrewMoreTap: () {
        setState(() {
          _selectIndex = 2;
          tabController?.index = 2;
        });
      }, switchToRetrospect: () {
        setState(() {
          _selectIndex = 1;
          tabController?.index = 1;
        });
      }),
      RetroPage(tabNo: _retroSelectIndex),
      const CrewListPage(),
      const Feed(),
    ];

    return Scaffold(
      backgroundColor: background,
      body: Stack(
        children: [
          // 메인 콘텐츠(스크롤)
          SafeArea(
            child: CustomScrollView(
              physics: const BouncingScrollPhysics(),
              slivers: [
                SliverAppBar(
                  title: Text(
                    "To-GO",
                    style: TextStyle(
                      fontSize: 24.sp,
                      fontWeight: FontWeight.w700,
                      color: c700,
                    ),
                  ),
                  backgroundColor: background,
                  centerTitle: false,
                  actions: [
                    IconButton(
                        onPressed: () {
                          Navigator.pushNamed(context, Routes.notificationList);
                        },
                        icon: const Icon(
                          Icons.notifications_outlined,
                          color: c700,
                        )),
                    Container(
                        padding: EdgeInsets.only(left: 8.w, right: 19.w),
                        child: GestureDetector(
                            onTap: () {
                              if (userInfo != null) {
                                Navigator.pushNamed(context, Routes.myPage);
                              }
                            },
                            child: CircleAvatar(
                              radius: 18.5.r,
                              backgroundImage: userInfo != null &&
                                      userInfo['profile_image'] != null
                                  ? NetworkImage(userInfo['profile_image'])
                                  : null,
                            )))
                  ],
                  toolbarHeight: 55,
                  floating: true, // 최상단으로 올리지 않아도 appbar 표시
                  scrolledUnderElevation: 0, // 스크롤시 appbar 색상 변경 안되게
                  snap: true,
                  bottom: (_selectIndex == 1)
                      ? TabBar(
                          controller: retroTabController,
                          indicatorColor: Colors.white,
                          unselectedLabelColor: Color(0xFF848484),
                          labelColor: fontColor,
                          tabs: [
                              Tab(
                                child: Text(
                                  "회고 목록",
                                  style: TextStyle(
                                    fontSize: 16.sp,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                              Tab(
                                child: Text(
                                  "챌린지 목록",
                                  style: TextStyle(
                                    fontSize: 16.sp,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              )
                            ])
                      : null,
                ),
                SliverList(
                    delegate: SliverChildListDelegate([
                  pageOptions.elementAt(_selectIndex),
                ]))
              ],
              controller: scrollController,
            ),
          ),
          // 곡선이 적용된 TabBar (Stack의 맨 위)
          Align(
            alignment: Alignment.bottomCenter,
            child: SafeArea(
              top: false,
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(36),
                ),
                child: Container(
                  height: 80,
                  decoration: const BoxDecoration(
                    color: Color(0xFF181818),
                    border: Border(
                      left: BorderSide(
                        color: Color(0xFF838383),
                        width: 0.3,
                      ),
                      top: BorderSide(
                        color: Color(0xFF838383),
                        width: 0.3,
                      ),
                      right: BorderSide(
                        color: Color(0xFF838383),
                        width: 0.3,
                      ),
                    ),
                    borderRadius: BorderRadius.vertical(
                      top: Radius.circular(36),
                    ),
                  ),
                  child: TabBar(
                    dividerColor: Colors.transparent,
                    indicatorColor: Colors.transparent,
                    labelColor: background2,
                    unselectedLabelColor: const Color(0xFF848484),
                    controller: tabController,
                    tabs: const [
                      Tab(
                        icon: Icon(
                          TabBarIcon.home,
                        ),
                        text: "홈",
                      ),
                      Tab(
                        icon: Icon(TabBarIcon.layers),
                        text: "회고",
                      ),
                      Tab(
                        icon: Icon(
                          TabBarIcon.award,
                        ),
                        text: "크루",
                      ),
                      Tab(
                        icon: Icon(TabBarIcon.files),
                        text: "피드",
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
