from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Q
from .models import Retrospect, Template
from .serializers import RetrospectSerializer, TemplateSerializer
from crew.models import Crew
from .permissions import IsOwnerOrReadOnly, IsTemplateOwnerOrCrewMemberOrReadOnly
# Create your views here.


class RetrospectViewSet(viewsets.ModelViewSet):
    """ViewSet for the Retrospect model."""
    serializer_class = RetrospectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Returns a queryset containing only the retrospects created by the
        currently authenticated user.
        """
        user = self.request.user
        # Ensure the user is authenticated to view their retrospects
        if not user.is_authenticated:
            return Retrospect.objects.none() # Return empty queryset for anonymous users

        # Filter to only include retrospects where the user is the author
        return Retrospect.objects.select_related(
            'user', 'crew', 'challenge', 'template'
        ).filter(user=user)

    def perform_create(self, serializer):
        """Set the user field automatically when creating a retrospect."""
        serializer.save(user=self.request.user)

    # Add specific actions if needed, e.g., linking to crew, etc.
    # Example: List retrospects for a specific challenge or user might be useful
    # @action(detail=False, methods=['get'], url_path='by-challenge/(?P<challenge_id>\\d+)')
    # def by_challenge(self, request, challenge_id=None):
    #     ...

    # @action(detail=False, methods=['get'], url_path='my-retrospects')
    # def my_retrospects(self, request):
    #    ...

class TemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for the Template model."""
    serializer_class = TemplateSerializer
    # Use IsAuthenticatedOrReadOnly for create/list, custom perm for object-level R/U/D
    permission_classes = [IsAuthenticatedOrReadOnly, IsTemplateOwnerOrCrewMemberOrReadOnly]

    def get_queryset(self):
        """Filter templates:
        - Authenticated users see COMMON templates, their own USER templates,
          and templates belonging to Crews they are members of.
        - Unauthenticated users see only COMMON templates.
        """
        user = self.request.user
        base_queryset = Template.objects.select_related('user', 'crew').all()

        if user.is_authenticated:
            try:
                user_crews = user.crews.all()
            except AttributeError:
                user_crews = Crew.objects.none()

            return base_queryset.filter(
                Q(owner_type=Template.TemplateOwnerType.COMMON) |
                Q(owner_type=Template.TemplateOwnerType.USER, user=user) |
                Q(owner_type=Template.TemplateOwnerType.CREW, crew__in=user_crews)
            ).distinct()
        else:
            # Unauthenticated users only see common templates
            return base_queryset.filter(owner_type=Template.TemplateOwnerType.COMMON)

    def perform_create(self, serializer):
        """Set user or crew based on owner_type if not provided.
           Validate that the user can create the specified type.
        """
        owner_type = serializer.validated_data.get('owner_type')
        user = self.request.user

        if owner_type == Template.TemplateOwnerType.USER:
            # Assign the current user if creating a USER template
            serializer.save(user=user, crew=None) # Explicitly set crew to None
        elif owner_type == Template.TemplateOwnerType.CREW:
            # Crew must be provided in the request data for CREW type
            # The serializer validates its presence.
            # We should also validate if the user is part of the specified crew.
            crew = serializer.validated_data.get('crew')
            if not user.crews.filter(pk=crew.pk).exists():
                 raise permissions.PermissionDenied("You do not have permission to create a template for this crew.")
            serializer.save(user=None) # Explicitly set user to None
        elif owner_type == Template.TemplateOwnerType.COMMON:
            # Optionally restrict who can create COMMON templates (e.g., admins)
            # For now, assume any authenticated user can, but without user/crew link
            # Add permission check here if needed: if not user.is_staff: raise ...
            serializer.save(user=None, crew=None)
        else:
            # Should be caught by serializer validation, but as a safeguard:
            super().perform_create(serializer)
