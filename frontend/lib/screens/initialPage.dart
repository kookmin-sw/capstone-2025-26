import 'package:flutter/material.dart';
import 'package:reme/screens/home.dart';
import 'package:reme/screens/restroPage.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/icon/tab_bar_icon_icons.dart';

class Initialpage extends StatefulWidget {
  const Initialpage({super.key});

  @override
  State<Initialpage> createState() => _InitialpageState();
}

class _InitialpageState extends State<Initialpage>
    with SingleTickerProviderStateMixin {
  TabController? tabController;
  ScrollController scrollController = ScrollController();
  int _selectIndex = 0;
  double _opacity = 1.0;

  final List<Widget> _pageOptions = [
    const Home(),
    const RetroPage(), // Retrospect
    Container(), //dummy Widget - crew
    Container(), //dummy Widget - challenge
    Container() //dummy Widget - profile
  ];

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    tabController = TabController(length: 5, vsync: this);
    tabController!.addListener(() => setState(() {
          scrollController.jumpTo(0);
          _selectIndex = tabController!.index;
          print(_selectIndex);
        }));
    scrollController.addListener(() {
      setState(() {
        // 스크롤 위치에 따라 opacity 조정
        _opacity = 1 - (scrollController.offset / 200).clamp(0.0, 1.0);
      });
    });
  }

  @override
  void dispose() {
    // TODO: implement dispose
    tabController!.dispose();
    scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        backgroundColor: background,
        bottomNavigationBar: SafeArea(
          child: Container(
            height: 70,
            clipBehavior: Clip.antiAlias,
            decoration: const ShapeDecoration(
              color: Color(0xFF181818),
              shape: RoundedRectangleBorder(
                side: BorderSide(
                  width: 0.50,
                  color: Color(0xFF838383),
                ),
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(36),
                  topRight: Radius.circular(36),
                ),
              ),
            ),
            child: ClipRect(
              child: TabBar(
                  indicatorColor: Colors.transparent,
                  labelColor: background2,
                  unselectedLabelColor: Color(0xFF848484),
                  controller: tabController,
                  tabs: const [
                    Tab(
                      icon: Icon(TabBarIcon.home,),
                      text: "홈",
                    ),
                    Tab(
                      icon: Icon(TabBarIcon.layers),
                      text: "회고",
                    ),
                    Tab(
                      icon: Icon(TabBarIcon.award,),
                      text: "크루",
                    ),
                    Tab(
                      icon: Icon(TabBarIcon.command),
                      text: "목표",
                    ),
                    Tab(
                      icon: Icon(TabBarIcon.user),
                      text: "프로필",
                    ),
                  ]),
            ),
          ),
        ),
        body: SafeArea(
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              SliverAppBar(
                title: const Text(
                  "Re:Me",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: c700
                  ),
                ),
                backgroundColor: background,
                centerTitle: false,
                actions: [
                  IconButton(
                      onPressed: () {},
                      icon: const Icon(Icons.notifications_outlined, color: c700,)),
                ],
                toolbarHeight: 55,
                floating: true, // 최상단으로 올리지 않아도 appbar 표시
                scrolledUnderElevation: 0, // 스크롤시 appbar 색상 변경 안되게
                snap: true,
              ),
              SliverList(
                  delegate: SliverChildListDelegate(
                      [_pageOptions.elementAt(_selectIndex)]))
            ],
            controller: scrollController,
          ),
        ));
  }
}
