import 'package:get/get.dart';

class UserInfoController extends GetxController {
  final userInfo = <String, dynamic>{}.obs;

  void setUserInfo(
      String id, String username, String email, String? profileImage) {
    userInfo['id'] = id;
    userInfo['username'] = username;
    userInfo['email'] = email;
    userInfo['profile_image'] = profileImage;
  }

  Map<String, dynamic> getUserInfo() {
    return userInfo;
  }

  void updateUserInfo(String key, dynamic value) {
    userInfo[key] = value;
  }
}
