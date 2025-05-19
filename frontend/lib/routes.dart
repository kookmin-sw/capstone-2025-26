import 'package:reme/screens/crewDetail.dart';
import 'package:reme/screens/guidePage.dart';
import 'package:reme/screens/initialPage.dart';
import 'package:reme/screens/login.dart';
import 'package:reme/screens/signupPage.dart';
import 'package:reme/screens/retrospectChallengeList.dart';
import 'package:reme/screens/retrospect_completion_screen.dart';
import 'package:reme/screens/create_challenge_name_screen.dart';
import 'package:reme/screens/create_challenge_plan_screen.dart';
import 'package:reme/screens/create_challenge_waiting_screen.dart';
import 'package:reme/screens/challenge_plan_completed_screen.dart';

class Routes {
  static const splash = "/main";
  static const login = "/login";
  static const signup = "/signup";
  static const crew = "/crew";
  static const retrospectChallenge = "/retrospect-challenge";
  static const retrospectCompletion = "/retrospect-completion";
  static const first = "/first";
  static const createChallengeName = "/create-challenge-name";
  static const createChallengePlan = "/create-challenge-plan";
  static const createChallengeWaiting = "/create-challenge-waiting";
  static const challengePlanCompleted = "/challenge_plan_completed";
}

var namedRoute = {
  Routes.splash: (context) => const Initialpage(),
  Routes.login: (context) => const LoginPage(),
  Routes.signup: (context) => const SignupPage(),
  Routes.crew: (context) => const CrewDetail(),
  Routes.first: (context) => const GuidePage(),
  Routes.retrospectChallenge: (context) => const RetrospectChallengeList(),
  Routes.retrospectCompletion: (context) => const RetrospectCompletionScreen(),
  Routes.createChallengeName: (context) => const CreateChallengeNameScreen(),
  Routes.createChallengePlan: (context) => const CreateChallengePlanScreen(),
  Routes.createChallengeWaiting: (context) =>
      const CreateChallengeWaitingScreen(),
  Routes.challengePlanCompleted: (context) =>
      const ChallengePlanCompletedScreen(),
};
