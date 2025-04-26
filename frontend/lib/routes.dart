import 'package:reme/screens/crewDetail.dart';
import 'package:reme/screens/initialPage.dart';
import 'package:reme/screens/login.dart';

class Routes{
  static const splash = "/";
  static const login = "/login";
  static const crew = "/crew";
}

var namedRoute = {
  Routes.splash: (context) => Initialpage(),
  Routes.login: (context) => LoginPage(),
  Routes.crew: (context) => CrewDetail(),
};