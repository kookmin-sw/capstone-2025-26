import 'package:reme/screens/crewDetail.dart';
import 'package:reme/screens/initialPage.dart';
import 'package:reme/screens/login.dart';
import 'package:reme/screens/signupPage.dart';

class Routes {
  static const splash = "/";
  static const login = "/login";
  static const signup = "/signup";
  static const crew = "/crew";
}

var namedRoute = {
  Routes.splash: (context) => const Initialpage(),
  Routes.login: (context) => const LoginPage(),
  Routes.signup: (context) => const SignupPage(),
  Routes.crew: (context) => const CrewDetail(),
};
