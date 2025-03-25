from rest_framework import status
from rest_framework.response import Response
from .serializer import KakaoUserSerializer, UserSerializer
from .models import User, Provider
from token_manager.serializer import CustomTokenObtainPairSerializer
import random

class OAuthUserManager:
    def __init__(self):
        pass

    def create_kakao_user(self, sub, nickname, email=None):
        try:
            if not email:
                email = f"{sub}@kakao.com"
            user = User.objects.filter(email=email)
            has_user = user.count() > 0
            if has_user:
                refresh = CustomTokenObtainPairSerializer.get_token(user.first())
                return refresh, user.first()
            else:
                ## give random unusable password
                password = email + str(random.random())[3:]
                kakao = Provider.objects.filter(domail='kakao.com')
                has_provider = kakao.count()
                if has_provider:
                    kakao = kakao[0]
                else:
                    kakao = Provider.objects.create(domain='kakao.com', name='kakao')
                serializer = UserSerializer(data={'email': email, 'nickname': nickname, 'password': password, 'provider': kakao.id})
                if serializer.is_valid():
                    user = serializer.save()
                    user.is_active = True
                    user.save()
                    refresh = CustomTokenObtainPairSerializer.get_token(user)
                    return refresh, user
            return None, None
        except Exception as e:
            return None, None
        
    def create_naver_user(self, id, nickname, email=None):
        print(id, email, nickname)
        try:
            if not email:
                email = f"{id}@naver.com"
            user = User.objects.filter(email=email)
            has_user = user.count() > 0
            if has_user:
                refresh = CustomTokenObtainPairSerializer.get_token(user.first())
                return refresh, user.first()
            else:
                ## give random unusable password
                password = email + str(random.random())[3:]
                naver = Provider.objects.filter(domain='naver.com')
                has_provider = naver.count()
                if has_provider:
                    naver = naver[0]
                else:
                    naver = Provider.objects.create(domain='naver.com', name='naver')
                print(naver)
                print(email, nickname, password)
                serializer = UserSerializer(data={'email': email, 'nickname': nickname, 'password': password, 'provider': naver.id})
                if serializer.is_valid():
                    user = serializer.save()
                    user.is_active = True
                    user.save()
                    refresh = CustomTokenObtainPairSerializer.get_token(user)
                    return refresh, user
                return None, None
        except Exception as e:
            return None, None