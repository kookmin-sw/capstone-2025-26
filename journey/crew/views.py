from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Crew, CrewMembership, CrewMembershipStatus, CrewMembershipRole
from .serializers import CrewSerializer, CrewMembershipSerializer
from .permissions import IsCrewCreatorOrReadOnly  # 커스텀 권한 클래스를 가져옵니다.
from retrospect.models import Template, Retrospect, Challenge, ChallengeStatus
from retrospect.serializers import TemplateSerializer, RetrospectSerializer, ChallengeSerializer
# Create your views here.

class CrewViewSet(viewsets.ModelViewSet):
    """
    크루 조회·수정 및 참여 처리 기능을 제공하는 API 엔드포인트입니다.
    """
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    # 모든 요청은 인증이 필요합니다.
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='my-crews')
    def my_crews(self, request):
        """현재 사용자가 속한 크루 목록을 반환합니다."""
        user = request.user
        memberships = CrewMembership.objects.filter(user=user, status=CrewMembershipStatus.ACCEPTED)
        crews = [membership.crew for membership in memberships]
        serializer = CrewSerializer(crews, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='join', permission_classes=[permissions.IsAuthenticated])
    def join_crew(self, request, pk=None):
        """인증된 사용자가 특정 크루에 참여하도록 처리합니다.
        PENDING 요청이 있으면 승인, 없으면 ACCEPTED 멤버십을 생성합니다.
        첫 승인된 사용자는 CREATOR 역할을 부여받습니다."""
        crew = self.get_object()
        user = request.user

        try:
            membership = CrewMembership.objects.get(user=user, crew=crew)
            # 기존 멤버십 상태에 따라 처리합니다.
            if membership.status == CrewMembershipStatus.ACCEPTED:
                return Response({'detail': '이미 크루 멤버입니다.'}, status=status.HTTP_400_BAD_REQUEST)

            elif membership.status == CrewMembershipStatus.PENDING:
                # 대기 중인 요청을 승인합니다.
                membership.status = CrewMembershipStatus.ACCEPTED
                # 첫 승인된 멤버인지 확인합니다.
                is_first_accepted = not CrewMembership.objects.filter(
                    crew=crew, 
                    status=CrewMembershipStatus.ACCEPTED
                ).exclude(pk=membership.pk).exists()
                
                if is_first_accepted:
                    membership.role = CrewMembershipRole.CREATOR
                else:
                    # 첫 번째가 아니면 PARTICIPANT 역할로 설정합니다.
                    membership.role = CrewMembershipRole.PARTICIPANT
                
                membership.save()
                
                # 멤버 수를 갱신합니다.
                crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count()
                crew.save(update_fields=['member_count'])
                
                serializer = CrewMembershipSerializer(membership)
                return Response(serializer.data, status=status.HTTP_200_OK)

            elif membership.status == CrewMembershipStatus.REJECTED:
                return Response({'detail': '이전 조인 요청이 거절되었습니다. 관리자에게 문의하세요.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': '현재 상태로 요청을 처리할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        except CrewMembership.DoesNotExist:
            # 기존 멤버십이 없으면 ACCEPTED 멤버십을 생성합니다.
            is_first_member = not CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).exists()
            default_role = CrewMembershipRole.CREATOR if is_first_member else CrewMembershipRole.PARTICIPANT

            membership = CrewMembership.objects.create(
                user=user,
                crew=crew,
                role=default_role,
                status=CrewMembershipStatus.ACCEPTED
            )

            # 멤버 수를 갱신합니다.
            crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count()
            crew.save(update_fields=['member_count'])

            serializer = CrewMembershipSerializer(membership)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='leave', permission_classes=[permissions.IsAuthenticated])
    def leave_crew(self, request, pk=None):
        """인증된 사용자가 특정 크루에서 탈퇴하도록 처리합니다."""
        crew = self.get_object() # Gets the crew instance based on pk
        user = request.user

        try:
            membership = CrewMembership.objects.get(user=user, crew=crew)
        except CrewMembership.DoesNotExist:
            return Response({'detail': '크루 멤버가 아닙니다.'}, status=status.HTTP_404_NOT_FOUND)

        # Delete the membership
        membership.delete()

        # 멤버 수를 갱신합니다.
        crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count()
        crew.save(update_fields=['member_count'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='members')
    def list_members(self, request, pk=None):
        """특정 크루의 승인된 멤버 목록을 반환합니다."""
        crew = self.get_object() # Gets the crew instance based on pk
        # 승인된 멤버십을 조회합니다.
        memberships = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED)
        # 직렬화하여 응답합니다.
        serializer = CrewMembershipSerializer(memberships, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='request-join', permission_classes=[permissions.IsAuthenticated])
    def request_join(self, request, pk=None):
        """인증된 사용자가 특정 크루 참여 요청을 생성합니다. (상태: PENDING)"""
        crew = self.get_object()
        user = request.user

        # Check if membership already exists
        try:
            membership = CrewMembership.objects.get(user=user, crew=crew)
            # Handle existing membership statuses
            if membership.status == CrewMembershipStatus.ACCEPTED:
                return Response({'detail': '이미 크루 멤버입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            elif membership.status == CrewMembershipStatus.PENDING:
                return Response({'detail': '이미 참여 요청이 대기 중입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            elif membership.status == CrewMembershipStatus.REJECTED:
                # 이전 요청이 거절된 경우, 상태를 PENDING으로 변경합니다.
                membership.status = CrewMembershipStatus.PENDING
                membership.save()
                serializer = CrewMembershipSerializer(membership)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': '현재 상태로 요청을 처리할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        except CrewMembership.DoesNotExist:
            # 기존 멤버십이 없으면 PENDING 멤버십을 생성합니다.
            pass

        # 첫 참여 요청인지 확인하여 잠재적 역할을 결정합니다.
        is_first_member_request = not CrewMembership.objects.filter(crew=crew).exists()
        potential_role = CrewMembershipRole.CREATOR if is_first_member_request else CrewMembershipRole.PARTICIPANT

        # Create the new membership request with PENDING status
        membership = CrewMembership.objects.create(
            user=user,
            crew=crew,
            role=potential_role,
            status=CrewMembershipStatus.PENDING # Set status to PENDING
        )

        # 주의: 멤버 수는 갱신하지 않습니다.

        serializer = CrewMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path=r'accept_member/(?P<user_pk>\d+)', permission_classes=[permissions.IsAuthenticated])
    def accept_request(self, request, pk=None, user_pk=None):
        """크루 생성자가 특정 사용자의 PENDING 요청을 승인합니다."""
        crew = self.get_object() # Gets the crew instance based on pk
        
        try:
            membership = CrewMembership.objects.get(crew=crew, user_id=user_pk)
        except CrewMembership.DoesNotExist:
            return Response({'detail': '해당 사용자의 멤버십 요청을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if membership.status != CrewMembershipStatus.PENDING:
            membership.status = CrewMembershipStatus.ACCEPTED
            membership.save()

            # 멤버 수를 갱신합니다.
            crew.member_count = CrewMembership.objects.filter(crew=crew, status=CrewMembershipStatus.ACCEPTED).count()
            crew.save(update_fields=['member_count'])

            serializer = CrewMembershipSerializer(membership)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': '해당 멤버십은 PENDING 상태가 아닙니다.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path=r'reject_member/(?P<user_pk>\d+)', permission_classes=[permissions.IsAuthenticated])
    def reject_request(self, request, pk=None, user_pk=None):
        """크루 생성자가 특정 사용자의 PENDING 요청을 거절합니다."""
        crew = self.get_object() # Gets the crew instance based on pk
        # Permission check (IsCrewCreatorOrReadOnly) is handled automatically by the viewset

        try:
            membership = CrewMembership.objects.get(crew=crew, user_id=user_pk)
        except CrewMembership.DoesNotExist:
            return Response({'detail': '해당 사용자의 멤버십 요청을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if membership.status != CrewMembershipStatus.PENDING:
            return Response({'detail': f'해당 멤버십은 PENDING 상태가 아닙니다 (현재 상태: {membership.status}).'}, status=status.HTTP_400_BAD_REQUEST)

        # Change status to REJECTED
        membership.status = CrewMembershipStatus.REJECTED
        membership.save()

        # Member count does not change as they were never accepted.

        serializer = CrewMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='templates')
    def crew_templates(self, request, pk=None):
        """특정 크루의 템플릿 목록을 반환합니다."""
        crew = self.get_object()
        templates = Template.objects.filter(crew=crew)
        serializer = TemplateSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='retrospects')
    def crew_retrospects(self, request, pk=None):
        """특정 크루의 회고 목록을 반환합니다."""
        crew = self.get_object()
        retrospects = Retrospect.objects.filter(crew=crew)
        serializer = RetrospectSerializer(retrospects, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='challenges')
    def crew_challenges(self, request, pk=None):
        """특정 크루의 챌린지 목록을 반환하며, 상태(status) 필터링을 지원합니다."""
        crew = self.get_object()
        user = request.user

        # 사용자가 해당 크루의 승인된 멤버인지 확인합니다.
        if not CrewMembership.objects.filter(crew=crew, user=user, status=CrewMembershipStatus.ACCEPTED).exists():
            return Response({'detail': '크루 멤버만 챌린지를 조회할 수 있습니다.'}, 
                            status=status.HTTP_403_FORBIDDEN)

        # Base queryset for the crew's challenges
        queryset = Challenge.objects.filter(crew=crew)

        # Filter by status query parameter
        status_filter = request.query_params.get('status', None)
        valid_statuses = [choice[0] for choice in ChallengeStatus.choices]
        
        if status_filter and status_filter in valid_statuses:
            queryset = queryset.filter(status=status_filter)
        elif status_filter:
            # 유효하지 않은 상태 필터는 무시하고 전체를 반환합니다.
            pass 

        # Serialize the (potentially filtered) challenges
        serializer = ChallengeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # 기본 list, create, retrieve, update, destroy 액션을 지원합니다.
