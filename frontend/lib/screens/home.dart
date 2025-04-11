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
      padding: EdgeInsets.fromLTRB(10, 20, 10, 20),
      child: Column(
        children: [
          WidgetBox(
              height: 100,
              children: [
                ElevatedButton(onPressed: (){}, child: Text("회고하러가기"))
              ],
              isMore: false,
              marginLTRB: EdgeInsets.all(0)
          ),
          Container(
            height: 190,
            margin: EdgeInsets.fromLTRB(0, 15, 0, 0),
            child: Row(
              children: [
                WidgetBox(
                  width: MediaQuery.of(context).size.width/2 - 15,
                  height: 190,
                  children: [],
                  isMore: false,
                  marginLTRB: EdgeInsets.all(0),
                ),
                WidgetBox(
                  width: MediaQuery.of(context).size.width/2 - 15,
                  height: 190,
                  children: [],
                  isMore: false,
                  marginLTRB: EdgeInsets.only(left: 10),
                )
              ],
            ),
          ),
          WidgetBox(
            title: "오늘 회고할거",
            children: [
              CustomListitem(height: 50, content: "모두를 위한 머신러닝 읽기"),
              CustomListitem(height: 50, content: "모두를 위한 머신러닝 읽기"),
              CustomListitem(height: 50, content: "모두를 위한 머신러닝 읽기"),
            ],
            isMore: false,
            marginLTRB: EdgeInsets.only(top: 15)
          ),
          WidgetBox(
              title: "크루 목록",
              children: [
                CustomListitem(height: 50, content: "크루1"),
                CustomListitem(height: 50, content: "크루2"),
                CustomListitem(height: 50, content: "크루3"),
              ],
              isMore: true,
              marginLTRB: EdgeInsets.only(top: 15),
            onTap: (){
                print("더보기 누름");
            },
          )
        ],
      ),
    );
  }
}

