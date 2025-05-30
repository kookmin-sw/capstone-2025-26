import 'package:get/get.dart';

class ChallengeController {
  List<dynamic> challengeList = [].obs;
  List<dynamic> crewChallengeList = [].obs;

  void setChallengeList(List<dynamic> challenge) {
    this.challengeList = challenge;
  }
}
