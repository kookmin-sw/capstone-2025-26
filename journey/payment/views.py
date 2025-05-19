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
from .serializers import PaymentSerializer
from .models import Payment


class KakaoPayReadyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

            # 차후에 쿼리 파람에 구매 아이템 정보 추가
            cid = settings.CID
            partner_order_id = uuid.uuid4().hex
            partner_user_id = str(user.id)
            item_name = "회고 AI 프리미엄 버전"
            quantity = 1
            total_amount = 2000
            tax_free_amount = 0
            vat_amount = 0
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
                "partner_order_id": partner_order_id,
                "partner_user_id": partner_user_id,
                "item_name": item_name,
                "quantity": str(quantity),
                "total_amount": str(total_amount),
                "tax_free_amount": str(tax_free_amount),
                "approval_url": approval_url,
                "cancel_url": cancel_url,
                "fail_url": fail_url
            }

            response = requests.post(uri, headers=headers, json=data)

            if response.status_code == 200:
                # pc or mobile
                tid = response.json()['tid']
                created_at = response.json()['created_at']
                # Save payment information
                payment_data = {
                    'user': user.id,
                    'cid': cid,
                    'tid': tid,
                    'partner_order_id': partner_order_id,
                    'partner_user_id': partner_user_id,
                    'total': total_amount,
                    'tax_free': tax_free_amount,
                    'vat': vat_amount,
                    'item_name': item_name,
                    'quantity': quantity,
                    'created_at': created_at,
                    'status': 'ready'
                }
                # 이미 결제 중인 결제 취소
                payment = Payment.objects.filter(user=user, status='ready')
                if payment.exists():
                    for p in payment:
                        p.status = 'canceled'
                        p.save()

                # 결제 정보 저장
                serializer = PaymentSerializer(data=payment_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                return HttpResponseRedirect(response.json()['next_redirect_pc_url'])
            else:
                return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class KakaoPayApproveView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        payment = None
        try:
            user = request.user
            pg_token = request.query_params.get('pg_token')

            try:
                payment = Payment.objects.get(
                    user=user,
                    status='ready'
                )
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

            uri = "https://open-api.kakaopay.com/online/v1/payment/approve"
            headers = {
                "Authorization": f"SECRET_KEY {settings.KAKAO_PAY_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "cid": settings.CID,
                "tid": payment.tid,
                "partner_order_id": payment.partner_order_id,
                "partner_user_id": payment.partner_user_id,
                "pg_token": pg_token,
            }
            response = requests.post(uri, headers=headers, json=data)
            if response.status_code == 200:
                # Update payment status to approved
                payment.status = 'approved'
                payment.aid = response.json()['aid']
                payment.cid = response.json()['cid']
                payment.sid = response.json()['sid']
                payment.partner_order_id = response.json()['partner_order_id']  
                payment.partner_user_id = response.json()['partner_user_id']
                payment.payment_method_type = response.json()['payment_method_type']
                payment.item_name = response.json()['item_name']
                payment.quantity = response.json()['quantity']
                payment.total = int(response.json()['amount']['total'])
                payment.tax_free = int(response.json()['amount']['tax_free'])
                payment.vat = int(response.json()['amount']['vat'])
                payment.point = int(response.json()['amount']['point'])
                payment.discount = int(response.json()['amount']['discount'])
                payment.green_deposit = int(response.json()['amount']['green_deposit'])
                payment.created_at = response.json()['created_at']
                payment.approved_at = response.json()['approved_at']
                payment.save()
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                # Update payment status to failed
                if payment:
                    payment.status = 'failed'
                    payment.save()
                return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if payment:
                payment.status = 'failed'
                payment.save()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class KakaoPayFailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            partner_order_id = request.query_params.get('partner_order_id')
            partner_user_id = request.query_params.get('partner_user_id')

            # Get the payment record
            try:
                payment = Payment.objects.get(
                    partner_order_id=partner_order_id,
                    partner_user_id=partner_user_id,
                    status='ready'
                )
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

            # Update payment status to failed
            payment.status = 'failed'
            payment.save()

            return Response({'message': 'Payment failed'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class KakaoPayCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            partner_order_id = request.query_params.get('partner_order_id')
            partner_user_id = request.query_params.get('partner_user_id')

            # Get the payment record
            try:
                payment = Payment.objects.get(
                    partner_order_id=partner_order_id,
                    partner_user_id=partner_user_id,
                    status='ready'
                )
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

            # Update payment status to canceled
            payment.status = 'canceled'
            payment.save()

            return Response({'message': 'Payment canceled'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)