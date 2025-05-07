import 'package:reme/screens/crewDetail.dart';
import 'package:reme/screens/guidePage.dart';
import 'package:reme/screens/initialPage.dart';
import 'package:reme/screens/login.dart';
import 'package:reme/screens/signupPage.dart';

class Routes {
  static const splash = "/";
  static const login = "/login";
  static const signup = "/signup";
  static const crew = "/crew";
  static const first = "/first";
}

var namedRoute = {
  Routes.splash: (context) => Initialpage(),
  Routes.login: (context) => LoginPage(),
  Routes.crew: (context) => CrewDetail(),
  Routes.first: (context) => GuidePage(),
};
