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


class NaverAuthorizeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        naver_oauth_url = "https://nid.naver.com/oauth2.0/authorize"
        client_id = settings.NAVER_REST_API_KEY
        redirect_uri = settings.NAVER_REDIRECT_URI

        params = {
            'client_id': client_id, 
            'redirect_uri': redirect_uri, 
            'response_type': 'code', 
            'state': 'test', 
        }
        url = f"{naver_oauth_url}?{urlencode(params)}"
        return HttpResponseRedirect(url)
    
class NaverCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        if code is None:
            return Response({"detail": 'no code in redirect url'}, status=status.HTTP_400_BAD_REQUEST)
        
        uri = "https://nid.naver.com/oauth2.0/token"
        headers = {'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'}
        data = {
            'grant_type' : 'authorization_code',
            'client_id' : settings.NAVER_REST_API_KEY,
            'client_secret': settings.NAVER_SECRET_API_KEY, 
            'redirect_uri' : settings.NAVER_REDIRECT_URI,
            'code' : code, 
        }
        try:
            response = requests.post(uri, data=data, headers=headers)
            if response.status_code == 200:
                # Login or Create User
                data = response.json()
                naver_access_token = data['access_token']
                naver_refresh_token = data['refresh_token']
            else:
                return Response({'data': response.text}, status=response.status_code)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_408_REQUEST_TIMEOUT)
        uri = "https://openapi.naver.com/v1/nid/me"
        headers = {'Authorization': 'Bearer ' + naver_access_token}
        try:
            response = requests.get(uri, headers=headers)
            if response.status_code == 200:
                data = response.json()
                data = data.get('response')
                print(data)
                id = data.get('id')
                nickname = data.get('nickname')
                profile_image = data.get('profile_image')
                age = data.get('age')
                gender = data.get('gender')
                email = data.get('email')
                mobile = data.get('mobile')
                mobile_e164 = data.get('mobile_164')
                name = data.get('name')
                birthday = data.get('birthday')
                birthyear = data.get('birthyear')
                naver_manager = OAuthUserManager()
                refresh, user = naver_manager.create_naver_user(id=id, nickname=nickname, email=email)
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