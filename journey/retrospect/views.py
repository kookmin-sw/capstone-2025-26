from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import (Retrospect, Template, Challenge, Plan, ChallengeStatus, 
                 RetrospectWeeklyAnalysis, RetrospectVisibility, TemplateOwnerType, 
                 ChallengeOwnerType, RetrospectOwnerType, RetrospectWeeklyAnalysisOwnerType, Kpi, KpiResult)
from .serializers import (RetrospectSerializer, TemplateSerializer, ChallengeSerializer, 
                      PlanSerializer, PlanResponseSerializer, RetrospectWeeklyAnalysisSerializer, KpiSerializer, KpiResultSerializer)
from crew.models import Crew, CrewMembership, CrewMembershipStatus  # CrewMembership 관련 모델을 임포트합니다.
from .permissions import (IsRetrospectOwnerOrCrewMemberOrReadOnly,  # 인증 읽기 허용, 소유자·크루 멤버만 수정 가능
                          IsTemplateOwnerOrCrewMemberOrReadOnly, 
                          IsChallengeOwnerOrCrewMemberOrReadOnly, 
                          IsRetrospectWeeklyAnalysisOwnerOrCrewMemberOrReadOnly)
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from ai_manager.services.kpi_score_generator import score_kpis_from_retrospect

import os
import logging

# from django_filters.rest_framework import DjangoFilterBackend # If you want filtering

# Create your views here.

from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

logger = logging.getLogger(__name__)

# LangChain LLM 설정
llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    model_name="gemini-2.0-flash-lite-001",
    max_output_tokens=1024,
    temperature=0.7,
)

