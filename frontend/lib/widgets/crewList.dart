import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';

class CrewList extends StatelessWidget {
  ImageProvider? image;
  String crewName; // 크루 이름
  String crewIntro; //크루 한줄 소개
  CrewList(
      {super.key, this.image, required this.crewName, required this.crewIntro});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 334.w,
      height: 50.h,
      child: Row(
        children: [
          Image(
            image: image ?? Svg("assets/img/account_circle.svg"),
            width: 50.w,
            height: 50.h,
          ),
          SizedBox(
            width: 10.88.w,
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                crewName,
                style: const TextStyle(
                  color: fontColor,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              Container(
                width: 253.w,
                child: Text(
                  crewIntro,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: fontColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
}
