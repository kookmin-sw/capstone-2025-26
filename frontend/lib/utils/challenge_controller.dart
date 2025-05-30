import 'package:get/get.dart';

class ChallengeController {
  List<dynamic> challengeList = [].obs;
  List<dynamic> crewChallengeList = [].obs;
  Map<String, dynamic> idchallenge = {};

  void setChallengeList(List<dynamic> challenge) {
    this.challengeList = challenge;
    for (var item in challenge) {
      idchallenge[item['id'].toString()] = item['challenge_name'];
    }
  }
}
