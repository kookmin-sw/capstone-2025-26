import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
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
                child: Image(image: AssetImage('assets/img/kakao_login_large_narrow.png'), height: 70,),
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => SocialLoginWebView(social: "kakao")
                      )
                  ).then((data){
                    // 데이터가 넘어오지 않을 때 1초간 SnackBar 띄움.
                    if(data != null) {
                      const storage = FlutterSecureStorage(); // accessToken과 refreshToken을 저장하는 SecrueStorage
                      storage.write(key: 'AccessToken', value: data.accessToken);
                      storage.write(key: 'RefreshToken', value: data.refreshToken);
                      Navigator.pushNamedAndRemoveUntil(context, "/", (route) => false);
                    }else{
                      // Toast Message
                      ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                              content: Text("Login Failed"),
                            duration: Duration(seconds: 1),
                          )
                      );
                    }
                  });
                },
              ),
              SizedBox(height: 50,),
              InkWell(
                child: Image(image: AssetImage('assets/img/naver_login.png'),height: 75,),
                onTap: (){
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => SocialLoginWebView(social: "naver")
                      )
                  ).then((data){
                    const storage = FlutterSecureStorage(); // accessToken과 refreshToken을 저장하는 SecrueStorage
                    storage.write(key: 'AccessToken', value: data.accessToken);
                    storage.write(key: 'RefreshToken', value: data.refreshToken);
                    Navigator.pushNamedAndRemoveUntil(context, "/", (route)=>false);
                  });
                },
              )
            ],
          ),
        ),
      ),
    );
  }
}
