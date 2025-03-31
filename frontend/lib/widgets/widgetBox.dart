import 'package:flutter/material.dart';

class WidgetBox extends StatelessWidget {
  double? width, height;
  List<Widget> children;
  String title;
  bool devide;
  WidgetBox({super.key, this.width, this.height, required this.children, this.title='', required this.devide});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: this.width,
      height: this.height,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1), // 투명도 70% 회색
            spreadRadius: 3, // 퍼짐 효과
            blurRadius: 10, // 뭉갬 효과
          )
        ]
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if(title != '')
            Container(
              padding: EdgeInsets.fromLTRB(10, 10, 0, 0),
              child: Text(
                title,
              ),
            ),
          if(devide)
            Divider(
              thickness: 3,
              height: 10,
            ),
          Container(
            padding: EdgeInsets.fromLTRB(10, 0, 5, 5),
            child: Column(
              children: children,
            ),
          ),
        ],
      ),
    );
  }
}
