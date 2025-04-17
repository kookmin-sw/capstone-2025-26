import 'package:flutter/material.dart';
import 'package:reme/widgets/customListItem.dart';
import 'package:reme/widgets/widgetBox.dart';

class Home extends StatefulWidget {
  const Home({super.key});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 20, 10, 20),
      child: Column(
        children: [
          WidgetBox(
              height: 100,
              isMore: false,
              marginLTRB: const EdgeInsets.all(0),
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(
                        onPressed: () {}, child: const Text("회고하러가기")),
                    ElevatedButton(
                        onPressed: () {
                          Navigator.pushNamed(context, '/signup');
                        },
                        child: const Text("회원가입")),
                  ],
                )
              ]),
          Container(
            height: 190,
            margin: const EdgeInsets.fromLTRB(0, 15, 0, 0),
            child: Row(
              children: [
                WidgetBox(
                  width: MediaQuery.of(context).size.width / 2 - 15,
                  height: 190,
                  isMore: false,
                  marginLTRB: const EdgeInsets.all(0),
                  children: const [],
                ),
                WidgetBox(
                  width: MediaQuery.of(context).size.width / 2 - 15,
                  height: 190,
                  isMore: false,
                  marginLTRB: const EdgeInsets.only(left: 10),
                  children: const [],
                )
              ],
            ),
          ),
          WidgetBox(
              title: "오늘 회고할거",
              isMore: false,
              marginLTRB: const EdgeInsets.only(top: 15),
              children: [
                CustomListitem(height: 50, content: "모두를 위한 머신러닝 읽기"),
                CustomListitem(height: 50, content: "모두를 위한 머신러닝 읽기"),
                CustomListitem(height: 50, content: "모두를 위한 머신러닝 읽기"),
              ]),
          WidgetBox(
            title: "크루 목록",
            isMore: true,
            marginLTRB: const EdgeInsets.only(top: 15),
            onTap: () {
              print("더보기 누름");
            },
            children: [
              CustomListitem(height: 50, content: "크루1"),
              CustomListitem(height: 50, content: "크루2"),
              CustomListitem(height: 50, content: "크루3"),
            ],
          )
        ],
      ),
    );
  }
}
