import 'dart:io';

import 'package:get/get.dart';
import 'package:reme/services/mydio.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:reme/utils/user_info_controller.dart';

MyDio dio = MyDio();

Future<dynamic> updateUser(
    {required String id,
    String? email,
    String? password,
    String? username,
    File? profile_image}) async {
  String? profile_image_link;
  if (profile_image != null) {
    profile_image_link = await uploadProfileImage(profile_image, 0, null);
  }
  try {
    final response = await dio.patch('/users/${id}/', {
      if (email != null) 'email': email,
      if (password != null) 'password': password,
      if (username != null) 'username': username,
      if (profile_image_link != null) 'profile_image': profile_image_link,
    });
    return response;
  } catch (e) {
    print(e);
  }
}

Future<String> uploadProfileImage(File image, int type, int? crew_id) async {
  try {
    final storage = FirebaseStorage.instance;
    final ref;
    final id = Get.find<UserInfoController>().userInfo['id'];

    switch (type) {
      case 0:
        ref = storage.ref().child('userprofile').child('${id}profile.png');
        break;
      case 1:
        ref = storage.ref().child('crewprofile').child('${crew_id}profile.png');
        break;
      case 2:
        ref = storage.ref().child('crewback');
        break;
      case 3:
        ref = storage.ref().child('challengeimage');
        break;
      default:
        ref = storage.ref();
        break;
    }

    // 메타데이터 설정
    final metadata = SettableMetadata(
      contentType: 'image/png',
      customMetadata: {'picked-file-path': image.path},
    );

    // 파일 업로드
    final uploadTask = await ref.putFile(image, metadata);

    // 업로드 완료 후 URL 가져오기
    final downloadURL = await uploadTask.ref.getDownloadURL();

    return downloadURL;
  } catch (e) {
    print('이미지 업로드 에러: $e');
    rethrow;
  }
}

Future<dynamic> getUserInfo() async {
  // TODO: 유저 정보 가져오기
  final response = await dio.get('/users/user_info/');
  return response.data;
}

Future<dynamic> getChallengeList({required int filter}) async {
  // filter 0: 개인, 1: 크루
  // TODO: 챌린지 목록 가져오기
  final response = await dio.get('/retrospect/challenges/');
  return response.data;
}
