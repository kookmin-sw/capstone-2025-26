from rest_framework import serializers

class LLMRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)

class LLMResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    
class AIQuerySerializer(serializers.Serializer):
    query_text = serializers.CharField(max_length=1000)
