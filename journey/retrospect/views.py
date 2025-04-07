from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Retrospect, Template, Challenge, Plan, ChallengeStatus, RetrospectWeeklyAnalysis
from .serializers import RetrospectSerializer, TemplateSerializer, ChallengeSerializer, PlanSerializer, RetrospectWeeklyAnalysisSerializer
from crew.models import Crew
from .permissions import IsOwnerOrReadOnly, IsTemplateOwnerOrCrewMemberOrReadOnly, IsChallengeOwnerOrCrewMemberOrReadOnly, IsRetrospectWeeklyAnalysisOwnerOrCrewMemberOrReadOnly
# Create your views here.


class RetrospectViewSet(viewsets.ModelViewSet):
    """ViewSet for the Retrospect model."""
    serializer_class = RetrospectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Returns a queryset containing only the retrospects created by the
        currently authenticated user.
        """
        user = self.request.user
        # Ensure the user is authenticated to view their retrospects
        if not user.is_authenticated:
            return Retrospect.objects.none() # Return empty queryset for anonymous users

        # Filter to only include retrospects where the user is the author
        return Retrospect.objects.select_related(
            'user', 'crew', 'challenge', 'template'
        ).filter(user=user)

    def perform_create(self, serializer):
        """Set the user field automatically when creating a retrospect."""
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
    # Use IsAuthenticatedOrReadOnly for create/list, custom perm for object-level R/U/D
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
            try:
                user_crews = user.crews.all()
            except AttributeError:
                user_crews = Crew.objects.none()

            return base_queryset.filter(
                Q(owner_type=Template.TemplateOwnerType.COMMON) |
                Q(owner_type=Template.TemplateOwnerType.USER, user=user) |
                Q(owner_type=Template.TemplateOwnerType.CREW, crew__in=user_crews)
            ).distinct()
        else:
            # Unauthenticated users only see common templates
            return base_queryset.filter(owner_type=Template.TemplateOwnerType.COMMON)

    def perform_create(self, serializer):
        """Set user or crew based on owner_type if not provided.
           Validate that the user can create the specified type.
        """
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user

        if owner_type == Template.TemplateOwnerType.USER:
            # Assign the current user if creating a USER template
            serializer.save(user=user, crew=None) # Explicitly set crew to None
        elif owner_type == Template.TemplateOwnerType.CREW:
            # Crew must be provided in the request data for CREW type
            # The serializer validates its presence.
            # We should also validate if the user is part of the specified crew.
            crew = serializer.validated_data.get('crew')
            if not user.crews.filter(pk=crew.pk).exists():
                 raise permissions.PermissionDenied("You do not have permission to create a template for this crew.")
            serializer.save(user=None) # Explicitly set user to None
        elif owner_type == Template.TemplateOwnerType.COMMON:
            # Optionally restrict who can create COMMON templates (e.g., admins)
            # For now, assume any authenticated user can, but without user/crew link
            # Add permission check here if needed: if not user.is_staff: raise ...
            serializer.save(user=None, crew=None)
        else:
            # Should be caught by serializer validation, but as a safeguard:
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

        # Filter by user/crew ownership
        try:
            user_crews = user.crews.all()
        except AttributeError:
            user_crews = Crew.objects.none()

        queryset = queryset.filter(
            Q(owner_type=Challenge.ChallengeOwnerType.USER, user=user) |
            Q(owner_type=Challenge.ChallengeOwnerType.CREW, crew__in=user_crews)
        ).distinct()

        # Filter by status query parameter (defaults to None -> show all)
        status_filter = self.request.query_params.get('status', None) 
        valid_statuses = [choice[0] for choice in ChallengeStatus.choices]

        if status_filter and status_filter in valid_statuses:
            queryset = queryset.filter(status=status_filter)
        # Add handling for invalid status if needed (currently ignored)
        elif status_filter: 
            pass # Ignore invalid status, show all

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
        plan_instance = serializer.validated_data.get('plan') # Plan might be provided directly

        # 1. Determine Ownership and Validate Permissions
        challenge_owner_user = None
        challenge_owner_crew = None
        if owner_type == Challenge.ChallengeOwnerType.USER:
            challenge_owner_user = user
            if crew:
                # This should be caught by serializer, but double-check
                raise permissions.PermissionDenied("Cannot assign crew to a USER challenge.")
        elif owner_type == Challenge.ChallengeOwnerType.CREW:
            challenge_owner_crew = crew
            if not crew:
                 # This should be caught by serializer
                 raise permissions.PermissionDenied("Crew is required for CREW challenge.")
            if not user.crews.filter(pk=crew.pk).exists():
                 raise permissions.PermissionDenied("You are not a member of this crew.")

        # 2. Handle Plan Creation/Association
        if initial_plan_description:
            # Generate plan using LLM
            plan_data = generate_plan_from_description(initial_plan_description)
            # Create Plan object
            plan_instance = Plan.objects.create(**plan_data)
            # Remove 'plan' from validated_data if it was initially None due to description input
            serializer.validated_data.pop('plan', None)

        # 3. Generate KPI using LLM
        kpi_description, kpi_metrics = generate_kpi_from_challenge(
            challenge_name, plan_instance.plan_list
        )

        # 4. Save the Challenge instance with all data
        serializer.save(
            user=challenge_owner_user,
            crew=challenge_owner_crew,
            plan=plan_instance,
            kpi_description=kpi_description,
            kpi_metrics=kpi_metrics,
            status=Challenge.ChallengeStatus.LIVE # Default status on creation
        )

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Allows updating the status of a specific challenge.
        Expects {"status": "NEW_STATUS"} in the request body.
        NEW_STATUS must be one of 'LIVE', 'SUCCESS', 'FAIL'.
        Permissions are checked by IsChallengeOwnerOrCrewMemberOrReadOnly.
        """
        challenge = self.get_object() # Retrieves the challenge instance
        # get_object() already handles 404 Not Found

        new_status = request.data.get('status')

        # Validate the new status
        valid_statuses = [choice[0] for choice in ChallengeStatus.choices]
        if not new_status:
            return Response({'detail': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if new_status not in valid_statuses:
            return Response({'detail': f'Invalid status. Must be one of {valid_statuses}.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Update the status
        challenge.status = new_status
        challenge.save(update_fields=['status'])

        # Serialize and return the updated challenge
        serializer = self.get_serializer(challenge)
        return Response(serializer.data)

# --- Placeholder for LLM functions ---
# These would likely live in a separate service/module
def generate_plan_from_description(description: str) -> dict:
    # Placeholder: Replace with actual LLM call
    # Simulates generating a plan list based on the description
    print(f"[LLM Placeholder] Generating plan for: {description}")
    # Example structure for plan_list
    plan_steps = [f"Step 1 based on '{description}'", f"Step 2 based on '{description}'", "Step 3 generic"]
    return {"plan_list": plan_steps}

def generate_kpi_from_challenge(challenge_name: str, plan_list: list) -> tuple[str, dict]:
    # Placeholder: Replace with actual LLM call
    print(f"[LLM Placeholder] Generating KPI for: {challenge_name} with plan: {plan_list}")
    kpi_desc = f"KPI description generated for {challenge_name}."
    # Example structure for kpi_metrics
    kpi_metrics = {"completion_rate": 0, "step_1_focus": 0, "consistency": 0}
    return kpi_desc, kpi_metrics
# --- End Placeholder ---


class RetrospectWeeklyAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for the RetrospectWeeklyAnalysis model."""
    serializer_class = RetrospectWeeklyAnalysisSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRetrospectWeeklyAnalysisOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """Filter RetrospectWeeklyAnalysis:
        - By default, show LIVE challenges (for user or their crews).
        - Add query params to filter by status (e.g., ?status=SUCCESS, ?status=FAIL)
        - Unauthenticated users likely see nothing or public crew challenges?
          (Policy TBD, currently only authenticated users see relevant challenges)
        """
        user = self.request.user
        if not user.is_authenticated:
            return RetrospectWeeklyAnalysis.objects.none() # No challenges for anonymous users for now

        queryset = RetrospectWeeklyAnalysis.objects.select_related('user', 'crew').all()

        # Filter by user/crew ownership
        try:
            user_crews = user.crews.all()
        except AttributeError:
            user_crews = Crew.objects.none()

        queryset = queryset.filter(
            Q(owner_type=RetrospectWeeklyAnalysis.RetrospectWeeklyAnalysisOwnerType.USER, user=user) |
            Q(owner_type=RetrospectWeeklyAnalysis.RetrospectWeeklyAnalysisOwnerType.CREW, crew__in=user_crews)
        ).distinct()

        return queryset
        