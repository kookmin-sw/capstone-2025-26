import 'package:flutter/material.dart';
import 'package:reme/themes/color.dart';

class CrewBox extends StatelessWidget {
  double height;
  String? category;
  String title;
  ImageProvider? profileImage;
  Color? categoryColor;
  EdgeInsets marginLTRB;
  CrewBox({super.key, required this.height, this.profileImage, this.category, required this.title, this.categoryColor, required this.marginLTRB});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
      ),
      margin: marginLTRB,
      padding: EdgeInsets.all(20),
      child: Row(
        children: [
          CircleAvatar(
            backgroundImage: profileImage,
            radius: 27.5,
            backgroundColor: Colors.white
          ),
          SizedBox(width: 15,),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if(category != null)
              Container(
                padding: EdgeInsets.fromLTRB(13, 0, 13, 0),
                color: categoryColor,
                child: Text(
                  category!,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: fontColor
                  ),
                ),
              ),
              Text(
                title,
                style: const TextStyle(
                  color: fontColor,
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              )
            ],
          )
        ],
      ),
    );
  }
}
