import 'package:flutter/material.dart';

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
            style: TextStyle(
              fontSize: 18.0,
              fontWeight: FontWeight.w500,
              color: Color(0xFF333C4B)
            ),
          ),
          Spacer(),
          Icon(
              Icons.chevron_right_outlined,
            color: Color(0xFFD7D7D7),
          )
        ],
      ),
    );
  }
}
