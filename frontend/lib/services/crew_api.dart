import 'package:reme/services/mydio.dart';

MyDio dio = MyDio();

Future<dynamic> getJoinedCrewList() async {
  final response = await dio.get('/crew/my-crews/');
  return response.data;
}

Future<dynamic> joinCrew(String crewId) async {
  final response = await dio.post('/crew/$crewId/request-join/', null);
  return response;
}

Future<dynamic> acceptJoinRequest(String crewId, String userId) async {
  final response = await dio.post('/crew/$crewId/accept_member/$userId/', null);
  return response;
}

Future<dynamic> rejectJoinRequest(String crewId, String userId) async {
  final response = await dio.post('/crew/$crewId/reject_member/$userId/', null);
  return response;
}

Future<dynamic> getCrewList() async {
  final response = await dio.get('/crew/');
  return response;
}
