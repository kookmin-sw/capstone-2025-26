import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/routes.dart';
import 'package:reme/screens/crew_list_page.dart';
import 'package:reme/screens/feed.dart';
import 'package:reme/screens/home.dart';
import 'package:reme/screens/retrospectPage.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';

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

  @override
  void initState() {
    super.initState();
    tabController = TabController(length: 4, vsync: this);
    retroTabController = TabController(length: 2, vsync: this);

    tabController!.addListener(() => setState(() {
          scrollController.jumpTo(0);
          retroTabController!.index = 0;
          _selectIndex = tabController!.index;
        }));
    retroTabController!.addListener(() => setState(() {
          _retroSelectIndex = retroTabController!.index;
        }));
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
                        onPressed: () {},
                        icon: const Icon(
                          Icons.notifications_outlined,
                          color: c700,
                        )),
                    Container(
                        padding: EdgeInsets.only(left: 8.w, right: 19.w),
                        child: GestureDetector(
                            onTap: () {
                              Navigator.pushNamed(context, Routes.myPage,
                                  arguments: "이다현");
                            },
                            child: CircleAvatar(
                              radius: 18.5.r,
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
