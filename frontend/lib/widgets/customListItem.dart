import 'package:flutter/material.dart';
import 'package:reme/themes/color.dart';

class CustomListitem extends StatelessWidget {
  double width, height;
  String content;
  CustomListitem({super.key, this.width=double.maxFinite, required this.height, required this.content});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      child: Row(
        children: [
          Text(
            content,
            style: const TextStyle(
              fontSize: 18.0,
              fontWeight: FontWeight.w500,
              color: fontColor
            ),
          ),
          Spacer(),
          const Icon(
              Icons.chevron_right_outlined,
            color: greyColor,
          )
        ],
      ),
    );
  }
}
