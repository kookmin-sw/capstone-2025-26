from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from rest_framework import status
import jwt
from user_manager.utils import OAuthUserManager
from user_manager.serializer import UserSerializer


class KakaoAuthorizeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        kakao_oauth_url = "https://kauth.kakao.com/oauth/authorize"
        client_id = settings.KAKAO_REST_API_KEY
        redirect_uri = settings.KAKAO_REDIRECT_URI

        params = {
            'client_id': client_id, 
            'redirect_uri': redirect_uri, 
            'response_type': 'code', 
        }
        url = f"{kakao_oauth_url}?{urlencode(params)}"
        return HttpResponseRedirect(url)
    
class KakaoCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        if code is None:
            return Response({"detail": 'no code in redirect url'}, status=status.HTTP_400_BAD_REQUEST)
        
        uri = "https://kauth.kakao.com/oauth/token"
        headers = {'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'}
        data = {
            'grant_type' : 'authorization_code',
            'client_id' : settings.KAKAO_REST_API_KEY,
            'redirect_uri' : settings.KAKAO_REDIRECT_URI,
            'code' : code,
        }
        try:
            response = requests.post(uri, data=data, headers=headers)
            if response.status_code == 200:
                # Login or Create User
                # enable id token from kakao developers(OIDC)
                # WIP - 회원가입인지 로그인인지 파악 후 처리 필요
                data = response.json()
                kakao_access_token = data['access_token']
                kakao_refresh_token = data['refresh_token']
                scope = data['scope']
                id_token = data.get('id_token')
                user_data = jwt.decode(id_token, options={"verify_signature": False})
                sub = user_data.get('sub')
                profile_image = user_data.get('profile_image')
                kakao_email = user_data.get('email')
                nickname = user_data.get('nickname')
                kakao_manager = OAuthUserManager()
                refresh, user = kakao_manager.create_kakao_user(sub=sub, email=kakao_email, nickname=nickname)
                if refresh: 
                    return Response({
                    'user': UserSerializer(user).data, 
                    'refresh': str(refresh), 
                    'access': str(refresh.access_token)
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'detail': 'user creation failed' }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'data': response.text}, status=response.status_code)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_408_REQUEST_TIMEOUT)