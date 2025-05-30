import 'package:get/get_rx/get_rx.dart';

class RetrospectController {
  List<dynamic> retrospectList = [].obs;

  void setRetrospectList(List<dynamic> retrospectList) {
    this.retrospectList = retrospectList;
  }
}
