import 'package:get/get.dart';

class CrewController extends GetxController {
  var joinedCrew = <dynamic>[].obs; // 가입한 크루 목록
  var notJoinedCrew = <dynamic>[].obs; // 가입하지 않은 크루 목록

  void setJoinedCrewList(List<dynamic> crew) {
    joinedCrew.value = crew;
  }

  List<dynamic> getJoinedCrewList() {
    return joinedCrew;
  }

  void addJoinedCrew(dynamic crew) {
    joinedCrew.add(crew);
  }

  void setNotJoinedCrewList(List<dynamic> crew) {
    notJoinedCrew.clear();
    for (var c in crew) {
      if (!joinedCrew.any((e) => e['id'] == c['id'])) {
        notJoinedCrew.add(c);
      }
    }
  }

  List<dynamic> getNotJoinedCrewList() {
    return notJoinedCrew;
  }
}
