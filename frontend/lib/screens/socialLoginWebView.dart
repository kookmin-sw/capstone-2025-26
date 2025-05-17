import 'package:flutter/material.dart';
import 'package:reme/models/user_info.dart';
import 'package:reme/utils/secret.dart';
import 'package:webview_flutter/webview_flutter.dart';

class SocialLoginWebView extends StatefulWidget {
  String social;
  SocialLoginWebView({super.key, required this.social});

  @override
  State<SocialLoginWebView> createState() => _WebViewState(social);
}

class _WebViewState extends State<SocialLoginWebView>
    with SingleTickerProviderStateMixin {
  String service;
  String? access_token;
  String? refresh_token;
  int loading = 0;
  late WebViewController _webViewController;
  bool showWebView = true;

  _WebViewState(this.service);

  Future<String> parseToken(int where) async {
    String s_where = where.toString();
    final result = await _webViewController.runJavaScriptReturningResult("""
        var spans = document.querySelectorAll('.prettyprint')[1];
        spans.querySelectorAll('span')[$s_where].innerText
      """) as String;
    return result;
  }

  @override
  void initState() {
    super.initState();
    _webViewController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(NavigationDelegate(
        onNavigationRequest: (request) {
          final url = request.url;
          if (url.contains("/callback/")) {
            setState(() {
              showWebView = false;
            });
          }
          return NavigationDecision.navigate;
        },
        onPageStarted: (url) {
          setState(() {
            loading = 0;
          });
        },
        onProgress: (int percent) {
          setState(() {
            loading = percent;
          });
        },
        onPageFinished: (String url) async {
          if (url.contains("/callback/")) {
            try {
              access_token = await parseToken(118);
              refresh_token = await parseToken(112);
              refresh_token =
                  refresh_token!.replaceAll('\\', "").replaceAll("\"", "");
              access_token =
                  access_token!.replaceAll('\\', "").replaceAll("\"", "");
              String user_name = await parseToken(76);
              String id = await parseToken(14);
              String email = await parseToken(69);
              String profile_image = await parseToken(88);
              await Future.delayed(const Duration(milliseconds: 500));
              Navigator.pop(
                  context,
                  UserInfo(
                    access_token,
                    refresh_token,
                    user_name,
                    email,
                    id,
                    profile_image,
                  ));
            } catch (e) {
              print(e is Error);
              Navigator.pop(context, e);
            }
          }
        },
      ))
      ..loadRequest(Uri.parse(api_baseUrl + '/' + service! + '/login'));
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Container(
        color: Colors.white,
        child: Stack(
          children: [
            if (showWebView) WebViewWidget(controller: _webViewController),
            if (!showWebView || loading < 100.0)
              const Center(
                child: CircularProgressIndicator(
                  backgroundColor: Colors.white,
                  strokeWidth: 10,
                  color: Colors.black,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
