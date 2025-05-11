from django.db import models
from django.conf import settings # Import settings to reference AUTH_USER_MODEL
from django.core.exceptions import ValidationError

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

class KpiDataType(models.TextChoices):
    FLOAT = 'FLOAT', 'Float'
    INTEGER = 'INTEGER', 'Integer'
    TEXT = 'TEXT', 'Text'
    BOOLEAN = 'BOOLEAN', 'Boolean'


# --- Models ---


class Plan(models.Model):
    """챌린지 계획 모델"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plans', null=True, blank=True)
    challenge = models.ForeignKey('Challenge', on_delete=models.CASCADE, related_name='plans', null=True, blank=True)
    plan_text = models.TextField(null=True, blank=True)  # 계획 내용을 텍스트 형태로 저장
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Plan {self.id}" if not self.challenge else f"Plan for {self.challenge.challenge_name}"

class Template(models.Model):
    """회고 템플릿 모델"""
    user = models.ForeignKey('user_manager.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='templates')
    crew = models.ForeignKey('crew.Crew', on_delete=models.SET_NULL, null=True, blank=True, related_name='templates') # 개인 회고 템플릿인 경우 NULL
    owner_type = models.CharField(max_length=10, choices=TemplateOwnerType.choices)
    name = models.CharField(max_length=255)
    steps = models.JSONField() # 회고 작성 예시

    TemplateOwnerType = TemplateOwnerType

    def __str__(self):
        return self.name

class Challenge(models.Model):
    """챌린지 모델"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenges', null=True, blank=True) # 개인 챌린지일 경우
    crew = models.ForeignKey('crew.Crew', on_delete=models.CASCADE, related_name='challenges', null=True, blank=True) # 크루 챌린지일 경우
    challenge_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True, default='') # 목표 설명 추가
    deadline = models.DateTimeField()
    owner_type = models.CharField(max_length=10, choices=ChallengeOwnerType.choices)
    status = models.CharField(max_length=10, choices=ChallengeStatus.choices, default=ChallengeStatus.LIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ChallengeOwnerType = ChallengeOwnerType

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
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='retrospects') # 계획 없이 작성 가능 , 따로 계획 안세우고 싶을수도 있으니까
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='retrospects')
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True, related_name='retrospects') # 템플릿 없이 작성 가능
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='retrospects') # 작성자
    crew = models.ForeignKey('crew.Crew', on_delete=models.CASCADE, related_name='retrospects', null=True, blank=True) # 크루 회고일 경우
    content = models.TextField()
    visibility = models.CharField(max_length=10, choices=RetrospectVisibility.choices, default=RetrospectVisibility.PRIVATE)
    owner_type = models.CharField(max_length=10, choices=RetrospectOwnerType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    RetrospectOwnerType = RetrospectOwnerType
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

    RetrospectWeeklyAnalysisOwnerType = RetrospectWeeklyAnalysisOwnerType

    def __str__(self):
        owner = self.user if self.owner_type == RetrospectWeeklyAnalysisOwnerType.USER else self.crew
        return f"Weekly Analysis for {owner} ({self.start_date} - {self.end_date})"

# --- New Models ---

class Kpi(models.Model):
    """KPI 정의 모델 (사용자별, 챌린지별)"""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='kpis')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kpis')
    name = models.CharField(max_length=255) # KPI 이름
    definition = models.TextField(blank=True, default='') # KPI 설명
    measurement_unit = models.CharField(max_length=50, blank=True, default='') # 측정 단위
    data_type = models.CharField(max_length=10, choices=KpiDataType.choices) # 데이터 유형
    measurement_method = models.TextField(blank=True, default='') # 측정 방법 (선택적)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('challenge', 'user', 'name') # 사용자, 챌린지별 KPI 이름은 고유해야 함
        indexes = [
            models.Index(fields=['challenge', 'user']),
        ]

    def __str__(self):
        return f"KPI '{self.name}' for {self.user} in {self.challenge}"

class KpiResult(models.Model):
    """
    회고(Retrospect)를 기반으로 KPI별 평가(스코어)를 기록하는 모델
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kpi_results')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='kpi_results')
    kpi = models.ForeignKey(Kpi, on_delete=models.CASCADE, related_name='kpi_results')
    retrospect = models.ForeignKey(Retrospect, on_delete=models.CASCADE, related_name='kpi_results')

    score = models.FloatField()  # 0 ~ 1 범위 권장
    comment = models.TextField(blank=True, null=True)  # 추가 설명
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "KPI Result"
        verbose_name_plural = "KPI Results"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'challenge', 'kpi', 'retrospect']),
        ]
        # 같은 (user, challenge, kpi, retrospect) 조합으로는 두 번 저장 불가
        # 즉, 같은 회고에 대해 같은 KPI에 대해 한 번만 기록 가능
        unique_together = ('user', 'challenge', 'kpi', 'retrospect')  



    def __str__(self):
        return f"Result for KPI '{self.kpi.name}' on retrospect {self.retrospect.id} (Score: {self.score:.2f})"
