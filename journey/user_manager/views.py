from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from token_manager.serializer import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .serializer import UserSerializer, LoginSerializer
from django.contrib.auth.hashers import check_password
from .models import Notification
from .serializers import NotificationSerializer


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]


    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        return super().get_serializer_class()


    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True
            user.save()
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            return Response({
                'user': UserSerializer(user).data, 
                'refresh': str(refresh), 
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(email=request.data.get('email'))

            if not user.is_active:
                raise AuthenticationFailed("Account is inactive.")
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            if not check_password(request.data.get('password'), user.password):
                raise AuthenticationFailed('Invalid credentials')
            return Response({
                'user': UserSerializer(user).data, 
                'refresh': str(refresh), 
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            token = RefreshToken(request.data.get('refresh_token'))
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'detail': e}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_account(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_info(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class NotificationViewSet(viewsets.ModelViewSet):
    """
    사용자의 알림을 조회, 생성, 읽음 처리하는 API (관리자 권한 필요)
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 현재 로그인한 사용자의 알림만 반환 (GET 요청 시)
        # 생성(POST)은 permission_classes에서 제어
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['patch'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        """ 특정 알림을 읽음 상태로 변경합니다. """
        notification = self.get_object()
        if notification.user != request.user:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        """ 사용자의 모든 알림을 읽음 상태로 변경합니다. """
        notifications = self.get_queryset().filter(is_read=False)
        notifications.update(is_read=True)
        return Response({'status': 'all notifications marked as read'}, status=status.HTTP_200_OK)