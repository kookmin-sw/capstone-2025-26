import 'package:flutter/material.dart';

class WidgetBox extends StatelessWidget {
  double? width, height;
  List<Widget> children;
  String title;
  bool isMore;
  EdgeInsets marginLTRB;
  Function()? onTap;
  WidgetBox({super.key, this.width=double.maxFinite, this.height, required this.children, this.title='', required this.isMore, required this.marginLTRB, this.onTap});

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Container(
        width: this.width,
        height: this.height,
        margin: marginLTRB,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if(title != '')
              Container(
                padding: EdgeInsets.fromLTRB(28, 24, 0, 10),
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF333C4B)
                  ),
                ),
              ),
            Container(
              margin: EdgeInsets.fromLTRB(20, 0, 20, 0),
              padding: EdgeInsets.fromLTRB(10, 10, 0, 5),
              child: Column(
                children: children,
              ),
            ),
            if(isMore)
              InkWell(
                onTap: onTap,
                child: Container(
                  height: 32,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    gradient: const LinearGradient(
                      begin: Alignment.centerLeft,
                      end: Alignment.centerRight,
                      colors: [
                        Color(0xFFFFFFFF),
                        Color(0xFFF8FAF9),
                        Color(0xFFFFFFFF)
                      ]
                    )
                  ),
                  child: Column(
                    children: [
                      Container(
                        width: 394,
                        height: 2,
                        decoration: const ShapeDecoration(
                          shape: RoundedRectangleBorder(
                            side: BorderSide(
                              width: 1,
                              strokeAlign: BorderSide.strokeAlignCenter,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                      Container(
                        margin: EdgeInsets.fromLTRB(0, 7, 0, 0),
                        child: const Center(
                          child: Text(
                              "더보기",
                            style: TextStyle(
                              color: const Color(0xFF4D5967),
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
