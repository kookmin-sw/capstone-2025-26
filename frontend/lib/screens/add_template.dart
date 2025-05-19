import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:reme/themes/color.dart';

class AddTemplate extends StatefulWidget {
  const AddTemplate({super.key});

  @override
  State<AddTemplate> createState() => _AddTemplateState();
}

class _AddTemplateState extends State<AddTemplate> {
  List<TextEditingController> controllers = [];
  int steps = 3;
  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    controllers.add(TextEditingController());
    controllers.add(TextEditingController());
    controllers.add(TextEditingController());
    controllers.add(TextEditingController());
    controllers.add(TextEditingController());
    controllers.add(TextEditingController());
    controllers.add(TextEditingController());
    controllers.add(TextEditingController());
  }

  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: background,
      appBar: AppBar(
        backgroundColor: background,
        scrolledUnderElevation: 0,
        elevation: 0,
        leading: IconButton(
          onPressed: () {
            Navigator.pop(context);
          },
          icon: const Icon(
            Icons.arrow_back_ios_new,
            color: Colors.white,
          ),
        ),
      ),
      body: Container(
        margin:
            EdgeInsets.only(left: 21.w, top: 27.h, right: 21.w, bottom: 27.h),
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '템플릿 만들기',
                      style: TextStyle(
                        fontSize: 27.sp,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 5.h),
                    _buildInput(
                        "템플릿 이름", "한줄 설명", controllers[0], controllers[1]),
                    SizedBox(height: 20.h),
                    Row(
                      children: [
                        Text(
                          '내용',
                          style: TextStyle(
                            fontSize: 27.sp,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                          ),
                        ),
                        Spacer(),
                        IconButton(
                          onPressed: () {
                            setState(() {
                              if (steps > 1) {
                                steps--;
                                controllers.removeLast();
                                controllers.removeLast();
                              }
                            });
                          },
                          icon:
                              Icon(Icons.remove_outlined, color: Colors.white),
                        ),
                        IconButton(
                          onPressed: () {
                            setState(() {
                              steps++;
                              controllers.add(TextEditingController());
                              controllers.add(TextEditingController());
                            });
                          },
                          icon: Icon(Icons.add_outlined, color: Colors.white),
                        )
                      ],
                    ),
                    SizedBox(height: 5.h),
                    Container(
                      padding: EdgeInsets.all(12.r),
                      decoration: BoxDecoration(
                        color: boxBackgroundColor,
                        borderRadius: BorderRadius.circular(10.r),
                      ),
                      child: Column(
                        children: [
                          ...List.generate(
                              steps,
                              (index) => _buildInput(
                                  "${index + 1}단계 이름",
                                  "${index + 1}단계 설명",
                                  controllers[index + 2],
                                  controllers[index + 3])),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Container(
              width: double.maxFinite,
              child: ElevatedButton(
                onPressed: () {},
                child: Text(
                  "만들기 완료",
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10.r),
                  ),
                  backgroundColor: c900,
                ),
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildInput(
      String title,
      String subTitle,
      TextEditingController titleController,
      TextEditingController subController) {
    return Container(
      width: double.maxFinite,
      margin: EdgeInsets.only(bottom: 10.h),
      child: Column(
        children: [
          TextFormField(
            controller: titleController,
            decoration: InputDecoration(
              labelText: title,
              labelStyle: TextStyle(
                fontSize: 18.sp,
                fontWeight: FontWeight.w400,
                color: fontColor,
              ),
              focusColor: c800,
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: c800, width: 2.0),
              ),
              focusedBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: c800, width: 2.0),
              ),
            ),
            style: TextStyle(
              color: fontColor,
            ),
            cursorColor: c800,
          ),
          TextFormField(
            controller: subController,
            decoration: InputDecoration(
              labelText: subTitle,
              labelStyle: TextStyle(
                fontSize: 18.sp,
                fontWeight: FontWeight.w400,
                color: fontColor,
              ),
              focusColor: c800,
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: c800, width: 2.0),
              ),
              focusedBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: c800, width: 2.0),
              ),
            ),
            style: TextStyle(
              color: fontColor,
            ),
            cursorColor: c800,
          ),
        ],
      ),
    );
  }
}
