import 'package:flutter/material.dart';

class CircleButton extends StatelessWidget {
  double size;
  Color btnColor;
  IconData? icon;
  String name;
  CircleButton({super.key, required this.size, required this.btnColor, this.icon, required this.name});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(50),
        color: btnColor,
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if(icon != null)
            Icon(
                icon,
              size: size/2,
              color: Colors.white,
            ),
          Text(
              name,
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold
            ),
          )
        ],
      ),
    );
  }
}
