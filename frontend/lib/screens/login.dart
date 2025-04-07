import 'package:flutter/material.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        padding: EdgeInsets.all(10),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                "Re:Me",
                style: TextStyle(
                  fontSize: 27,
                  fontWeight: FontWeight.bold
                ),
              ),
              SizedBox(
                height: 100,
              ),
              InkWell(
                child: Image(image: AssetImage('assets/img/kakao_login_large_wide.png')),
                onTap: (){
                  print("카카오 로그인 눌림");
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
