from rest_framework import serializers
from retrospect.models import Challenge, Kpi, Plan, Retrospect
import json
from datetime import date

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

class TriggerWeeklyAnalysisSerializer(serializers.Serializer):
    challenge_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False, # challenge_ids가 없으면 모든 활성 챌린지 대상
        allow_empty=True, # 빈 리스트도 허용 (명시적으로 모든 활성 챌린지를 의미)
        help_text="분석을 실행할 챌린지 ID 리스트. 비어 있거나 제공되지 않으면 모든 활성 챌린지를 대상으로 지난주 분석을 실행합니다."
    )
    week_start_date = serializers.DateField(
        required=False,
        help_text="분석 시작일 (YYYY-MM-DD 형식). challenge_ids와 함께 제공될 때 사용됩니다. 없으면 지난주 월요일로 자동 계산됩니다."
    )
    week_end_date = serializers.DateField(
        required=False,
        help_text="분석 종료일 (YYYY-MM-DD 형식). challenge_ids와 함께 제공될 때 사용됩니다. 없으면 지난주 일요일로 자동 계산됩니다."
    )

    def validate(self, data):
        """
        week_start_date와 week_end_date의 유효성을 검사합니다.
        - 둘 다 제공되거나, 둘 다 제공되지 않아야 합니다.
        - week_start_date는 week_end_date보다 이전이어야 합니다.
        - challenge_ids가 제공되지 않은 경우, 날짜 필드는 무시되므로 유효성 검사를 건너뜁니다.
        """
        week_start = data.get('week_start_date')
        week_end = data.get('week_end_date')
        challenge_ids = data.get('challenge_ids')

        # challenge_ids가 명시적으로 제공되었을 때만 날짜 유효성 검사
        if challenge_ids is not None and len(challenge_ids) > 0: # None이거나 빈 리스트가 아닐 때
            if (week_start and not week_end) or (not week_start and week_end):
                raise serializers.ValidationError("week_start_date와 week_end_date는 함께 제공되거나 둘 다 제공되지 않아야 합니다.")
            
            if week_start and week_end and week_start > week_end:
                raise serializers.ValidationError("week_start_date는 week_end_date보다 이전이거나 같아야 합니다.")
        
        # challenge_ids가 None (제공되지 않음)이거나 빈 리스트일 경우, 날짜 필드는 사용되지 않으므로 특정 유효성 검사가 필요 없음.
        # 이 경우, tasks.py의 trigger_chunked_finalize_weekly_analyses 가 호출되어 자체적으로 날짜를 결정함.

        return data


class SimplePlanItemSerializer(serializers.ModelSerializer):
    """Simple serializer for individual plan items."""
    class Meta:
        model = Plan
        fields = ['id', 'plan_text']

class GeneratePlanResponseSerializer(serializers.Serializer):
    """Serializer for the generate plan API response."""
    user = serializers.IntegerField(source='user.id')
    challenge = serializers.IntegerField(source='challenge.id')
    plans = SimplePlanItemSerializer(many=True)

    def create(self, validated_data):
        # This serializer is for response representation, not for creating objects.
        raise NotImplementedError("This serializer is not meant for object creation.")

    def update(self, instance, validated_data):
        # This serializer is for response representation, not for updating objects.
        raise NotImplementedError("This serializer is not meant for object update.")

