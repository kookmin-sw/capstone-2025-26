from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from rest_framework import status, permissions
import jwt
from user_manager.utils import OAuthUserManager
from user_manager.serializer import UserSerializer
import uuid


class KakaoPayReadyView(APIView):
    #permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            #user = request.user
            #if not user.is_authenticated:
            #    return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

            # 차후에 쿼리 파람에 구매 아이템 정보 추가
            cid = settings.CID
            partner_order_id = uuid.uuid4().hex
            #partner_user_id = user.id
            item_name = "test_item"
            quantity = "1"
            total_amount = "2000"
            tax_free_amount = "0"
            approval_url = "http://13.125.14.13:8000/api/payment/kakao/approve"
            cancel_url = "http://13.125.14.13:8000/api/payment/kakao/cancel"
            fail_url = "http://13.125.14.13:8000/api/payment/kakao/fail"
            # 로컬 테스트
            approval_url = "http://localhost:8000/api/payment/kakao/approve"
            cancel_url = "http://localhost:8000/api/payment/kakao/cancel"
            fail_url = "http://localhost:8000/api/payment/kakao/fail"
            uri = "https://open-api.kakaopay.com/online/v1/payment/ready"
            
            headers = {
                "Authorization": f"SECRET_KEY {settings.KAKAO_PAY_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "cid": cid,
                "partner_order_id": "partner_order_id",
                "partner_user_id": "partner_user_id",
                "item_name": "item_name",
                "quantity": quantity,
                "total_amount": total_amount,
                "tax_free_amount": tax_free_amount,
                "approval_url": approval_url,
                "cancel_url": cancel_url,
                "fail_url": fail_url
            }
            print(data)
            print(headers)
            response = requests.post(uri, headers=headers, json=data)
            print(response.json())
            if response.status_code == 200:
                # pc or mobile
                return HttpResponseRedirect(response.json()['next_redirect_pc_url'])
            else:
                print(response.json())
                return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
