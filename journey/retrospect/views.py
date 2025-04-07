from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import (Retrospect, Template, Challenge, Plan, ChallengeStatus, 
                 RetrospectWeeklyAnalysis, RetrospectVisibility, TemplateOwnerType, 
                 ChallengeOwnerType, RetrospectOwnerType, RetrospectWeeklyAnalysisOwnerType)
from .serializers import RetrospectSerializer, TemplateSerializer, ChallengeSerializer, PlanSerializer, RetrospectWeeklyAnalysisSerializer
from crew.models import Crew, CrewMembership, CrewMembershipStatus # Import CrewMembership models
from .permissions import (IsRetrospectOwnerOrCrewMemberOrReadOnly, # Use the new permission class
                          IsTemplateOwnerOrCrewMemberOrReadOnly, 
                          IsChallengeOwnerOrCrewMemberOrReadOnly, 
                          IsRetrospectWeeklyAnalysisOwnerOrCrewMemberOrReadOnly)
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
        """Set the user field automatically when creating a retrospect.
           The owner_type and crew (if applicable) should be validated by the serializer.
           The creator is always the request.user.
        """
        # Ensure the user is always set as the creator
        serializer.save(user=self.request.user)

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

        queryset = Challenge.objects.select_related('user', 'crew', 'plan').all()

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
        - Generate Plan via LLM if initial_plan_description is provided.
        - Generate KPI via LLM.
        - Assign Plan and KPI results to the challenge instance.
        """
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user
        crew = serializer.validated_data.get('crew')
        challenge_name = serializer.validated_data.get('challenge_name')
        initial_plan_description = serializer.validated_data.pop('initial_plan_description', None)
        plan_instance = serializer.validated_data.get('plan')

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

        if initial_plan_description:
            plan_data = generate_plan_from_description(initial_plan_description)
            plan_instance = Plan.objects.create(**plan_data)
            serializer.validated_data.pop('plan', None)

        kpi_description, kpi_metrics = generate_kpi_from_challenge(
            challenge_name, plan_instance.plan_list if plan_instance else [] # Handle case where plan might not exist yet
        )

        serializer.save(
            user=challenge_owner_user,
            crew=challenge_owner_crew,
            plan=plan_instance,
            kpi_description=kpi_description,
            kpi_metrics=kpi_metrics,
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

# --- Placeholder LLM functions --- #
def generate_plan_from_description(description: str) -> dict:
    print(f"[LLM Placeholder] Generating plan for: {description}")
    plan_steps = [f"Step 1 based on '{description}'", f"Step 2 based on '{description}'", "Step 3 generic"]
    return {"plan_list": plan_steps}

def generate_kpi_from_challenge(challenge_name: str, plan_list: list) -> tuple[str, dict]:
    print(f"[LLM Placeholder] Generating KPI for: {challenge_name} with plan: {plan_list}")
    kpi_desc = f"KPI description generated for {challenge_name}."
    kpi_metrics = {"completion_rate": 0, "step_1_focus": 0, "consistency": 0}
    return kpi_desc, kpi_metrics
# --- End Placeholder --- #


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

    # Add other necessary actions, e.g., for generating the analysis summary/KPI via LLM or calculation
    # @action(detail=False, methods=['post'], url_path='generate-weekly')
    # def generate_weekly_analysis(self, request):
    #     ...
        