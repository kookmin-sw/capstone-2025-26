import 'package:flutter/material.dart';
import 'package:reme/models/tokens.dart';
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
  int loading = 0;
  late WebViewController _webViewController;

  _WebViewState(this.service);

  Future<String> parseToken(int where) async {
    final result = await _webViewController.runJavaScriptReturningResult(
        "document.querySelectorAll('.str')[$where].innerText") as String;

    return result;
  }

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _webViewController = WebViewController()
      ..setJavaScriptMode(
          JavaScriptMode.unrestricted) // WebView안에서 Javascript 실행할지
      ..setNavigationDelegate(NavigationDelegate(// Webview 설정
          onPageStarted: (url) {
        setState(() {
          loading = 0;
        });
      }, onProgress: (int percent) {
        setState(() {
          loading = percent;
        });
      }, onPageFinished: (String url) async {
        // 페이지가 로딩이 완료되었을 때
        setState(() {
          loading = 100;
        });
        if (url.contains("/callback/")) {
          try {
            access_token = await parseToken(27); // 파싱한 accessToken 위치
            refresh_token = await parseToken(25); // 파싱한 refreshToken 위치
            refresh_token = refresh_token!
                .replaceAll('\\', "")
                .replaceAll("\"", ""); // parsing한 토큰 역슬레시와 따옴표 지우기
            access_token = access_token!
                .replaceAll('\\', "")
                .replaceAll("\"", ""); // parsing한 토큰 역슬레시와 따옴표 지우기
            Navigator.pop(context, Tokens(access_token, refresh_token));
          } catch (e) {
            print(e);
          }
        }
      }))
      ..loadRequest(Uri.parse('$api_baseUrl/$service/login'));
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Stack(children: [
        if (loading < 100)
          Center(
            child: CircularProgressIndicator(
              value: loading / 100.0,
              strokeAlign: 40,
            ),
          ),
        WebViewWidget(controller: _webViewController),
      ]),
    );
  }
}
