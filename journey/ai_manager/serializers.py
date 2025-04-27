from rest_framework import serializers
from retrospect.models import Challenge, Kpi, Plan, Retrospect # Import Plan and Retrospect models
import json

class LLMRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)

class LLMResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    
class AIQuerySerializer(serializers.Serializer):
    query_text = serializers.CharField(max_length=1000)

class GeneratePlanRequestSerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField(required=True, help_text="The ID of the challenge to generate plan for.")
    user_context = serializers.CharField(required=False, allow_blank=True, help_text="Optional additional context provided by the user.")
    item_count = serializers.IntegerField(required=False, default=3, min_value=1, max_value=5, 
                                         help_text="Number of plan items to generate (default: 3, range: 1-5)")

    def validate_challenge_id(self, value):
        """Check if the challenge exists."""
        if not Challenge.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Challenge with ID {value} does not exist.")
        return value

class GenerateKpiRequestSerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField(required=True, help_text="The ID of the challenge to generate KPIs for.")
    plan_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of plan IDs associated with the challenge."
    )
    context = serializers.CharField(required=False, allow_blank=True, help_text="Optional additional context provided by the user.")
    item_count = serializers.IntegerField(required=False, default=3, min_value=1, max_value=5, 
                                        help_text="Number of KPIs to generate (default: 3, range: 1-5)")

    def validate_plan_ids(self, value):
        """Check if all plans exist."""
        if not value:
            raise serializers.ValidationError("At least one plan ID is required.")
            
        invalid_ids = []
        for plan_id in value:
            if not Plan.objects.filter(id=plan_id).exists():
                invalid_ids.append(plan_id)
        
        if invalid_ids:
            raise serializers.ValidationError(f"Plans with IDs {invalid_ids} do not exist.")
        
        return value

    def validate_challenge_id(self, value):
        """Check if the challenge exists."""
        if not Challenge.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Challenge with ID {value} does not exist.")
        return value

# Serializer to represent the output structure of a generated KPI (used internally or in response)
class KpiOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kpi
        fields = ['id', 'name', 'definition', 'measurement_unit', 'data_type', 'challenge', 'user']
        read_only_fields = ['id', 'challenge', 'user'] # challenge and user are set contextually

# Separate serializer for the API response that contains a list of KPIs
class KpiListResponseSerializer(serializers.Serializer):
    kpis = KpiOutputSerializer(many=True)

# 회고를 기반으로 다음 계획 생성을 위한 serializer (retrospect에서 이동)
class GenerateNextPlanSerializer(serializers.Serializer):
    retrospect_id = serializers.IntegerField(required=True, help_text="회고 ID")
    challenge_id = serializers.IntegerField(required=True, help_text="챌린지 ID")
    
    def validate_retrospect_id(self, value):
        """회고가 존재하는지 확인"""
        if not Retrospect.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"회고 ID {value}이(가) 존재하지 않습니다.")
        return value
        
    def validate_challenge_id(self, value):
        """챌린지가 존재하는지 확인"""
        if not Challenge.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"챌린지 ID {value}이(가) 존재하지 않습니다.")
        return value
        
    def validate(self, data):
        """회고가 해당 챌린지에 속하는지 확인"""
        retrospect_id = data.get('retrospect_id')
        challenge_id = data.get('challenge_id')
        
        if retrospect_id and challenge_id:
            retrospect = Retrospect.objects.filter(id=retrospect_id, challenge_id=challenge_id).first()
            if not retrospect:
                raise serializers.ValidationError("해당 회고는 제공된 챌린지에 속하지 않습니다.")
                
        return data
