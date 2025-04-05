from rest_framework import permissions
from .models import CrewMembership, CrewMembershipRole

class IsCrewCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of a crew to edit or delete it.
    Assumes the user is already authenticated.
    Read operations are allowed for any authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the crew.
        # Check if a membership exists for the requesting user and this crew,
        # and if that membership role is CREATOR.
        try:
            membership = CrewMembership.objects.get(crew=obj, user=request.user)
            return membership.role == CrewMembershipRole.CREATOR
        except CrewMembership.DoesNotExist:
            # If the user is not a member at all, they certainly aren't the creator.
            return False 