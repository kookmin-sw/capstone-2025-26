import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/routes.dart';
import 'package:reme/themes/color.dart';

class CrewList extends StatefulWidget {
  final ImageProvider? image;
  final int crewId;
  final String crewName;
  final String crewIntro;
  final bool? isJoined;
  final VoidCallback? onJoinTap;
  final VoidCallback? afterCardClicked;
  bool? joinClicked;

  CrewList({
    super.key,
    this.image,
    required this.crewId,
    required this.crewName,
    required this.crewIntro,
    this.isJoined,
    this.onJoinTap,
    this.joinClicked,
    this.afterCardClicked,
  });

  @override
  State<CrewList> createState() => _CrewListState();
}

class _CrewListState extends State<CrewList> {
  late bool joinClicked;

  @override
  void initState() {
    super.initState();
    joinClicked = widget.joinClicked ?? false;
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.pushNamed(context, Routes.crew, arguments: widget.crewId)
            .then((_) {
          widget.afterCardClicked?.call();
        });
      },
      child: Container(
        width: 334.w,
        height: 50.h,
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8.r),
              child: widget.image != null
                  ? Image(
                      image: widget.image!,
                      width: 50.w,
                      height: 50.h,
                      fit: BoxFit.cover,
                    )
                  : Container(
                      width: 50.w,
                      height: 50.h,
                      color: Colors.white,
                      child: Icon(Icons.group,
                          size: 50.w * 0.7, color: Colors.grey)),
            ),
            SizedBox(
              width: 10.88.w,
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.crewName,
                  style: const TextStyle(
                    color: fontColor,
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Container(
                  width: (widget.isJoined == null)
                      ? 253.w
                      : (widget.isJoined == true)
                          ? 289.w
                          : 197.w,
                  child: Text(
                    widget.crewIntro,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: fontColor,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
            if (widget.isJoined == false)
              GestureDetector(
                onTap: () {
                  if (!joinClicked) {
                    setState(() {
                      joinClicked = true;
                    });
                    widget.onJoinTap?.call();
                  }
                },
                child: Container(
                  alignment: Alignment.center,
                  width: 70.w,
                  margin: EdgeInsets.symmetric(horizontal: 11.w),
                  decoration: BoxDecoration(
                    color: (!joinClicked) ? c900 : grey,
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  child: Text(
                    (!joinClicked) ? "가입하기" : "승인대기중",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 15.sp,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              )
          ],
        ),
      ),
    );
  }
}
