import 'package:flutter/material.dart';

class CrewBox extends StatelessWidget {
  double height;
  String? category;
  String title;
  ImageProvider? profileImage;
  Color? categoryColor;
  CrewBox({super.key, required this.height, this.profileImage, this.category, required this.title, this.categoryColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
      ),
      margin: EdgeInsets.all(10),
      padding: EdgeInsets.all(20),
      child: Row(
        children: [
          CircleAvatar(
            backgroundImage: profileImage,
            radius: 27.5,
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
                  ),
                ),
              ),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.black,
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
