import 'package:reme/services/mydio.dart';

MyDio dio = MyDio();

Future<dynamic> getRetrospectList({int? crew_id, int? challenge_id}) async {
  final response = await dio.get('/retrospect/kpi-results/');
  return response.data;
}

Future<dynamic> getRetrospectDetail(int retrospect_id) async {
  final response = await dio.get('/retrospect/retrospects/$retrospect_id/');
  return response.data;
}

Future<void> createRetrospect(
    {int? crew_id,
    required int challenge_id,
    required int template_id,
    required Map<String, dynamic> content}) async {
  bool isCrew = false;
  if (crew_id != null) {
    isCrew = true;
  }

  final response = await dio.post('/retrospect/retrospects/', {
    'crew': isCrew ? crew_id : null,
    'challenge': challenge_id,
    'template': template_id,
    'content': content,
    'visibility': "PRIVATE",
    'owner_type': isCrew ? "CREW" : "USER",
    'initial_plan_description': 'asdf', // 추후 지울 필요 있음.
  });
  return response.data;
}

Future<dynamic> getTemplateList() async {
  final response = await dio.get('/retrospect/templates/');
  return response.data['results'];
}

Future<dynamic> setVisibility(
    {required int retrospect_id,
    required String visibility,
    int? crew_id}) async {
  final response = await dio.patch('/retrospect/retrospects/$retrospect_id/', {
    'visibility': visibility,
  });
  return response.data;
}

Future<dynamic> getKpiResult(
    {required int challenge_id, required DateTime date, int count = 0}) async {
  if (count > 5) return [];
  final response =
      await dio.get('/retrospect/kpi-results/by-challenge/$challenge_id/');

  if (response.data.isEmpty) {
    await Future.delayed(const Duration(milliseconds: 800));
    return getKpiResult(
        challenge_id: challenge_id, date: date, count: count + 1);
  } else {
    List<dynamic> kpiResult = [];
    for (var result in response.data) {
      if (result['created_at'].split('T')[0] == date.toString().split(' ')[0]) {
        kpiResult.add(result);
      }
    }

    return kpiResult;
  }
}
