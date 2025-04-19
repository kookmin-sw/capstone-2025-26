import 'package:flutter/material.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart';
import 'package:reme/themes/color.dart';

class BoxUserInfo extends StatefulWidget {
  String name;
  ImageProvider? profileImg;
  BoxUserInfo({super.key, required this.name, this.profileImg});

  @override
  State<BoxUserInfo> createState() => _BoxUserInfoState(this.name, this.profileImg);
}

class _BoxUserInfoState extends State<BoxUserInfo> {
  String name;
  ImageProvider? profileImg;
  bool isProfile = false; // 프로필 사진이 넘어 왔는지 저장
  _BoxUserInfoState(this.name,this.profileImg);
  @override
  Widget build(BuildContext context) {
    if(this.profileImg == null){
      this.profileImg = Svg('assets/img/account_circle.svg');
    }else isProfile = true;
    return Container(
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: c950,
            radius: 32.63,
            child: CircleAvatar(
              // 여기에 사용자 이미지
              foregroundImage: profileImg,
              backgroundColor: (isProfile == true)? null : Colors.white,
              radius: 28.64,
            ),
          ),
          SizedBox(
            width: 10,
          ),
          Text(
            name,
            style: TextStyle(
              color: fontColor,
              fontWeight: FontWeight.w800,
              fontSize: 18
            ),
          ),
          Spacer(),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: dark,

            ),
              onPressed: (){},
              child: Text(
                "팔로우",
                style: TextStyle(
                  color: fontColor,
                  fontSize: 13,
                  fontWeight: FontWeight.w300,

                ),
              ),
            )
        ],
      ),
    );
  }
}
