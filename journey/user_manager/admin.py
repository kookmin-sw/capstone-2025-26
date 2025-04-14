from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    #목록에 표시될 필드
    list_display = ("email", "nickname", "is_staff", "is_superuser", "provider", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "provider")

    #검색 가능 필드
    search_fields = ("email", "nickname")

    #정렬 기준
    ordering = ("-date_joined",)

    #유저 상세 보기/edit 페이지 구성
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인 정보", {"fields": ("nickname", "profile_image", "provider")}),
        ("권한 설정", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("로그 기록", {"fields": ("last_login", "date_joined")}),
    )

    #유저 생성 페이지 구성 (createsuperuser처럼)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nickname", "password1", "password2", "is_staff", "is_superuser", "is_active"),
        }),
    )
