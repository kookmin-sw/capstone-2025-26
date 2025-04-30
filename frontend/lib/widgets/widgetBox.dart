import 'package:flutter/material.dart';
import 'package:reme/themes/color.dart';

class WidgetBox extends StatelessWidget {
  double? width, height;
  List<Widget> children;
  String title;
  bool isMore;
  EdgeInsets marginLTRB;
  Function()? onTap;
  WidgetBox(
      {super.key,
      this.width = double.maxFinite,
      this.height,
      required this.children,
      this.title = '',
      required this.isMore,
      required this.marginLTRB,
      this.onTap});

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Container(
        width: width,
        height: height,
        margin: marginLTRB,
        decoration: BoxDecoration(
          color: boxBackgroundColor,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != '')
              Container(
                padding: const EdgeInsets.fromLTRB(28, 24, 0, 0),
                child: Text(
                  title,
                  style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: fontColor),
                ),
              ),
            Container(
              margin: const EdgeInsets.fromLTRB(20, 10, 20, 20),
              child: Column(
                children: children,
              ),
            ),
            if (isMore)
              InkWell(
                onTap: onTap,
                child: Container(
                  height: 32,
                  decoration: BoxDecoration(
                    color: boxBackgroundColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    children: [
                      Container(
                        height: 1,
                        decoration: const BoxDecoration(
                            gradient: LinearGradient(
                                begin: Alignment.centerLeft,
                                end: Alignment.centerRight,
                                colors: [
                              Color(0xFF1C1B20),
                              Color(0xFF2C2C34),
                              Color(0xFF1C1B20),
                            ])),
                      ),
                      Container(
                        margin: const EdgeInsets.fromLTRB(0, 7, 0, 0),
                        child: const Center(
                          child: Text(
                            "더보기",
                            style: TextStyle(
                              color: fontColor,
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                              height: 1.50,
                            ),
                          ),
                        ),
                      )
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
