import 'package:flutter/material.dart';
import 'package:reme/themes/color.dart';
import 'package:reme/utils/iconToImage.dart';
import 'package:reme/widgets/crewBox.dart';

class RetroPage extends StatefulWidget {
  const RetroPage({super.key});

  @override
  State<RetroPage> createState() => _RetroPageState();
}

class _RetroPageState extends State<RetroPage> {
  ImageProvider? plusIcon;

  void firstUpdate(){
    setState(() {
      IconToImage(Icon(Icons.add, color: fontColor,), size: 48).then((result){
        plusIcon = result;
        print("test");
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.fromLTRB(10, 20, 10, 20),
      child: Column(
        children: [
          CrewBox(
              profileImage: AssetImage("assets/img/plusIcon.png"),
              height: 64,
              title: "새 회고 만들기",
              marginLTRB: EdgeInsets.zero
          ),
          for(int i = 0; i<10; i++)
            CrewBox(
                height: 100,
                title: "회고 제목",
                marginLTRB: EdgeInsets.fromLTRB(0, 10, 0, 0),
              category: "어학",
              categoryColor: Colors.grey,
            )
        ],
      ),
    );
  }
}
