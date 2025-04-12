import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:reme/models/tokens.dart';
import 'package:reme/screens/socialLoginWebView.dart';

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
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => SocialLoginWebView(social: "kakao")
                      )
                  ).then((data){
                    const storage = FlutterSecureStorage(); // accessToken과 refreshToken을 저장하는 SecrueStorage
                    storage.write(key: 'AccessToken', value: data.accessToken);
                    storage.write(key: 'RefreshToken', value: data.refreshToken);
                    Navigator.pushNamedAndRemoveUntil(context, "/", (route)=>false);
                  });
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
