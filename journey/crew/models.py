from django.db import models

class CrewMembershipRole(models.TextChoices):
    CREATOR = 'CREATOR', 'Creator'
    PARTICIPANT = 'PARTICIPANT', 'Participant'

class CrewMembershipStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'


class Crew(models.Model):
    """크루 모델"""
    crew_name = models.CharField(max_length=255, unique=True)
    crew_description = models.TextField(blank=True)
    member_count = models.IntegerField(default=0) # 멤버십 상태 변경 시 업데이트 필요
    crew_image = models.URLField(max_length=2048, null=True, blank=True)

    def __str__(self):
        return self.crew_name

class CrewMembership(models.Model):
    """사용자와 크루의 관계 (멤버십)"""
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='crew_memberships')
    crew = models.ForeignKey('crew.Crew', on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=CrewMembershipRole.choices, default=CrewMembershipRole.PARTICIPANT)
    status = models.CharField(max_length=20, choices=CrewMembershipStatus.choices, default=CrewMembershipStatus.PENDING)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'crew') # 사용자는 한 크루에 한 번만 가입 가능

    def __str__(self):
        return f"{self.user} - {self.crew} ({self.get_status_display()})"