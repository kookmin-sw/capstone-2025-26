from rest_framework import serializers
from .models import Crew, CrewMembership
from user_manager.serializer import UserSerializer

class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ['id', 'crew_name', 'crew_description', 'member_count', 'crew_image']
        read_only_fields = ['id', 'member_count'] # member_count is likely managed internally

class CrewMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    crew = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CrewMembership
        fields = ['id', 'user', 'crew', 'role', 'status', 'joined_at']
        read_only_fields = ['id', 'user', 'crew', 'role', 'status', 'joined_at']
