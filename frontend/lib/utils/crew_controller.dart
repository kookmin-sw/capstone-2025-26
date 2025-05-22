import 'package:get/get.dart';

class CrewController extends GetxController {
  final joinedCrew = <dynamic>[].obs;

  void setJoinedCrewList(List<dynamic> crew) {
    this.joinedCrew.value = crew;
  }

  List<dynamic> getJoinedCrewList() {
    return joinedCrew;
  }

  void addJoinedCrew(dynamic crew) {
    this.joinedCrew.add(crew);
  }
}
