from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import random, string

class NotificationType(models.TextChoices):
    INVITE_CREW = 'INVITE_CREW', 'Crew Invitation'
    REQUEST_JOIN_CREW = 'REQUEST_JOIN_CREW', 'Crew Join Request'
    ACCEPT_JOIN_CREW = 'ACCEPT_JOIN_CREW', 'Crew Join Accepted'
    REJECT_JOIN_CREW = 'REJECT_JOIN_CREW', 'Crew Join Rejected'
    WEEKLY_ANALYSIS_DONE = 'WEEKLY_ANALYSIS_DONE', 'Weekly Analysis Completed'
    # ... 기타 필요한 타입
    ETC = 'ETC', 'Etc'


class Provider(models.Model):
    domain = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=50)
def generate_unique_uid():
    """4자리 고유 UID 생성"""
    while True:
        # 4자리 숫자 생성
        uid = ''.join(random.choices(string.digits, k=4))
        # 중복 체크
        if not User.objects.filter(uid=uid).exists():
            return uid
   
class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=False,  
        null=True,     
        blank=True,    
        default=None   
    )
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True)
    uid = models.CharField(max_length=255, unique=True, null=True, blank=True) # Firebase UID
    # Add Extra user fields here
    profile_image = models.URLField(max_length=2048, null=True, blank=True)

    def __str__(self):
        return self.nickname or self.email

    def save(self, *args, **kwargs):
    # 신규 사용자이고 UID가 없는 경우에만 생성
        if not self.pk and not self.uid:
            self.uid = generate_unique_uid()
        super().save(*args, **kwargs)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Notification(models.Model):
    """알림 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications') # 알림 수신자
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    content = models.CharField(max_length=255) # 알림 내용
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # GenericForeignKey 설정 (관련 객체를 가리키기 위함)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True) # 관련된 모델 타입
    object_id = models.PositiveIntegerField(null=True, blank=True) # 관련된 객체의 PK
    related_object = GenericForeignKey('content_type', 'object_id') # 관련 객체에 직접 접근 가능

    def __str__(self):
        return f"Notification for {self.user}: {self.content[:50]}"