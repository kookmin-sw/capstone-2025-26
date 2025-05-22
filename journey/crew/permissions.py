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

class IsMembershipOwnerOrCrewCreatorOrAdmin(permissions.BasePermission):
    """
    Custom permission for CrewMembershipViewSet.
    - List/Retrieve: Any authenticated user.
    - Create: Admin users only.
    - Update (role, status): Admin users or the creator of the crew.
    - Delete: Admin users, the creator of the crew, or the user themselves.
    """

    def has_permission(self, request, view):
        # Allow list and retrieve for any authenticated user
        if view.action in ['list', 'retrieve']:
            return request.user and request.user.is_authenticated
        
        # Allow create only for admin users
        if view.action == 'create':
            return request.user and request.user.is_staff
        
        # For other actions (update, partial_update, destroy), 
        # permission is checked at the object level by has_object_permission.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj is a CrewMembership instance
        if not request.user or not request.user.is_authenticated:
            return False

        is_admin = request.user.is_staff
        is_crew_creator = False
        try:
            # Check if the request.user is the creator of the crew associated with the membership
            crew_creator_membership = CrewMembership.objects.get(
                crew=obj.crew, 
                role=CrewMembershipRole.CREATOR, 
                status='ACCEPTED' # Ensuring the creator is an accepted member
            )
            is_crew_creator = crew_creator_membership.user == request.user
        except CrewMembership.DoesNotExist:
            # No creator found for this crew, or creator is not accepted.
            # This scenario should ideally not happen if crews always have a creator.
            is_crew_creator = False

        is_membership_owner = obj.user == request.user

        if view.action in ['update', 'partial_update']:
            # Allow update if admin or crew creator
            return is_admin or is_crew_creator
        
        if view.action == 'destroy':
            # Allow delete if admin, crew creator, or membership owner
            return is_admin or is_crew_creator or is_membership_owner

        # Default deny for any other unhandled actions, though typically covered by has_permission
        return False 