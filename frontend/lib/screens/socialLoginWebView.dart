import 'package:flutter/material.dart';
import 'package:reme/utils/secret.dart';
import 'package:webview_flutter/webview_flutter.dart';

class SocialLoginWebView extends StatefulWidget {
  String social;
  SocialLoginWebView({super.key, required this.social});

  @override
  State<SocialLoginWebView> createState() => _WebViewState(social);
}

class _WebViewState extends State<SocialLoginWebView> {
  String service;
  String? access_token;
  String? refresh_token;
  late WebViewController _webViewController;

  _WebViewState(this.service);

  Future<String> parseToken(int where) async{
    final result = await _webViewController.runJavaScriptReturningResult(
      "document.querySelectorAll('.str')["+where.toString()+"].innerText")as String;

    return result;
  }

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _webViewController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(NavigationDelegate(
          onPageFinished: (String url) async {
            print("loading 완료");
            if(url.contains("callback")){
              access_token = await parseToken(27);
              refresh_token = await parseToken(25);
              refresh_token = refresh_token!.replaceAll('\\', "").replaceAll("\"", ""); // parsing한 토큰 역슬레시와 따옴표 지우기
              access_token = access_token!.replaceAll('\\', "").replaceAll("\"", ""); // parsing한 토큰 역슬레시와 따옴표 지우기
              print("AccessToken: "+access_token!);
              print("RefreshToken: "+refresh_token!);
              Navigator.pop(context);
            }
          }
      ))
      ..loadRequest(Uri.parse(api_baseUrl+'/'+service!+'/login'));
  }
  @override
  Widget build(BuildContext context) {

    return SafeArea(
      child: WebViewWidget(
          controller: _webViewController
      ),
    );
  }
}


