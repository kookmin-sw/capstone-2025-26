from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Crew, CrewMembership, CrewMembershipStatus, CrewMembershipRole
from .serializers import CrewSerializer, CrewMembershipSerializer
from .permissions import IsCrewCreatorOrReadOnly # Import the custom permission
from retrospect.models import Template, Retrospect, Challenge, ChallengeStatus
from retrospect.serializers import TemplateSerializer, RetrospectSerializer, ChallengeSerializer
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
        If the user has a PENDING request, it accepts it.
        If the user has no request, it creates an ACCEPTED membership.
        The first user to be ACCEPTED becomes the CREATOR.
        """
        crew = self.get_object()
        user = request.user

        try:
            membership = CrewMembership.objects.get(user=user, crew=crew)
            # Membership exists, handle based on status
            if membership.status == CrewMembershipStatus.ACCEPTED:
                return Response({'detail': 'User is already a member of this crew.'}, status=status.HTTP_400_BAD_REQUEST)

            elif membership.status == CrewMembershipStatus.PENDING:
                # Accept the pending request
                membership.status = CrewMembershipStatus.ACCEPTED
                # Check if this user is now the first accepted member
                is_first_accepted = not CrewMembership.objects.filter(
                    crew=crew, 
                    status=CrewMembershipStatus.ACCEPTED
                ).exclude(pk=membership.pk).exists() # Exclude self if checking before save
                
                if is_first_accepted:
                    membership.role = CrewMembershipRole.CREATOR
                else:
                    # Ensure role is participant if not the first (might have been wrongly assigned CREATOR on request)
                    membership.role = CrewMembershipRole.PARTICIPANT
                
                membership.save()
                
                # Update member count
                crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count()
                crew.save(update_fields=['member_count'])
                
                serializer = CrewMembershipSerializer(membership)
                return Response(serializer.data, status=status.HTTP_200_OK) # OK, as we updated existing

            elif membership.status == CrewMembershipStatus.REJECTED:
                 return Response({'detail': 'Your previous join request was rejected. Please contact the crew admin.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                 return Response({'detail': 'Cannot process join request due to existing membership status.'}, status=status.HTTP_400_BAD_REQUEST)

        except CrewMembership.DoesNotExist:
            # No existing membership, create a new ACCEPTED one
            # Determine role based on whether the crew has accepted members *before* creating
            is_first_member = not CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).exists()
            default_role = CrewMembershipRole.CREATOR if is_first_member else CrewMembershipRole.PARTICIPANT

            membership = CrewMembership.objects.create(
                user=user,
                crew=crew,
                role=default_role,
                status=CrewMembershipStatus.ACCEPTED
            )

            # Update member_count
            crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count()
            crew.save(update_fields=['member_count'])

            serializer = CrewMembershipSerializer(membership)
            return Response(serializer.data, status=status.HTTP_201_CREATED) # CREATED, as it's new

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
        crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count() # Recalculate or decrement
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

    @action(detail=True, methods=['post'], url_path='request-join')
    def request_join(self, request, pk=None):
        """Allows an authenticated user to request joining a specific crew.
        Creates a membership record with PENDING status.
        """
        crew = self.get_object()
        user = request.user

        # Check if membership already exists
        try:
            membership = CrewMembership.objects.get(user=user, crew=crew)
            # Handle existing membership statuses
            if membership.status == CrewMembershipStatus.ACCEPTED:
                return Response({'detail': 'User is already a member of this crew.'}, status=status.HTTP_400_BAD_REQUEST)
            elif membership.status == CrewMembershipStatus.PENDING:
                return Response({'detail': 'Join request is already pending.'}, status=status.HTTP_400_BAD_REQUEST)
            elif membership.status == CrewMembershipStatus.REJECTED:
                 return Response({'detail': 'Your previous join request was rejected. Please contact the crew admin to rejoin.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                 return Response({'detail': 'Cannot process join request due to existing membership status.'}, status=status.HTTP_400_BAD_REQUEST)

        except CrewMembership.DoesNotExist:
            # No existing membership for this user, proceed to create a PENDING request
            pass

        # Determine potential role if approved (first requester might become creator)
        is_first_member_request = not CrewMembership.objects.filter(crew=crew).exists()
        potential_role = CrewMembershipRole.CREATOR if is_first_member_request else CrewMembershipRole.PARTICIPANT

        # Create the new membership request with PENDING status
        membership = CrewMembership.objects.create(
            user=user,
            crew=crew,
            role=potential_role, # Assign potential role, can be confirmed/changed on approval
            status=CrewMembershipStatus.PENDING # Set status to PENDING
        )

        # Note: Member count is NOT updated here.

        serializer = CrewMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path=r'reject_member/(?P<user_pk>\d+)')
    def reject_request(self, request, pk=None, user_pk=None):
        """Allows the crew creator to reject a PENDING join request from a specific user."""
        crew = self.get_object() # Gets the crew instance based on pk
        # Permission check (IsCrewCreatorOrReadOnly) is handled automatically by the viewset

        try:
            membership = CrewMembership.objects.get(crew=crew, user_id=user_pk)
        except CrewMembership.DoesNotExist:
            return Response({'detail': 'Membership request not found for this user in this crew.'}, status=status.HTTP_404_NOT_FOUND)

        if membership.status != CrewMembershipStatus.PENDING:
            return Response({'detail': f'This membership is not pending (status: {membership.status}). Cannot reject.'}, status=status.HTTP_400_BAD_REQUEST)

        # Change status to REJECTED
        membership.status = CrewMembershipStatus.REJECTED
        membership.save()

        # Member count does not change as they were never accepted.

        serializer = CrewMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_200_OK) # OK, showing the rejected status

    @action(detail=True, methods=['get'], url_path='templates')
    def crew_templates(self, request):
        """Returns a list of templates for a specific crew."""
        crew = self.get_object()
        templates = Template.objects.filter(crew=crew)
        serializer = TemplateSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='retrospects')
    def crew_retrospects(self, request):
        """Returns a list of retrospects for a specific crew."""
        crew = self.get_object()
        retrospects = Retrospect.objects.filter(crew=crew)
        serializer = RetrospectSerializer(retrospects, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='challenges')
    def crew_challenges(self, request, pk=None):
        """Returns a list of challenges for a specific crew, optionally filtered by status.

        Checks if the user is a member of the crew.
        Filters by status query param: ?status=LIVE / SUCCESS / FAIL
        """
        crew = self.get_object()
        user = request.user

        # Check if user is an accepted member of the crew
        if not CrewMembership.objects.filter(crew=crew, user=user, status=CrewMembershipStatus.ACCEPTED).exists():
            # Optionally, allow public viewing or creator override depending on deeper permission logic
            return Response({'detail': 'You must be a member of this crew to view its challenges.'}, 
                            status=status.HTTP_403_FORBIDDEN)

        # Base queryset for the crew's challenges
        queryset = Challenge.objects.filter(crew=crew)

        # Filter by status query parameter
        status_filter = request.query_params.get('status', None)
        valid_statuses = [choice[0] for choice in ChallengeStatus.choices]
        
        if status_filter and status_filter in valid_statuses:
            queryset = queryset.filter(status=status_filter)
        elif status_filter:
             # Optional: Return error for invalid status, or just ignore it and return all
             # For now, ignore invalid status and return all challenges for the crew
             pass 

        # Serialize the (potentially filtered) challenges
        serializer = ChallengeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # Standard ModelViewSet actions (list, create, retrieve, update, destroy) are still available
