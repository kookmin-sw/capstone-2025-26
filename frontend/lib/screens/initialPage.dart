import 'package:flutter/material.dart';

class Initialpage extends StatefulWidget {
  const Initialpage({super.key});

  @override
  State<Initialpage> createState() => _InitialpageState();
}

class _InitialpageState extends State<Initialpage>
    with SingleTickerProviderStateMixin {
  TabController? tabController;
  int _selectIndex = 0;

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    tabController = TabController(length: 5, vsync: this);
    tabController!.addListener(
        () => setState((){
          _selectIndex = tabController!.index;
          print(_selectIndex);
        })
    );
  }

  @override
  void dispose() {
    // TODO: implement dispose
    tabController!.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
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
              onPressed: (){},
              icon: Icon(Icons.search_outlined)
          ),
          IconButton(
              onPressed: (){},
              icon: Icon(Icons.notifications_outlined)
          ),
        ],
      ),
      bottomNavigationBar: Container(
        height: 70,
        child: TabBar(
            indicatorColor: Colors.transparent,
            labelColor: Color(0xFF333C4B),
            unselectedLabelColor: Colors.grey,
            controller: tabController,
            tabs: [
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
            ]
        ),
      ),

    );
  }
}
