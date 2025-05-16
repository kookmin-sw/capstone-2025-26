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
from crew.models import Crew, CrewMembership, CrewMembershipStatus # Import CrewMembership models
from .permissions import (IsRetrospectOwnerOrCrewMemberOrReadOnly, # Use the new permission class
                          IsTemplateOwnerOrCrewMemberOrReadOnly, 
                          IsChallengeOwnerOrCrewMemberOrReadOnly, 
                          IsRetrospectWeeklyAnalysisOwnerOrCrewMemberOrReadOnly)
from django.utils import timezone
from datetime import timedelta

# Create your views here.


class RetrospectViewSet(viewsets.ModelViewSet):
    """ViewSet for the Retrospect model."""
    serializer_class = RetrospectSerializer
    # Updated permission class
    permission_classes = [IsAuthenticatedOrReadOnly, IsRetrospectOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """
        Filter retrospects based on user authentication, ownership, crew membership,
        and visibility settings.
        """
        user = self.request.user
        base_queryset = Retrospect.objects.select_related(
            'user', 'crew', 'challenge', 'template'
        ).all()

        if not user.is_authenticated:
            # Unauthenticated users only see PUBLIC retrospects
            return base_queryset.filter(visibility=RetrospectVisibility.PUBLIC)
        
        # Authenticated users see:
        # 1. Their own USER retrospects (regardless of visibility)
        # 2. CREW retrospects of crews they are members of (if visibility is CREW or PUBLIC)
        # 3. All PUBLIC retrospects (covered by the first filter if owner or the second if member, or separate Q)

        # Get IDs of crews the user is an accepted member of
        user_crew_ids = CrewMembership.objects.filter(
            user=user, 
            status=CrewMembershipStatus.ACCEPTED
        ).values_list('crew_id', flat=True)

        queryset = base_queryset.filter(
            # Own USER retrospects (any visibility)
            Q(owner_type=RetrospectOwnerType.USER, user=user) |
            # CREW retrospects for their crews (CREW or PUBLIC visibility)
            (Q(owner_type=RetrospectOwnerType.CREW, crew_id__in=user_crew_ids) & 
             Q(visibility__in=[RetrospectVisibility.CREW, RetrospectVisibility.PUBLIC])) |
            # Other PUBLIC retrospects (might overlap, but ensures all public are included)
            Q(visibility=RetrospectVisibility.PUBLIC)
        ).distinct() # Use distinct to avoid duplicates if a user owns a public retrospect
        
        return queryset
    
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

        serializer.save(user=user, challenge=challenge, template=template, crew=crew_to_save)

    # 분리하는게 좋을 것 같아서 일단 주석처리
    # def perform_create(self, serializer):
    #     """회고 생성 시 Plan을 자동 생성하고 연결"""

    #     user = self.request.user
    #     retrospect = serializer.save(user=user)

    #     try:
    #         #회고 기반 Plan 생성
    #         plan = generate_plan_from_retrospect(retrospect.challenge, retrospect)

    #         #회고에 Plan 연결 후 저장
    #         retrospect.plan = plan
    #         retrospect.save(update_fields=['plan'])
        
    #     except Exception as e:
    #         # 회고는 저장됐지만 Plan 생성 실패
    #         print(f"[ERROR] 회고 기반 Plan 생성 실패: {e}")


    # Add specific actions if needed, e.g., linking to crew, etc.
    # Example: List retrospects for a specific challenge or user might be useful
    # @action(detail=False, methods=['get'], url_path='by-challenge/(?P<challenge_id>\\d+)')
    # def by_challenge(self, request, challenge_id=None):
    #     ...

    # @action(detail=False, methods=['get'], url_path='my-retrospects')
    # def my_retrospects(self, request):
    #    ...

class TemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for the Template model."""
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsTemplateOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """Filter templates:
        - Authenticated users see COMMON templates, their own USER templates,
          and templates belonging to Crews they are members of.
        - Unauthenticated users see only COMMON templates.
        """
        user = self.request.user
        base_queryset = Template.objects.select_related('user', 'crew').all()

        if user.is_authenticated:
            # Corrected: Get crew IDs via CrewMembership
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
            # Unauthenticated users only see common templates
            return base_queryset.filter(owner_type=TemplateOwnerType.COMMON)

    def perform_create(self, serializer):
        """Set user or crew based on owner_type if not provided.
           Validate that the user can create the specified type.
        """
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user

        if owner_type == TemplateOwnerType.USER:
            serializer.save(user=user, crew=None)
        elif owner_type == TemplateOwnerType.CREW:
            crew = serializer.validated_data.get('crew')
            # Corrected: Check membership using CrewMembership
            if not CrewMembership.objects.filter(
                crew=crew, 
                user=user, 
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                 raise permissions.PermissionDenied("You do not have permission to create a template for this crew.")
            serializer.save(user=None, crew=crew)
        elif owner_type == TemplateOwnerType.COMMON:
            # Add permission check here if needed: if not user.is_staff: raise ...
            serializer.save(user=None, crew=None)
        else:
            super().perform_create(serializer)

class ChallengeViewSet(viewsets.ModelViewSet):
    """ViewSet for the Challenge model."""
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsChallengeOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """Filter Challenges:
        - By default, show challenges of all statuses (for user or their crews).
        - Add query params to filter by status (e.g., ?status=SUCCESS, ?status=FAIL, ?status=LIVE)
        - Unauthenticated users see nothing.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Challenge.objects.none()

        queryset = Challenge.objects.select_related('user', 'crew').all()

        # Corrected: Get crew IDs via CrewMembership
        user_crew_ids = CrewMembership.objects.filter(
            user=user,
            status=CrewMembershipStatus.ACCEPTED
        ).values_list('crew_id', flat=True)

        queryset = queryset.filter(
            Q(owner_type=ChallengeOwnerType.USER, user=user) |
            Q(owner_type=ChallengeOwnerType.CREW, crew_id__in=user_crew_ids)
        ).distinct()

        # Filter by status query parameter
        status_filter = self.request.query_params.get('status', None)
        valid_statuses = [choice[0] for choice in ChallengeStatus.choices]

        if status_filter and status_filter in valid_statuses:
            queryset = queryset.filter(status=status_filter)
        elif status_filter:
            pass # Ignore invalid status

        return queryset

    def perform_create(self, serializer):
        """Handle Challenge creation:
        - Set user or crew based on owner_type.
        - Generate KPI via LLM.
        - Assign Plan and KPI results to the challenge instance.
        """
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user
        crew = serializer.validated_data.get('crew')
        challenge_name = serializer.validated_data.get('challenge_name')
        

        challenge_owner_user = None
        challenge_owner_crew = None
        if owner_type == ChallengeOwnerType.USER:
            challenge_owner_user = user
            if crew:
                raise permissions.PermissionDenied("Cannot assign crew to a USER challenge.")
        elif owner_type == ChallengeOwnerType.CREW:
            challenge_owner_crew = crew
            if not crew:
                 raise permissions.PermissionDenied("Crew is required for CREW challenge.")
            # Corrected: Check membership using CrewMembership
            if not CrewMembership.objects.filter(
                crew=crew,
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                 raise permissions.PermissionDenied("You are not a member of this crew.")

        serializer.save(
            user=challenge_owner_user,
            crew=challenge_owner_crew,
            status=ChallengeStatus.LIVE
        )

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Allows updating the status of a challenge."""
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
    """ViewSet for the RetrospectWeeklyAnalysis model."""
    serializer_class = RetrospectWeeklyAnalysisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRetrospectWeeklyAnalysisOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """Filter weekly analyses:
        - Authenticated users see their own USER analyses and analyses
          belonging to Crews they are members of.
        - Unauthenticated users see nothing (or maybe public ones if that becomes a feature).
        """
        user = self.request.user
        if not user.is_authenticated:
            return RetrospectWeeklyAnalysis.objects.none()

        base_queryset = RetrospectWeeklyAnalysis.objects.select_related('user', 'crew').all()

        # Get IDs of crews the user is an accepted member of
        user_crew_ids = CrewMembership.objects.filter(
            user=user,
            status=CrewMembershipStatus.ACCEPTED
        ).values_list('crew_id', flat=True)

        queryset = base_queryset.filter(
            Q(owner_type=RetrospectWeeklyAnalysisOwnerType.USER, user=user) |
            Q(owner_type=RetrospectWeeklyAnalysisOwnerType.CREW, crew_id__in=user_crew_ids)
        ).distinct()

        # Add filtering by date range, etc., if needed via query params
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        """Set user or crew based on owner_type.
           Validate that the user can create the specified type.
        """
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user

        if owner_type == RetrospectWeeklyAnalysisOwnerType.USER:
            # Assign the current user if creating a USER analysis
            serializer.save(user=user, crew=None)
        elif owner_type == RetrospectWeeklyAnalysisOwnerType.CREW:
            # Crew must be provided in the request data for CREW type
            # The serializer validates its presence.
            # Validate if the user is part of the specified crew.
            crew = serializer.validated_data.get('crew')
            if not CrewMembership.objects.filter(
                crew=crew,
                user=user,
                status=CrewMembershipStatus.ACCEPTED
            ).exists():
                 raise permissions.PermissionDenied("You do not have permission to create an analysis for this crew.")
            serializer.save(user=None, crew=crew)
        else:
            # Should be caught by serializer validation, but as a safeguard:
            super().perform_create(serializer)
        
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Return different serializers for different actions:
        - Use PlanResponseSerializer for list and retrieve actions
        - Use PlanSerializer for all other actions
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
        # Or for crew members of a crew-owned challenge
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
        """
        Override list method to return plans in the requested format
        """
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
        """
        Override retrieve method to return a single plan in the requested format
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
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
        Allow KPI creation only for challenges the user owns or for crews they belong to.
        """
        challenge = serializer.validated_data.get('challenge')
        user = self.request.user

        # Only allow KPI creation for the challenge owner
        if challenge.owner_type == ChallengeOwnerType.USER:
            if challenge.user != user:
                raise PermissionDenied("You can only create KPI for challenges you created.")
        # Or for crew members of a crew-owned challenge
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
