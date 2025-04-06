from rest_framework import permissions

# Permission class for Retrospect (assuming it was defined here previously)
class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the object has a 'user' attribute
        if hasattr(obj, 'user') and obj.user is not None:
            return obj.user == request.user
        # Add logic here if ownership is determined differently for some models
        return False

# Permission class specifically for Templates
class IsTemplateOwnerOrCrewMemberOrReadOnly(permissions.BasePermission):
    """Permission for Templates:
    - Read access for anyone (if listed by get_queryset).
    - Write access only for the owner (if USER type).
    - Write access for crew members (or admins - simplified for now) (if CREW type).
    - No write access for COMMON type for regular users.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed (controlled by get_queryset)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check write permissions based on owner_type
        if obj.owner_type == Template.TemplateOwnerType.USER:
            return obj.user == request.user
        elif obj.owner_type == Template.TemplateOwnerType.CREW:
            # Check if the user is part of the crew associated with the template
            # More granular control (e.g., only crew admin) might be needed later
            return request.user.is_authenticated and request.user.crews.filter(pk=obj.crew.pk).exists()
        elif obj.owner_type == Template.TemplateOwnerType.COMMON:
            # Disallow modification of common templates via API for now
            # Admins might have separate permissions
            return False
        return False # Default deny