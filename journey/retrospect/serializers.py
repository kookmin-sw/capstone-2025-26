from rest_framework import serializers
from .models import Retrospect, Challenge, Template, Plan, RetrospectWeeklyAnalysis
from user_manager.models import User
from crew.models import Crew

class RetrospectSerializer(serializers.ModelSerializer):
    """Serializer for the Retrospect model."""
    # Use PrimaryKeyRelatedField for related objects initially for simplicity
    # Consider using nested serializers or StringRelatedField later if needed
    user = serializers.PrimaryKeyRelatedField(read_only=True) # Set automatically based on request user
    challenge = serializers.PrimaryKeyRelatedField(queryset=Challenge.objects.all())
    template = serializers.PrimaryKeyRelatedField(queryset=Template.objects.all(), allow_null=True, required=False)
    crew = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Retrospect
        fields = [
            'id',
            'challenge',
            'template',
            'user',
            'crew',
            'content',
            'kpi_result',
            'visibility',
            'owner_type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user'] # user is set in the view

    def validate(self, data):
        """
        Validate owner_type based on whether crew is provided.
        Validate visibility based on owner_type.
        """
        is_crew_retrospect = data.get('crew') is not None
        owner_type = data.get('owner_type')

        # Validate owner_type consistency
        if is_crew_retrospect and owner_type != Retrospect.RetrospectOwnerType.CREW:
            raise serializers.ValidationError("If 'crew' is provided, 'owner_type' must be 'CREW'.")
        if not is_crew_retrospect and owner_type != Retrospect.RetrospectOwnerType.USER:
            raise serializers.ValidationError("If 'crew' is not provided, 'owner_type' must be 'USER'.")

        # Validate visibility
        visibility = data.get('visibility')
        if owner_type == Retrospect.RetrospectOwnerType.CREW and visibility == Retrospect.RetrospectVisibility.PRIVATE:
             raise serializers.ValidationError("Crew retrospects cannot have 'PRIVATE' visibility.")

        # Add more validation if needed, e.g., user belongs to the crew if crew is specified

        return data 

class TemplateSerializer(serializers.ModelSerializer):
    """Serializer for the Template model."""
    # Decide if user/crew should be read_only or set based on context
    # If a template is created in a user context, user is set.
    # If created in a crew context, crew is set.
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    crew = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Template
        fields = [
            'id',
            'user',
            'crew',
            'owner_type',
            'name',
            'steps',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """
        Ensure either user or crew is set based on owner_type,
        but not both (unless owner_type is COMMON, adjust if needed).
        """
        owner_type = data.get('owner_type')
        user = data.get('user')
        crew = data.get('crew')

        if owner_type == Template.TemplateOwnerType.USER:
            if not user:
                raise serializers.ValidationError("User must be provided for USER owner_type.")
            if crew:
                raise serializers.ValidationError("Crew must not be provided for USER owner_type.")
        elif owner_type == Template.TemplateOwnerType.CREW:
            if not crew:
                raise serializers.ValidationError("Crew must be provided for CREW owner_type.")
            if user:
                raise serializers.ValidationError("User must not be provided for CREW owner_type.")
        elif owner_type == Template.TemplateOwnerType.COMMON:
            # Common templates might not have a user or crew owner.
            if user or crew:
                raise serializers.ValidationError("User or Crew must not be provided for COMMON owner_type.")
        else:
            # Handle potential future owner types or raise an error
            raise serializers.ValidationError(f"Invalid owner_type: {owner_type}")

        # Add more specific step validation if needed

        return data 

# Serializer for Plan (if needed independently, otherwise might be nested)
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'plan_list']
        # Consider making plan_list writable here if Plan is created/updated separately

class ChallengeSerializer(serializers.ModelSerializer):
    """Serializer for the Challenge model."""
    # plan = PlanSerializer() # Option 1: Nested serializer (read-only by default)
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all()) # Option 2: Use ID
    user = serializers.PrimaryKeyRelatedField(read_only=True) # Set in perform_create for USER type
    crew = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all(), allow_null=True, required=False)
    # kpi_description & kpi_metrics are likely generated by LLM, maybe read_only or set server-side?

    # Field to receive the initial plan description for LLM generation (not part of the model)
    initial_plan_description = serializers.CharField(write_only=True, required=False,
                                               help_text="Provide a description to generate the initial plan using LLM.")

    class Meta:
        model = Challenge
        fields = [
            'id',
            'plan', # If using PrimaryKeyRelatedField
            'user',
            'crew',
            'challenge_name',
            'deadline',
            'kpi_description',
            'kpi_metrics',
            'owner_type',
            'status',
            'created_at',
            'initial_plan_description', # Only for creation input
        ]
        read_only_fields = [
            'id',
            'user', # Set based on owner_type in view
            'kpi_description', # Assuming generated by LLM
            'kpi_metrics', # Assuming generated by LLM
            'created_at'
        ]

    def validate(self, data):
        """
        Validate owner_type and associated user/crew fields.
        Ensure plan is handled correctly (either ID provided or generated).
        """
        owner_type = data.get('owner_type')
        # User is set in perform_create, not taken from input for USER type
        crew = data.get('crew')

        # Validate owner type consistency
        if owner_type == Challenge.ChallengeOwnerType.USER:
            if crew:
                raise serializers.ValidationError("Crew must not be provided for USER owner_type challenge.")
        elif owner_type == Challenge.ChallengeOwnerType.CREW:
            if not crew:
                raise serializers.ValidationError("Crew must be provided for CREW owner_type challenge.")
        else:
            raise serializers.ValidationError(f"Invalid owner_type: {owner_type}")

        # Plan handling:
        # If initial_plan_description is provided, 'plan' might be optional initially
        # If initial_plan_description is NOT provided, 'plan' (ID) should be required
        initial_description = data.get('initial_plan_description')
        plan = data.get('plan')

        if not initial_description and not plan:
             raise serializers.ValidationError("Either 'plan' ID or 'initial_plan_description' must be provided.")
        if initial_description and plan:
             raise serializers.ValidationError("Provide either 'plan' ID or 'initial_plan_description', not both.")

        return data 


class RetrospectWeeklyAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for the RetrospectWeeklyAnalysis model."""
    # Decide if user/crew should be read_only or set based on context
    # If a template is created in a user context, user is set.
    # If created in a crew context, crew is set.
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    crew = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all(), allow_null=True, required=False)

    class Meta:
        model = RetrospectWeeklyAnalysis
        fields = [
            'id',
            'user',
            'crew',
            'summary',
            'weekly_kpi',
            'start_date',
            'end_date',
            'owner_type',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        """
        Ensure either user or crew is set based on owner_type,
        but not both (unless owner_type is COMMON, adjust if needed).
        """
        owner_type = data.get('owner_type')
        user = data.get('user')
        crew = data.get('crew')

        if owner_type == RetrospectWeeklyAnalysis.RetrospectWeeklyAnalysisOwnerType.USER:
            if not user:
                raise serializers.ValidationError("User must be provided for USER owner_type.")
            if crew:
                raise serializers.ValidationError("Crew must not be provided for USER owner_type.")
        elif owner_type == RetrospectWeeklyAnalysis.RetrospectWeeklyAnalysisOwnerType.CREW:
            if not crew:
                raise serializers.ValidationError("Crew must be provided for CREW owner_type.")
            if user:
                raise serializers.ValidationError("User must not be provided for CREW owner_type.")
        else:
            # Handle potential future owner types or raise an error
            raise serializers.ValidationError(f"Invalid owner_type: {owner_type}")

        # Add more specific step validation if needed

        return data 