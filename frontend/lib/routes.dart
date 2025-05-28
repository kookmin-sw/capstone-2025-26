import 'package:reme/screens/add_post.dart';
import 'package:reme/screens/add_template.dart';
import 'package:reme/screens/crew_admin_page.dart';
import 'package:reme/screens/crewDetail.dart';
import 'package:reme/screens/guidePage.dart';
import 'package:reme/screens/initialPage.dart';
import 'package:reme/screens/login.dart';
import 'package:reme/screens/my_page.dart';
import 'package:reme/screens/notification_list_page.dart';
import 'package:reme/screens/retrospect_detail.dart';
import 'package:reme/screens/signupPage.dart';
import 'package:reme/screens/retrospectChallengeList.dart';
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
  static const first = "/first";
  static const createChallengeName = "/create-challenge-name";
  static const createChallengePlan = "/create-challenge-plan";
  static const createChallengeWaiting = "/create-challenge-waiting";
  static const challengePlanCompleted = "/challenge_plan_completed";
  static const myPage = "/my-page";
  static const notificationList = "/notification-list";
  static const addPost = "/add-post";
  static const crewAdmin = "/crew-admin";
  static const retrospectDetail = "/retrospect-detail";
  static const addTemplate = "/add-template";
}

var namedRoute = {
  Routes.splash: (context) => const Initialpage(),
  Routes.login: (context) => LoginPage(),
  Routes.signup: (context) => const SignupPage(),
  Routes.crew: (context) => const CrewDetail(),
  Routes.first: (context) => GuidePage(),
  Routes.createChallengeName: (context) => const CreateChallengeNameScreen(),
  Routes.createChallengePlan: (context) => const CreateChallengePlanScreen(),
  Routes.createChallengeWaiting: (context) =>
      const CreateChallengeWaitingScreen(),
  Routes.challengePlanCompleted: (context) =>
      const ChallengePlanCompletedScreen(),
  Routes.myPage: (context) => MyPage(),
  Routes.notificationList: (context) => NotificationListPage(),
  Routes.addPost: (context) => AddPost(),
  Routes.crewAdmin: (context) => CrewAdminPage(),
  Routes.retrospectDetail: (context) => RetrospectDetail(),
  Routes.addTemplate: (context) => AddTemplate(),
};
