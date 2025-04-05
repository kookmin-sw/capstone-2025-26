from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Crew, CrewMembership, CrewMembershipStatus, CrewMembershipRole
from .serializers import CrewSerializer, CrewMembershipSerializer
from .permissions import IsCrewCreatorOrReadOnly # Import the custom permission

# Create your views here.

class CrewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows crews to be viewed or edited.
    Also handles joining a crew.
    """
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    # Require authentication for all crew actions
    permission_classes = [permissions.IsAuthenticated, IsCrewCreatorOrReadOnly]

    @action(detail=False, methods=['get'], url_path='my-crews')
    def my_crews(self, request):
        """Returns a list of crews the current user is a member of."""
        user = request.user
        # Find memberships where the user is accepted
        memberships = CrewMembership.objects.filter(user=user, status=CrewMembershipStatus.ACCEPTED)
        # Get the crew objects from these memberships
        crews = [membership.crew for membership in memberships]
        # Serialize the crew data
        serializer = CrewSerializer(crews, many=True, context={'request': request}) # Pass request context for potential hyperlinked fields
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='join')
    def join_crew(self, request, pk=None):
        """Allows an authenticated user to join a specific crew.
        The first user to join becomes the CREATOR.
        """
        crew = self.get_object() # Gets the crew instance based on pk
        user = request.user

        # Check if membership already exists before determining the role
        try:
            membership = CrewMembership.objects.get(user=user, crew=crew)
            # Membership exists, handle re-join scenarios or return appropriate response
            if membership.status == CrewMembershipStatus.ACCEPTED:
                return Response({'detail': 'User is already a member of this crew.'}, status=status.HTTP_400_BAD_REQUEST)
            elif membership.status == CrewMembershipStatus.PENDING:
                return Response({'detail': 'Join request is already pending.'}, status=status.HTTP_400_BAD_REQUEST)
            elif membership.status == CrewMembershipStatus.REJECTED:
                # Decide if re-joining is allowed and what status/role it implies
                # For now, let's just say they can't rejoin automatically this way
                 return Response({'detail': 'Your previous join request was rejected. Please contact the crew admin.'}, status=status.HTTP_400_BAD_REQUEST)
                 # Or allow re-joining, potentially resetting status/role:
                 # membership.status = CrewMembershipStatus.ACCEPTED # Or PENDING
                 # membership.role = CrewMembershipRole.PARTICIPANT # Reset role?
                 # membership.save()
                 # serializer = CrewMembershipSerializer(membership)
                 # return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                 # Handle other potential existing statuses
                 return Response({'detail': 'Cannot process join request due to existing membership status.'}, status=status.HTTP_400_BAD_REQUEST)

        except CrewMembership.DoesNotExist:
            # No existing membership for this user, proceed to create one
            pass

        # Determine role based on whether the crew is empty *before* creating
        # Check for any accepted members currently in the crew
        is_first_member = not CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).exists()
        default_role = CrewMembershipRole.CREATOR if is_first_member else CrewMembershipRole.PARTICIPANT

        # Create the new membership
        membership = CrewMembership.objects.create(
            user=user,
            crew=crew,
            role=default_role,
            status=CrewMembershipStatus.ACCEPTED # Default to ACCEPTED, change to PENDING if approval is needed
        )

        # Update member_count
        # It's generally better to use aggregation or signals for member_count
        # but a simple increment works for now if status defaults to ACCEPTED.
        crew.member_count += 1
        crew.save(update_fields=['member_count'])

        serializer = CrewMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Fallback/unexpected case - should not be reached with current logic
        # return Response({'detail': 'Could not process join request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'], url_path='leave')
    def leave_crew(self, request, pk=None):
        """Allows an authenticated user to leave a specific crew."""
        crew = self.get_object() # Gets the crew instance based on pk
        user = request.user

        try:
            membership = CrewMembership.objects.get(user=user, crew=crew)
        except CrewMembership.DoesNotExist:
            return Response({'detail': 'You are not a member of this crew.'}, status=status.HTTP_404_NOT_FOUND)

        # Optional: Prevent creator from leaving?
        # if membership.role == CrewMembershipRole.CREATOR:
        #     return Response({'detail': 'Crew creator cannot leave the crew. You may need to delete the crew or transfer ownership first.'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the membership
        membership.delete()

        # Optional: Update member_count. Consider using signals for robustness.
        crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count() - 1 # Recalculate or decrement
        crew.save(update_fields=['member_count'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='members')
    def list_members(self, request, pk=None):
        """Returns a list of accepted members for a specific crew."""
        crew = self.get_object() # Gets the crew instance based on pk
        # Find accepted memberships for this crew
        memberships = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED)
        # Serialize the membership data (which includes user details)
        # Use CrewMembershipSerializer as it's designed to show membership details including the user
        serializer = CrewMembershipSerializer(memberships, many=True, context={'request': request})
        return Response(serializer.data)

    # Standard ModelViewSet actions (list, create, retrieve, update, destroy) are still available
