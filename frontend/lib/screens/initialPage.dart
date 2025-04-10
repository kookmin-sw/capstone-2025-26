import 'package:flutter/material.dart';
import 'package:reme/screens/home.dart';
import 'package:reme/screens/restroPage.dart';

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
    Container(), //dummy Widget - crew
    const RetroPage(), // Retrospect
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
        backgroundColor: const Color(0xFFF3F4F6),
        bottomNavigationBar: SizedBox(
          height: 70,
          child: TabBar(
              indicatorColor: Colors.transparent,
              labelColor: const Color(0xFF333C4B),
              unselectedLabelColor: Colors.grey,
              controller: tabController,
              tabs: const [
                Tab(
                  icon: Icon(Icons.home_outlined),
                  text: "홈",
                ),
                Tab(
                  icon: Icon(Icons.keyboard_command_key_outlined),
                  text: "크루",
                ),
                Tab(
                  icon: Icon(Icons.layers_outlined),
                  text: "회고",
                ),
                Tab(
                  icon: Icon(Icons.hotel_class_outlined),
                  text: "목표",
                ),
                Tab(
                  icon: Icon(Icons.person_2_outlined),
                  text: "프로필",
                ),
              ]),
        ),
        body: CustomScrollView(
          physics: const BouncingScrollPhysics(),
          slivers: [
            SliverAppBar(
              title: const Text(
                "Re:Me",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
              backgroundColor: Colors.white,
              centerTitle: false,
              actions: [
                IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.notifications_outlined)),
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
        ));
  }
}