# Langfuse 핸들러 초기화
langfuse_handler = None
try:
    langfuse_handler = CallbackHandler(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
except Exception as e:
    logger.warning(f"Langfuse 핸들러 초기화 오류: {str(e)}. 토큰 사용량 추적이 비활성화됩니다.")


class RetrospectViewSet(viewsets.ModelViewSet):
    """Retrospect 모델을 처리하는 ViewSet"""
    serializer_class = RetrospectSerializer
    # 비인증 사용자는 읽기만, 소유자·크루 멤버만 수정 가능
    permission_classes = [IsAuthenticatedOrReadOnly, IsRetrospectOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """비인증 사용자는 공개 회고만, 인증된 사용자는 본인이 작성한 회고만 조회합니다."""
        user = self.request.user
        base_queryset = Retrospect.objects.select_related(
            'user', 'crew', 'challenge', 'template'
        ).all()

        if not user.is_authenticated:
            # 비인증 사용자는 공개 회고만 조회합니다.
            return base_queryset.filter(visibility=RetrospectVisibility.PUBLIC)
        
        # 인증된 사용자는 본인이 작성한 회고만 조회합니다.
        return base_queryset.filter(user=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        challenge = serializer.validated_data.get('challenge')
        template = serializer.validated_data.get('template')

        # Only allow retrospects for challenges the user owns or for crews they belong to
        if challenge.owner_type == ChallengeOwnerType.USER:
            if challenge.user != user:
                raise PermissionDenied("You can only create retrospects for challenges you created.")
            crew_to_save = None
        elif challenge.owner_type == ChallengeOwnerType.CREW:
            if not CrewMembership.objects.filter(
                crew=challenge.crew,
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                raise PermissionDenied("You can only create retrospects for challenges of crews you belong to.")
            crew_to_save = challenge.crew
        else:
            raise PermissionDenied("Invalid challenge owner type.")

        # 트랜잭션 내에서 회고 생성 및 KPI 점수 생성 처리
        with transaction.atomic():
            instance = serializer.save(user=user, challenge=challenge, template=template, crew=crew_to_save)

            # KPI 점수 생성
            score_kpis_from_retrospect(instance, llm)
            print(f"KPI 점수 생성 완료 (회고 ID: {instance.id})")

        # 회고 저장 결과 및 생성된 KPI 결과를 리턴
        return instance

    
class TemplateViewSet(viewsets.ModelViewSet):
    """Template 모델을 처리하는 ViewSet"""
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsTemplateOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """
        템플릿을 필터링합니다.
        - 인증된 사용자는 COMMON, 본인 USER, 소속 CREW 템플릿을 조회합니다.
        - 비인증 사용자는 COMMON 템플릿만 조회합니다.
        """
        user = self.request.user
        base_queryset = Template.objects.select_related('user', 'crew').all()

        if user.is_authenticated:
            # 사용자가 속한 크루 ID 목록을 조회합니다.
            user_crew_ids = CrewMembership.objects.filter(
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).values_list('crew_id', flat=True)

            return base_queryset.filter(
                Q(owner_type=TemplateOwnerType.COMMON) |
                Q(owner_type=TemplateOwnerType.USER, user=user) |
                Q(owner_type=TemplateOwnerType.CREW, crew_id__in=user_crew_ids)
            ).distinct()
        else:
            # 비인증 사용자는 COMMON 템플릿만 조회합니다.
            return base_queryset.filter(owner_type=TemplateOwnerType.COMMON)

    def perform_create(self, serializer):
        """owner_type에 따라 user 또는 crew를 설정하고, 생성 권한을 검증합니다."""
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user

        if owner_type == TemplateOwnerType.USER:
            serializer.save(user=user, crew=None)
        elif owner_type == TemplateOwnerType.CREW:
            crew = serializer.validated_data.get('crew')
            # CrewMembership을 사용해 멤버십 여부를 확인합니다.
            if not CrewMembership.objects.filter(
                crew=crew, 
                user=user, 
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                 raise permissions.PermissionDenied("You do not have permission to create a template for this crew.")
            serializer.save(user=None, crew=crew)
        elif owner_type == TemplateOwnerType.COMMON:
            # COMMON 템플릿 생성 시 추가 권한 검증이 필요할 수 있습니다.
            serializer.save(user=None, crew=None)
        else:
            super().perform_create(serializer)

class ChallengeViewSet(viewsets.ModelViewSet):
    """Challenge 모델을 처리하는 ViewSet"""
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsChallengeOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """
        챌린지를 필터링합니다.
        - 기본: 사용자 또는 소속 크루의 모든 상태 챌린지를 조회합니다.
        - ?status=SUCCESS/FAIL/LIVE로 상태 필터링을 지원합니다.
        - 비인증 사용자는 결과가 없습니다.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Challenge.objects.none()

        queryset = Challenge.objects.select_related('user', 'crew').all()

        # 사용자가 속한 크루 ID 목록을 조회합니다.
        user_crew_ids = CrewMembership.objects.filter(
            user=user,
            status=CrewMembershipStatus.ACCEPTED
        ).values_list('crew_id', flat=True)

        queryset = queryset.filter(
            Q(owner_type=ChallengeOwnerType.USER, user=user) |
            Q(owner_type=ChallengeOwnerType.CREW, crew_id__in=user_crew_ids)
        ).distinct()

        # 상태(status) 쿼리 파라미터로 필터링합니다.
        status_filter = self.request.query_params.get('status', None)
        valid_statuses = [choice[0] for choice in ChallengeStatus.choices]

        if status_filter and status_filter in valid_statuses:
            queryset = queryset.filter(status=status_filter)
        elif status_filter:
            pass  # 유효하지 않은 상태는 무시합니다.

        return queryset

    def perform_create(self, serializer):
        """Challenge 생성 시 owner_type에 따라 user 또는 crew를 설정하고, KPI 및 Plan/KPI 결과를 할당합니다."""
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user
        crew = serializer.validated_data.get('crew')
        challenge_name = serializer.validated_data.get('challenge_name')
        

        challenge_owner_user = None
        challenge_owner_crew = None
        if owner_type == ChallengeOwnerType.USER:
            challenge_owner_user = user
            if crew:
                raise permissions.PermissionDenied("USER 챌린지에 crew를 지정할 수 없습니다.")
        elif owner_type == ChallengeOwnerType.CREW:
            challenge_owner_crew = crew
            if not crew:
                raise permissions.PermissionDenied("CREW 챌린지에는 crew가 필요합니다.")
            # CrewMembership을 사용해 멤버십 여부를 확인합니다.
            if not CrewMembership.objects.filter(
                crew=crew,
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                raise permissions.PermissionDenied("크루 멤버만 생성할 수 있습니다.")

        serializer.save(
            user=challenge_owner_user,
            crew=challenge_owner_crew,
            status=ChallengeStatus.LIVE
        )

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """챌린지 상태를 업데이트합니다."""
        challenge = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in ChallengeStatus.choices]
        if not new_status:
            return Response({'detail': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if new_status not in valid_statuses:
            return Response({'detail': f'Invalid status. Must be one of {valid_statuses}.'}, status=status.HTTP_400_BAD_REQUEST)

        challenge.status = new_status
        challenge.save(update_fields=['status'])

        serializer = self.get_serializer(challenge)
        return Response(serializer.data)


class RetrospectWeeklyAnalysisViewSet(viewsets.ModelViewSet):
    """주간 회고 분석 모델(RetrospectWeeklyAnalysis)을 처리하는 ViewSet"""
    serializer_class = RetrospectWeeklyAnalysisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRetrospectWeeklyAnalysisOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """
        주간 분석을 필터링합니다.
        - 인증된 사용자는 본인 USER 분석 및 소속 CREW 분석을 조회합니다.
        - 비인증 사용자는 결과가 없습니다.
        """
        user = self.request.user
        if not user.is_authenticated:
            return RetrospectWeeklyAnalysis.objects.none()

        base_queryset = RetrospectWeeklyAnalysis.objects.select_related('user', 'crew').all()

        # 사용자가 속한 크루 ID 목록을 조회합니다.
        user_crew_ids = CrewMembership.objects.filter(
            user=user,
            status=CrewMembershipStatus.ACCEPTED
        ).values_list('crew_id', flat=True)

        queryset = base_queryset.filter(
            Q(owner_type=RetrospectWeeklyAnalysisOwnerType.USER, user=user) |
            Q(owner_type=RetrospectWeeklyAnalysisOwnerType.CREW, crew_id__in=user_crew_ids)
        ).distinct()

        # 필요 시 query params로 날짜 범위 필터링을 추가합니다.
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        """
        owner_type에 따라 user 또는 crew를 설정하고, 생성 권한을 검증합니다.
        """
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user

        if owner_type == RetrospectWeeklyAnalysisOwnerType.USER:
            # USER 분석인 경우 현재 사용자를 할당합니다.
            serializer.save(user=user, crew=None)
        elif owner_type == RetrospectWeeklyAnalysisOwnerType.CREW:
            # CREW 분석인 경우 request에 전달된 crew를 사용하고, 멤버십을 확인합니다.
            crew = serializer.validated_data.get('crew')
            if not CrewMembership.objects.filter(
                crew=crew,
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                 raise permissions.PermissionDenied("You do not have permission to create an analysis for this crew.")
            serializer.save(user=None, crew=crew)
        else:
            # (안전장치) serializer 검증 후 호출됩니다.
            super().perform_create(serializer)
        
        
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        요청된 액션에 따라 시리얼라이저를 반환합니다:
        - list, retrieve: PlanResponseSerializer
        - 그 외: PlanSerializer
        """
        if self.action in ['list', 'retrieve']:
            return PlanResponseSerializer
        return PlanSerializer

    def perform_create(self, serializer):
        user = self.request.user
        challenge = serializer.validated_data.get('challenge')
        if challenge.owner_type == ChallengeOwnerType.USER:
            if challenge.user != user:
                raise PermissionDenied("You can only create KPI for challenges you created.")
        # CREW 소유 챌린지의 크루 멤버 여부를 확인합니다
        elif challenge.owner_type == ChallengeOwnerType.CREW:
            if not CrewMembership.objects.filter(
                crew=challenge.crew,
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                raise PermissionDenied("You can only create KPI for challenges of crews you belong to.")
        else:
            raise PermissionDenied("Invalid challenge owner type.")

        # Save with the requesting user as the KPI owner
        serializer.save(user=user, challenge=challenge)
    
    def list(self, request, *args, **kwargs):
        """list 메서드를 재정의하여 요청 형식에 맞게 Plan 목록을 반환합니다."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 챌린지로 필터링 (선택적)
        challenge_id = request.query_params.get('challenge_id')
        if challenge_id:
            queryset = queryset.filter(challenge_id=challenge_id)
            
        # 사용자로 필터링 (기본적으로 자신의 계획만 볼 수 있음)
        queryset = queryset.filter(user=request.user)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """retrieve 메서드를 재정의하여 요청 형식에 맞게 단일 Plan을 반환합니다."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-challenge/(?P<challenge_id>[^/.]+)')
    def by_challenge(self, request, challenge_id=None):
        """
        특정 챌린지의 Plan 목록을 조회합니다.
        """
        if not challenge_id:
            return Response({"error": "challenge_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            challenge = Challenge.objects.get(pk=challenge_id)
        except Challenge.DoesNotExist:
            return Response({"error": f"Challenge with id {challenge_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        # 챌린지 소유자 또는 크루 멤버인지 확인
        if challenge.owner_type == ChallengeOwnerType.USER:
            if challenge.user != request.user:
                raise PermissionDenied("오직 챌린지 소유자만 계획을 조회할 수 있습니다.")
        elif challenge.owner_type == ChallengeOwnerType.CREW:
            if not CrewMembership.objects.filter(
                crew=challenge.crew,
                user=request.user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                raise PermissionDenied("오직 크루 멤버만 계획을 조회할 수 있습니다.")
        
        queryset = Plan.objects.filter(challenge=challenge, user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
class KpiViewSet(viewsets.ModelViewSet):
    """
    KPI를 관리하는 ViewSet
    """
    serializer_class = KpiSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Kpi.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        사용자가 소유하거나 속한 크루의 챌린지에 대해서만 KPI를 생성할 수 있습니다.
        """
        challenge = serializer.validated_data.get('challenge')
        user = self.request.user

        # 챌린지 소유자인 경우만 KPI 생성이 가능합니다.
        if challenge.owner_type == ChallengeOwnerType.USER:
            if challenge.user != user:
                raise PermissionDenied("You can only create KPI for challenges you created.")
        # CREW 소유 챌린지의 경우 소속 크루 멤버만 생성할 수 있습니다.
        elif challenge.owner_type == ChallengeOwnerType.CREW:
            if not CrewMembership.objects.filter(
                crew=challenge.crew,
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                raise PermissionDenied("You can only create KPI for challenges of crews you belong to.")
        else:
            raise PermissionDenied("Invalid challenge owner type.")

        # Save with the requesting user as the KPI owner
        serializer.save(user=user, challenge=challenge)

    @action(detail=False, methods=['get'], url_path='by-challenge/(?P<challenge_id>[^/.]+)')
    def by_challenge(self, request, challenge_id=None, pk=None):
        """
        특정 챌린지의 KPI를 조회
        """
        kpis = Kpi.objects.filter(
            user=request.user,
            challenge_id=challenge_id
        ).order_by('-created_at')
        
        serializer = self.get_serializer(kpis, many=True)
        return Response(serializer.data)


class KpiResultViewSet(viewsets.ModelViewSet):
    """
    KPI 결과를 관리하는 ViewSet
    """
    serializer_class = KpiResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KpiResult.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        challenge = serializer.validated_data.get('challenge')
        kpi = serializer.validated_data.get('kpi')
        retrospect = serializer.validated_data.get('retrospect')
        serializer.save(user=user, challenge=challenge, kpi=kpi, retrospect=retrospect)

    @action(detail=False, methods=['get'], url_path='by-challenge/(?P<challenge_id>[^/.]+)')
    def by_challenge(self, request, challenge_id=None):
        """
        특정 챌린지의 KPI 결과를 조회
        """
        results = KpiResult.objects.filter(
            user=request.user,
            challenge_id=challenge_id
        ).order_by('-created_at')
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
