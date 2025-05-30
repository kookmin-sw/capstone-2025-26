import 'dart:convert';

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

  Map<String, dynamic> jsonData = {};

  _WebViewState(this.service);

  Future<String> extractJson() async {
    String result = await _webViewController.runJavaScriptReturningResult("""
    document.querySelectorAll('.prettyprint')[1].innerText
  """) as String;
    final start = result.indexOf('{');
    final end = result.lastIndexOf('}');
    if (start == -1 || end == -1 || end <= start) {
      throw Exception('JSON 부분을 찾을 수 없음');
    }
    result = result.substring(start, end + 1);

    return result
        .replaceAll('\\n', '')
        .replaceAll('\\"', '"')
        .replaceAll('\\\\', '\\');
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
            if (mounted) {
              setState(() {
                showWebView = false;
              });
            }
          }
          return NavigationDecision.navigate;
        },
        onPageStarted: (url) {
          if (mounted) {
            setState(() {
              loading = 0;
            });
          }
        },
        onProgress: (int percent) {
          if (mounted) {
            setState(() {
              loading = percent;
            });
          }
        },
        onPageFinished: (String url) async {
          if (url.contains("/api/${service}/callback/")) {
            try {
              extractJson().then((json) async {
                jsonData = jsonDecode(json);
                access_token = jsonData['access'];
                refresh_token = jsonData['refresh'];
                String? user_name = jsonData['user']['username'];
                String? email = jsonData['user']['email'];
                String id = jsonData['user']['id'].toString();
                String? profile_image = jsonData['user']['profile_image'];
                String dateTime = jsonData['user']['date_joined'].split('T')[0];
                DateTime joinedDate = DateTime.parse(dateTime);

                bool needSignup = joinedDate.isAtSameMomentAs(DateTime(
                    DateTime.now().year,
                    DateTime.now().month,
                    DateTime.now().day));
                await Future.delayed(const Duration(milliseconds: 500));
                if (mounted) {
                  Navigator.pop(
                      context,
                      UserInfo(
                        access_token,
                        refresh_token,
                        user_name,
                        email,
                        id,
                        profile_image,
                        needSignup,
                      ));
                }
              });
            } catch (e) {
              print(e is Error);
              if (mounted) {
                Navigator.pop(context, e);
              }
            }
          } else {
            if (mounted) {
              setState(() {
                loading = 0;
              });
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
