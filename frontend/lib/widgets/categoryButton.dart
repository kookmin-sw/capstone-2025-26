import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';

class CategoryButton extends StatelessWidget {
  String text;
  int index;
  double? width;
  double? height;
  bool isSelected = false;
  final VoidCallback onTap;

  CategoryButton({
    required this.text,
    required this.index,
    this.height,
    this.isSelected = false,
    required this.onTap,
    this.width,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor:
              isSelected ? const Color(0xFF1C398E) : boxBackgroundColor,
          foregroundColor: Colors.white,
          elevation: 0,
          padding:
              EdgeInsets.symmetric(vertical: height != null ? height! / 5 : 18),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
            side: BorderSide.none,
          ),
        ),
        child: Container(
          width: width,
          height: height,
          alignment: Alignment.center,
          child: Text(
            text,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
