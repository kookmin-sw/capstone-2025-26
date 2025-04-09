from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from . models import Provider, Notification 
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']

    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            pass
        else:
            raise serializers.ValidationError(
                _("credentials not provided"), code='data'
            )
        return attrs

class KakaoUserSerializer(serializers.ModelSerializer):
    provider = serializers.SlugRelatedField(
        queryset=Provider.objects.all(), 
        slug_field='name', 
        required=False, 
    )
    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'content', 'is_read', 'created_at', 'content_type', 'object_id']
        read_only_fields = ['id', 'created_at'] # User is now writable 