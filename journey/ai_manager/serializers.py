from rest_framework import serializers

class LLMRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)

class LLMResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    
class AIQuerySerializer(serializers.Serializer):
    query_text = serializers.CharField(max_length=1000)
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
