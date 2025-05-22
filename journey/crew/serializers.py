from rest_framework import serializers
from .models import Crew, CrewMembership, CrewMembershipRole, CrewMembershipStatus
from user_manager.serializer import UserSerializer
from user_manager.models import User

class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ['id', 'crew_name', 'crew_description', 'member_count', 'crew_image']
        read_only_fields = ['id', 'member_count'] # member_count is likely managed internally

class CrewMembershipSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    crew = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all())

    class Meta:
        model = CrewMembership
        fields = [
            'id', 
            'user', 
            'user_details', 
            'crew', 
            'role', 
            'status', 
            'joined_at'
        ]
        read_only_fields = ['id', 'user_details', 'joined_at']
        # 'role' and 'status' are writable by default when not in read_only_fields.
        # 'user' and 'crew' (IDs) are now writable.

    def validate(self, data):
        # For updates, prevent changing the user or crew.
        if self.instance:
            if 'user' in data and data['user'] != self.instance.user:
                raise serializers.ValidationError(
                    {"user": "Cannot change the user of an existing membership."}
                )
            if 'crew' in data and data['crew'] != self.instance.crew:
                raise serializers.ValidationError(
                    {"crew": "Cannot change the crew of an existing membership."}
                )
        # For creates, user and crew are required.
        # Serializer automatically checks for required fields based on model,
        # but PrimaryKeyRelatedField makes them required.
        # Explicit check can be added if needed, but DRF handles it.
        return data

    def create(self, validated_data):
        # Ensure role is not CREATOR if crew already has a CREATOR
        crew = validated_data.get('crew')
        role = validated_data.get('role')
        if role == CrewMembershipRole.CREATOR:
            if CrewMembership.objects.filter(crew=crew, role=CrewMembershipRole.CREATOR, status=CrewMembershipStatus.ACCEPTED).exists():
                raise serializers.ValidationError(
                    {"role": "This crew already has a CREATOR."}
                )
        
        # If status is ACCEPTED, ensure role is set (default is PARTICIPANT if not CREATOR).
        # Model has default role, so this should be fine.

        return CrewMembership.objects.create(**validated_data)
