import 'package:reme/services/mydio.dart';

MyDio dio = MyDio();

Future<dynamic> getJoinedCrewList() async {
  final response = await dio.get('/crew/crews/my-crews/');
  return response.data;
}

Future<dynamic> joinCrew(String crewId) async {
  final response = await dio.post('/crew/crews/$crewId/request-join/', null);
  return response;
}

Future<dynamic> acceptJoinRequest(String crewId, String userId) async {
  final response =
      await dio.post('/crew/crews/$crewId/accept_member/$userId/', null);
  return response;
}

Future<dynamic> rejectJoinRequest(String crewId, String userId) async {
  final response =
      await dio.post('/crew/crews/$crewId/reject_member/$userId/', null);
  return response;
}

Future<dynamic> getCrewList() async {
  final response = await dio.get('/crew/crews/');
  return response;
}

Future<dynamic> getCrewDeatil(int crewId) async {
  final response = await dio.get('/crew/crews/${crewId.toString()}/');
  return response;
}

Future<dynamic> getMyCrewMembership() async {
  final response = await dio.get('/crew/memberships/my-memberships/');
  return response;
}
