import 'package:flutter/material.dart';

class ProfileBox extends StatelessWidget {
  double height;
  String name, subIntro;
  ImageProvider profileImage;
  ProfileBox({super.key, required this.height, required this.profileImage, required this.name, required this.subIntro});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1), // 투명도 70% 회색
              spreadRadius: 3, // 퍼짐 효과
              blurRadius: 10, // 뭉갬 효과
            )
          ]
      ),
      margin: EdgeInsets.all(10),
      padding: EdgeInsets.all(8),
      child: Row(
        children: [
          CircleAvatar(
            backgroundImage: profileImage,
            radius: 60,
          ),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                name,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                subIntro,
                style: const TextStyle(
                  color: Colors.grey,
                ),
              )
            ],
          )
        ],
      ),
    );
  }
}
