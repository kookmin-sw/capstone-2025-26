from django.db import models

# Create your models here.

# --- ENUM Choices ---
class TemplateOwnerType(models.TextChoices):
    USER = 'USER', 'User'
    CREW = 'CREW', 'Crew'
    COMMON = 'COMMON', 'Common' # 공통 템플릿 타입 추가

class ChallengeOwnerType(models.TextChoices):
    USER = 'USER', 'User'
    CREW = 'CREW', 'Crew'

class RetrospectOwnerType(models.TextChoices):
    USER = 'USER', 'User'
    CREW = 'CREW', 'Crew'

class ChallengeStatus(models.TextChoices):
    LIVE = 'LIVE', 'Live'
    SUCCESS = 'SUCCESS', 'Success'
    FAIL = 'FAIL', 'Fail'

class RetrospectVisibility(models.TextChoices):
    PRIVATE = 'PRIVATE', 'Private'
    CREW = 'CREW', 'Crew Only'
    PUBLIC = 'PUBLIC', 'Public'

class RetrospectWeeklyAnalysisOwnerType(models.TextChoices):
    USER = 'USER', 'User'
    CREW = 'CREW', 'Crew'


# --- Models ---


class Plan(models.Model):
    """챌린지 계획 모델"""
    plan_list = models.JSONField() # 계획 내용을 JSON 형태로 저장

    def __str__(self):
        # plan_list 내용 중 일부를 보여주거나 특정 필드를 사용
        return f"Plan {self.id}"

class Template(models.Model):
    """회고 템플릿 모델"""
    user = models.ForeignKey('user_manager.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='templates')
    crew = models.ForeignKey('crew.Crew', on_delete=models.SET_NULL, null=True, blank=True, related_name='templates')
    owner_type = models.CharField(max_length=10, choices=TemplateOwnerType.choices)
    name = models.CharField(max_length=255)
    steps = models.JSONField()

    def __str__(self):
        return self.name

class Challenge(models.Model):
    """챌린지 모델"""
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='challenges', null=True, blank=True)
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='challenges', null=True, blank=True) # 개인 챌린지일 경우
    crew = models.ForeignKey('crew.Crew', on_delete=models.CASCADE, related_name='challenges', null=True, blank=True) # 크루 챌린지일 경우
    challenge_name = models.CharField(max_length=255)
    deadline = models.DateTimeField()
    kpi_description = models.TextField(blank=True) # 기존 kpi 필드를 이름 변경하거나 대체
    kpi_metrics = models.JSONField(null=True, blank=True) # 구조화된 KPI 저장 (예: {"metric1": "...", "metric2": "..."})
    owner_type = models.CharField(max_length=10, choices=ChallengeOwnerType.choices)
    status = models.CharField(max_length=10, choices=ChallengeStatus.choices, default=ChallengeStatus.LIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.challenge_name

class UserChallengeStatus(models.Model):
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='challenge_statuses')
    challenge = models.ForeignKey('retrospect.Challenge', on_delete=models.CASCADE, related_name='user_statuses')
    # status choices는 Challenge 모델의 SUCCESS, FAIL과 연관될 수 있음
    status = models.CharField(max_length=10, choices=[('ACHIEVED', 'Achieved'), ('FAILED', 'Failed'), ('PENDING', 'Pending')], default='PENDING')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'challenge')
        indexes = [
            models.Index(fields=['user', 'challenge']),
        ]

class Retrospect(models.Model):
    """회고 모델"""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='retrospects')
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True, related_name='retrospects') # 템플릿 없이 작성 가능
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='retrospects') # 작성자
    crew = models.ForeignKey('crew.Crew', on_delete=models.CASCADE, related_name='retrospects', null=True, blank=True) # 크루 회고일 경우
    content = models.TextField()
    kpi_result = models.FloatField(null=True, blank=True) # 챌린지 KPI 결과
    visibility = models.CharField(max_length=10, choices=RetrospectVisibility.choices, default=RetrospectVisibility.PRIVATE)
    owner_type = models.CharField(max_length=10, choices=RetrospectOwnerType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Retrospect for {self.challenge} by {self.user}"

class RetrospectWeeklyAnalysis(models.Model):
    """주간 회고 분석"""
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='weekly_analyses', null=True, blank=True) # 개인 분석일 경우
    crew = models.ForeignKey('crew.Crew', on_delete=models.CASCADE, related_name='weekly_analyses', null=True, blank=True) # 크루 분석일 경우
    summary = models.JSONField() # 주간 분석 요약
    weekly_kpi = models.IntegerField(null=True, blank=True)
    start_date = models.DateField() # 주 시작일
    end_date = models.DateField() # 주 종료일 (week_end -> end_date)
    owner_type = models.CharField(max_length=10, choices=RetrospectWeeklyAnalysisOwnerType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        owner = self.user if self.owner_type == RetrospectWeeklyAnalysisOwnerType.USER else self.crew
        return f"Weekly Analysis for {owner} ({self.start_date} - {self.end_date})"
