import 'package:reme/screens/crewDetail.dart';
import 'package:reme/screens/guidePage.dart';
import 'package:reme/screens/initialPage.dart';
import 'package:reme/screens/login.dart';
import 'package:reme/screens/my_page.dart';
import 'package:reme/screens/signupPage.dart';
import 'package:reme/screens/retrospectChallengeList.dart';
import 'package:reme/screens/retrospect_completion_screen.dart';

class Routes {
  static const splash = "/main";
  static const login = "/login";
  static const signup = "/signup";
  static const crew = "/crew";
  static const retrospectChallenge = "/retrospect-challenge";
  static const retrospectCompletion = "/retrospect-completion";
  static const first = "/first";
  static const myPage = "/my-page";
}

var namedRoute = {
  Routes.splash: (context) => Initialpage(),
  Routes.login: (context) => LoginPage(),
  Routes.signup: (context) => SignupPage(),
  Routes.crew: (context) => CrewDetail(),
  Routes.first: (context) => GuidePage(),
  Routes.retrospectChallenge: (context) => const RetrospectChallengeList(),
  Routes.retrospectCompletion: (context) => const RetrospectCompletionScreen(),
  Routes.myPage: (context) => MyPage(),
};
