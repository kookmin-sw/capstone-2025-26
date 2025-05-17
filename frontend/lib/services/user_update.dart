import 'dart:io';

import 'package:reme/services/mydio.dart';

final MyDio dio = MyDio();

Future<dynamic> updateUser(
    {required String id,
    String? email,
    String? password,
    String? username,
    File? profile_image}) async {
  String? profile_image_link;
  if (profile_image != null) {
    _uploadProfileImage(profile_image).then((value) {
      profile_image_link = value;
    });
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

Future<dynamic> _uploadProfileImage(File image) async {
  // TODO: 프로필 이미지 업로드 작업
}
