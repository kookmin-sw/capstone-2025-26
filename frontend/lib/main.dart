import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:reme/routes.dart';
import 'package:posthog_flutter/posthog_flutter.dart';
import 'package:reme/themes/color.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> main() async {
  // init WidgetsFlutterBinding if not yet
  WidgetsFlutterBinding.ensureInitialized();
  final config =
      PostHogConfig('phc_vcpqApKqc66zUcHBBqPntqdLGrPwww4mcwtJ2M5nQ3l');
  config.debug = true;
  config.captureApplicationLifecycleEvents = true;
  // or EU Host: 'https://eu.i.posthog.com'
  config.host = 'https://us.i.posthog.com';
  await Posthog().setup(config);
  // 달력 locale을 위한 초기화
  await initializeDateFormatting();

  //sharedPreferences 설정
  SharedPreferences prefs = await SharedPreferences.getInstance();
  runApp(MyApp(prefs: prefs));
}

class MyApp extends StatelessWidget {
  final SharedPreferences prefs;
  MyApp({super.key, required this.prefs});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    bool? isFirstInstall = prefs.getBool("first_install");
    bool? isAccessToken = prefs.getBool("logined");
    String initialRoute = Routes.first;

    if (isFirstInstall == null) {
      initialRoute = Routes.first;
    } else if (isAccessToken == null) {
      initialRoute = Routes.login;
    } else {
      initialRoute = Routes.splash;
    }

    // 안드로이드 하단바 꾸미기
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        systemNavigationBarDividerColor: Colors.transparent, //하단바 디바이더 색상
        systemNavigationBarColor: boxBackgroundColor, //하단바 색상
      ),
    );

    return ScreenUtilInit(
      designSize: Size(414, 896),
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Flutter Demo',
        theme: ThemeData(
          // This is the theme of your application.
          //
          // TRY THIS: Try running your application with "flutter run". You'll see
          // the application has a purple toolbar. Then, without quitting the app,
          // try changing the seedColor in the colorScheme below to Colors.green
          // and then invoke "hot reload" (save your changes or press the "hot
          // reload" button in a Flutter-supported IDE, or press "r" if you used
          // the command line to start the app).
          //
          // Notice that the counter didn't reset back to zero; the application
          // state is not lost during the reload. To reset the state, use hot
          // restart instead.
          //
          // This works for code too, not just values: Most code changes can be
          // tested with just a hot reload.
          colorScheme: ColorScheme.fromSeed(seedColor: c500),
          useMaterial3: true,
          fontFamily: 'Pretendard',
        ),
        initialRoute: initialRoute,
        routes: namedRoute,
        themeMode: ThemeMode.dark,
      ),
    );
  }
}
