// models/retrospect_challenge_model.dart
class RetrospectChallenge {
  final int id;
  final String challengeName;
  final String? description;
  final DateTime? completedAt;
  final String status;
  final bool hasRetrospect;
  final DateTime createdAt;
  final DateTime updatedAt;

  RetrospectChallenge({
    required this.id,
    required this.challengeName,
    this.description,
    this.completedAt,
    required this.status,
    required this.hasRetrospect,
    required this.createdAt,
    required this.updatedAt,
  });

  factory RetrospectChallenge.fromJson(Map<String, dynamic> json) {
    return RetrospectChallenge(
      id: json['id'] as int,
      challengeName: json['challenge_name'] as String,
      description: json['description'] as String?,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
      status: json['status'] as String,
      hasRetrospect: json['has_retrospect'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'challenge_name': challengeName,
      'description': description,
      'completed_at': completedAt?.toIso8601String(),
      'status': status,
      'has_retrospect': hasRetrospect,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class RetrospectChallengeResponse {
  final int count;
  final List<RetrospectChallenge> results;
  final String? next;
  final String? previous;

  RetrospectChallengeResponse({
    required this.count,
    required this.results,
    this.next,
    this.previous,
  });

  factory RetrospectChallengeResponse.fromJson(Map<String, dynamic> json) {
    return RetrospectChallengeResponse(
      count: json['count'] as int,
      results: (json['results'] as List<dynamic>)
          .map((item) =>
              RetrospectChallenge.fromJson(item as Map<String, dynamic>))
          .toList(),
      next: json['next'] as String?,
      previous: json['previous'] as String?,
    );
  }
}
