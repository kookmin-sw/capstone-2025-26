from rest_framework import permissions
from .models import Template, Challenge # Import necessary models

# Permission class for Retrospect (assuming it was defined here previously)
class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the object has a 'user' attribute and it's the request user
        if hasattr(obj, 'user') and obj.user is not None:
            return obj.user == request.user
        # Add logic here if ownership is determined differently for some models
        # e.g., for crew-owned objects, check crew membership
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
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if obj.owner_type == Template.TemplateOwnerType.USER:
            return obj.user == request.user
        elif obj.owner_type == Template.TemplateOwnerType.CREW:
            # Assumes user model has a 'crews' many-to-many field or similar
            try:
                return request.user.crews.filter(pk=obj.crew.pk).exists()
            except AttributeError:
                return False # User model might not have crews relationship
        elif obj.owner_type == Template.TemplateOwnerType.COMMON:
            return False # No modification for common templates by default
        return False

class IsChallengeOwnerOrCrewMemberOrReadOnly(permissions.BasePermission):
    """Permission for Challenges:
    - Read access is based on get_queryset.
    - Write access only for the owner (if USER type).
    - Write access for crew members (if CREW type).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if obj.owner_type == Challenge.ChallengeOwnerType.USER:
            return obj.user == request.user
        elif obj.owner_type == Challenge.ChallengeOwnerType.CREW:
            try:
                return request.user.crews.filter(pk=obj.crew.pk).exists()
            except AttributeError:
                return False
        return False