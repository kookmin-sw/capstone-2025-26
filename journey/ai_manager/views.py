import os
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Q
import logging
from .serializers import (
    GenerateKpiRequestSerializer, GeneratePlanRequestSerializer, KpiListResponseSerializer,
    GenerateNextPlanSerializer, TriggerWeeklyAnalysisSerializer, GeneratePlanResponseSerializer
)
from .permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import timedelta, date
from django.shortcuts import get_object_or_404

from .services.kpi_generator import generate_kpis_for_challenge
from .services.plan_generator import generate_plan_from_challenge, generate_plan_from_retrospect
from .tasks import (
    trigger_chunked_finalize_weekly_analyses, 
    finalize_weekly_challenge_analysis, 
    get_week_start_end_dates
    )

from retrospect.models import Challenge, Plan, Retrospect, RetrospectWeeklyAnalysis
from retrospect.serializers import PlanSerializer, PlanResponseSerializer, RetrospectWeeklyAnalysisSerializer

import logging

logger = logging.getLogger(__name__)

kpi_list_example = {
    "kpis": [
        {
            "id": 1, "name": "Daily Coding Time", "definition": "Total time spent coding per day.",
            "measurement_unit": "hours", "data_type": "FLOAT", "challenge": 1, "user": 1
        },
        {
            "id": 2, "name": "Tasks Completed", "definition": "Number of tasks completed from the plan.",
            "measurement_unit": "count", "data_type": "INTEGER", "challenge": 1, "user": 1
        }
    ]
}

plan_list_example = [
    {
        "id": 1, "content": "Complete Chapter 1 of 'Advanced Python'",
        "start_date": "2024-08-01", "end_date": "2024-08-01", "status": "PENDING"
    },
    {
        "id": 2, "content": "Practice 5 LeetCode problems (Easy)",
        "start_date": "2024-08-01", "end_date": "2024-08-01", "status": "PENDING"
    }
]

single_plan_example = {
    "id": 3, "content": "Review today's progress and plan tomorrow",
    "start_date": "2024-08-02", "end_date": "2024-08-02", "status": "PENDING"
}

class GenerateKpiFromChallengeAPIView(generics.GenericAPIView):
    """
    Challenge, 여러 Plan, 및 선택적 사용자 컨텍스트를 사용하여 KPI를 자동 생성합니다.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateKpiRequestSerializer

    @swagger_auto_schema(
        operation_summary="Generate KPIs based on a challenge and multiple plans",
        operation_description="Generate KPIs for a challenge using multiple plans and optional context",
        request_body=GenerateKpiRequestSerializer,
        responses={
            201: openapi.Response(
                description="KPIs successfully generated",
                schema=KpiListResponseSerializer,
                examples={'application/json': kpi_list_example}
            ),
            400: openapi.Response("Bad request, invalid input parameters"),
            403: openapi.Response("Permission Denied"),
            404: openapi.Response("Challenge not found"),
            500: openapi.Response("Server error during KPI generation")
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_id = serializer.validated_data['challenge_id']
        plan_ids = serializer.validated_data['plan_ids']
        user_context = serializer.validated_data.get('context', '')
        item_count = serializer.validated_data.get('item_count', 3)
        
        try:
            challenge = Challenge.objects.get(id=challenge_id)
            
            # 사용자 권한 확인: 챌린지 소유자나 크루 멤버여야 함
            if challenge.owner_type == 'USER' and challenge.user != request.user:
                return Response(
                    {"error": "You don't have permission to generate KPIs for this challenge."},
                    status=status.HTTP_403_FORBIDDEN
                )
            elif challenge.owner_type == 'CREW':
                # 크루 챌린지의 경우 사용자가 해당 크루의 멤버인지 확인
                from crew.models import CrewMembership, CrewMembershipStatus
                is_member = CrewMembership.objects.filter(
                    user=request.user,
                    crew=challenge.crew,
                    status=CrewMembershipStatus.ACCEPTED
                ).exists()
                
                if not is_member:
                    return Response(
                        {"error": "You don't have permission to generate KPIs for this crew challenge."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # 각 계획이 해당 챌린지와 사용자에 속하는지 확인
            for plan_id in plan_ids:
                try:
                    Plan.objects.get(id=plan_id, challenge=challenge)
                except Plan.DoesNotExist:
                    return Response(
                        {"error": f"Plan with ID {plan_id} does not belong to this challenge or does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # KPI 생성 (여러 계획 ID를 직접 전달)
            kpis = generate_kpis_for_challenge(challenge, plan_ids, user_context, request.user, item_count)
            
            # 응답 생성 - KpiListResponseSerializer 사용
            response_serializer = KpiListResponseSerializer({"kpis": kpis})
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Challenge.DoesNotExist:
            return Response(
                {"error": f"Challenge with ID {challenge_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeneratePlanFromChallengeAPIView(generics.GenericAPIView):
    """
    Challenge와 선택적 사용자 컨텍스트를 사용하여 Plan을 자동 생성합니다.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratePlanRequestSerializer

    @swagger_auto_schema(
        operation_summary="Generate a plan based on a challenge",
        operation_description="Generate a plan based on a challenge and optional user context using LLM",
        request_body=GeneratePlanRequestSerializer,
        responses={
            201: openapi.Response(
                description="Plan successfully created",
                schema=GeneratePlanResponseSerializer,
                examples={'application/json': {
                    "user": 1,
                    "challenge": 1,
                    "plans": [
                        {"id": 1, "plan_text": "Complete Chapter 1 of 'Advanced Python'"},
                        {"id": 2, "plan_text": "Practice 5 LeetCode problems (Easy)"}
                    ]
                }},
            ),
            400: openapi.Response("Bad request, invalid input parameters"),
            403: openapi.Response("Permission Denied"),
            404: openapi.Response("Challenge not found"),
            500: openapi.Response("Server error during plan generation")
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_id = serializer.validated_data['challenge_id']
        user_context = serializer.validated_data.get('user_context', '')
        item_count = serializer.validated_data.get('item_count', 3)
        
        try:
            challenge = Challenge.objects.get(id=challenge_id)
            
            # 사용자 권한 확인: 챌린지 소유자나 크루 멤버여야 함
            if challenge.owner_type == 'USER' and challenge.user != request.user:
                return Response(
                    {"error": "You don't have permission to generate a plan for this challenge."},
                    status=status.HTTP_403_FORBIDDEN
                )
            elif challenge.owner_type == 'CREW':
                # 크루 챌린지의 경우 사용자가 해당 크루의 멤버인지 확인
                from crew.models import CrewMembership, CrewMembershipStatus
                is_member = CrewMembership.objects.filter(
                    user=request.user,
                    crew=challenge.crew,
                    status=CrewMembershipStatus.ACCEPTED
                ).exists()
                
                if not is_member:
                    return Response(
                        {"error": "You don't have permission to generate a plan for this crew challenge."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Plan 생성
            generated_plans = generate_plan_from_challenge(challenge, user_context, item_count)            # 새로운 직렬화 클래스로 응답 생성
            response_data = {
                "user": request.user.id,
                "challenge": challenge.id,
                "plans": generated_plans  # Plan model instances
            }
            
            # Use the improved serializer with the response data
            response_serializer = GeneratePlanResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Challenge.DoesNotExist:
            return Response(
                {"error": f"Challenge with ID {challenge_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"계획 생성 오류: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# 회고 쓰면 자동으로 생성되기 보다는
# 회고 쓰면 사용자한테 플랜 자동생성 할거냐 물어보고 하는게 나은것같아서 분리함
# GenericAPIView 쓴 이유는 swagger 문서 자동 생성을 위함 

class GenerateNextPlanAPIView(generics.GenericAPIView):
    """
    회고 내용을 기반으로 다음 계획(Plan)을 자동으로 생성하는 API View.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenerateNextPlanSerializer

    @swagger_auto_schema(
        operation_summary="회고를 기반으로 내일 계획 생성",
        operation_description="회고 내용을 분석하여 AI로 다음 날 계획을 자동 생성합니다",
        request_body=GenerateNextPlanSerializer,
        responses={
            201: openapi.Response(
                description="계획 생성 성공",
                schema=PlanResponseSerializer,
                examples={'application/json': single_plan_example}
            ),
            400: openapi.Response("잘못된 요청 파라미터"),
            403: openapi.Response("권한 없음"),
            404: openapi.Response("챌린지 또는 회고 찾을 수 없음"),
            500: openapi.Response("계획 생성 중 서버 오류")
        }
    )
    def post(self, request):
        user = request.user
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge_id = serializer.validated_data['challenge_id']
        retrospect_id = serializer.validated_data['retrospect_id']

        try:
            challenge = get_object_or_404(Challenge, id=challenge_id)
            retrospect = get_object_or_404(Retrospect, id=retrospect_id, challenge=challenge)

            # 회고 및 챌린지 소유자 권한 체크
            if retrospect.user != request.user:
                raise PermissionDenied("이 회고를 기반으로 계획을 생성할 권한이 없습니다.")

            # 회고 기반 계획 생성
            generated_plans = generate_plan_from_retrospect(challenge, retrospect)
            
            # 회고의 외래키에 생성한 Plan을 할당하고 저장
            retrospect.plan = generated_plans
            retrospect.save(update_fields=['plan'])
            
            # 새로운 직렬화 클래스로 응답 생성
            response_serializer = PlanResponseSerializer(generated_plans)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"회고 기반 계획 생성 오류: {str(e)}")
            return Response({"error": f"계획 생성 중 오류가 발생했습니n다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TriggerWeeklyAnalysisView(generics.GenericAPIView):
    """
    주간 챌린지 분석을 수동으로 트리거하는 API 뷰입니다.

    - POST:
        특정 챌린지 ID 리스트와 기간을 지정하거나, 모든 활성 챌린지에 대해 지난주 분석을 실행합니다.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TriggerWeeklyAnalysisSerializer

    @swagger_auto_schema(
        operation_summary="주간 챌린지 분석 트리거",
        operation_description="특정 챌린지에 대한 주간 분석을 수동으로 트리거합니다. challenge_ids를 비워두면 모든 활성 챌린지에 대해 지난주 분석이 실행됩니다.",
        request_body=TriggerWeeklyAnalysisSerializer,
        responses={
            status.HTTP_202_ACCEPTED: "분석 작업 요청 성공",
            status.HTTP_400_BAD_REQUEST: "잘못된 요청 파라미터",
            status.HTTP_403_FORBIDDEN: "권한 없음"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            challenge_ids = data.get('challenge_ids', [])
            week_start_input = data.get('week_start_date')
            week_end_input = data.get('week_end_date')
            
            # 사용자가 접근 가능한 챌린지 필터링
            user = request.user
            if challenge_ids:
                accessible_challenges = Challenge.objects.filter(
                    # 사용자 본인의 챌린지이거나
                    (Q(owner_type='USER') & Q(user=user) & Q(id__in=challenge_ids)) |
                    # 사용자가 속한 크루의 챌린지
                    (Q(owner_type='CREW') & Q(crew__members=user) & Q(id__in=challenge_ids))
                ).values_list('id', flat=True)
                
                if not accessible_challenges:
                    return Response(
                        {"error": "지정한 챌린지에 대한 접근 권한이 없습니다."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # 사용자가 지정한 특정 챌린지들에 대한 분석 실행
                if week_start_input and week_end_input:
                    # 사용자가 지정한 기간에 대한 분석
                    week_start_str = week_start_input.isoformat()
                    week_end_str = week_end_input.isoformat()
                else:
                    # 지난주 기간에 대한 분석
                    today = date.today()
                    target_date = today - timedelta(days=7)
                    week_start, week_end = get_week_start_end_dates(target_date)
                    week_start_str = week_start.isoformat()
                    week_end_str = week_end.isoformat()
                
                # 개별 챌린지에 대한 분석 태스크 실행
                for challenge_id in accessible_challenges:
                    finalize_weekly_challenge_analysis.delay(challenge_id, week_start_str, week_end_str)
                
                return Response(
                    {
                        "message": f"{len(accessible_challenges)}개 챌린지에 대한 주간 분석 작업이 성공적으로 요청되었습니다.",
                        "triggered_challenge_ids": list(accessible_challenges),
                        "week_start": week_start_str,
                        "week_end": week_end_str
                    },
                    status=status.HTTP_202_ACCEPTED
                )
            else:
                # 모든 활성화된 챌린지에 대해 일괄 분석 요청
                trigger_chunked_finalize_weekly_analyses.delay()
                return Response(
                    {"message": "모든 활성 챌린지에 대한 지난주 분석 작업이 성공적으로 요청되었습니다."},
                    status=status.HTTP_202_ACCEPTED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ChallengeWeeklyAnalysisView(generics.GenericAPIView):
    """
    Challenge별 주간회고분석 결과를 조회하는 API 뷰.
    
    GET 요청으로 challenge_ids 파라미터를 받아 해당하는 모든 주간회고분석 결과를 반환합니다.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Challenge별 주간회고분석 결과 조회",
        operation_description="주어진 Challenge ID 목록에 해당하는 모든 주간회고분석 결과를 반환합니다.",
        manual_parameters=[
            openapi.Parameter('challenge_ids', openapi.IN_QUERY, 
                description="쉼표로 구분된 Challenge ID 목록 (예: 1,2,3)", 
                type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('start_date', openapi.IN_QUERY, 
                description="시작 날짜 필터 (YYYY-MM-DD)", 
                type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('end_date', openapi.IN_QUERY, 
                description="종료 날짜 필터 (YYYY-MM-DD)", 
                type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            status.HTTP_200_OK: "성공적으로 주간회고분석 결과 반환",
            status.HTTP_400_BAD_REQUEST: "잘못된 요청 파라미터",
            status.HTTP_403_FORBIDDEN: "인증 실패",
            status.HTTP_404_NOT_FOUND: "데이터 없음"
        }
    )
    def get(self, request, *args, **kwargs):
        # challenge_ids 파라미터 추출
        challenge_ids_param = request.query_params.get('challenge_ids', '')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not challenge_ids_param:
            return Response(
                {"error": "challenge_ids 파라미터가 필요합니다 (예: ?challenge_ids=1,2,3)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 쉼표로 구분된 문자열을 정수 리스트로 변환
            challenge_ids = [int(id_str.strip()) for id_str in challenge_ids_param.split(',')]
        except ValueError:
            return Response(
                {"error": "challenge_ids는 쉼표로 구분된 정수 리스트여야 합니다 (예: 1,2,3)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 사용자가 접근 가능한 챌린지 필터링
        user = request.user
        accessible_challenges = Challenge.objects.filter(
            # 사용자 본인의 챌린지이거나
            (Q(owner_type='USER') & Q(user=user)) |
            # 사용자가 속한 크루의 챌린지
            (Q(owner_type='CREW') & Q(crew__members=user))
        ).values_list('id', flat=True)
        
        # 요청된 챌린지 ID와 접근 가능한 챌린지 ID의 교집합 계산
        allowed_challenge_ids = list(set(challenge_ids) & set(accessible_challenges))
        
        if not allowed_challenge_ids:
            return Response(
                {"error": "접근 가능한 챌린지가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # 쿼리 구성
        queryset = RetrospectWeeklyAnalysis.objects.filter(challenge_id__in=allowed_challenge_ids)
        
        # 선택적 날짜 필터 적용
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
            
        # 최신순 정렬
        queryset = queryset.order_by('-created_at')
        
        # 직렬화 및 응답
        serializer = RetrospectWeeklyAnalysisSerializer(queryset, many=True)
        
        if not serializer.data:
            return Response(
                {"message": "주어진 필터 조건에 맞는 주간회고분석 결과가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWeeklyAnalysisView(generics.GenericAPIView):
    """
    로그인한 사용자의 주간회고분석 결과를 모두 조회하는 API 뷰.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="사용자의 주간회고분석 결과 조회",
        operation_description="로그인한 사용자의 모든 주간회고분석 결과를 반환합니다.",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, 
                description="시작 날짜 필터 (YYYY-MM-DD)", 
                type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('end_date', openapi.IN_QUERY, 
                description="종료 날짜 필터 (YYYY-MM-DD)", 
                type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            status.HTTP_200_OK: "사용자의 주간회고분석 결과 반환 성공",
            status.HTTP_403_FORBIDDEN: "인증 실패",
            status.HTTP_404_NOT_FOUND: "데이터 없음"
        }
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = RetrospectWeeklyAnalysis.objects.filter(
            Q(user=user) | 
            Q(crew__members=user)
        )
        
        # 선택적 날짜 필터 적용
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
            
        queryset = queryset.order_by('-created_at')
        
        # 직렬화 및 응답
        serializer = RetrospectWeeklyAnalysisSerializer(queryset, many=True)
        
        if not serializer.data:
            return Response(
                {"message": "주어진 필터 조건에 맞는 주간회고분석 결과가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(serializer.data, status=status.HTTP_200_OK)
    @swagger_auto_schema(
        operation_summary="Trigger weekly analysis",
        operation_description="Manually triggers weekly challenge analysis. Provide 'challenge_ids' and optional 'week_start_date', 'week_end_date' to target specific challenges and period. If 'challenge_ids' is empty or not provided, analysis runs for all active challenges for the last week.",
        request_body=TriggerWeeklyAnalysisSerializer,
        responses={
            202: openapi.Response(
                description="Analysis task(s) accepted. The message indicates whether tasks were queued for all active challenges or specific ones.",
                examples={
                    'application/json_specific': {
                        "summary": "Trigger for specific challenges",
                        "value": {
                            "message": "2개의 챌린지에 대한 주간 분석 작업이 성공적으로 요청되었습니다.",
                            "triggered_challenge_ids": [1, 2],
                            "week_start": "2024-07-22",
                            "week_end": "2024-07-28"
                        }
                    },
                    'application/json_all_active': {
                        "summary": "Trigger for all active challenges",
                        "value": {
                            "message": "모든 활성 챌린지에 대한 지난주 분석 작업이 성공적으로 요청되었습니다."
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request. This can be due to validation errors in the request data (e.g., malformed dates, invalid challenge IDs) or if no valid challenges are found for processing.",
                examples={
                    'application/json_validation_error': {
                        "summary": "Serializer validation error",
                        "value": {
                            "challenge_ids": ["This field is required."],
                            "week_start_date": ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]
                        }
                    },
                    'application/json_no_valid_challenges': {
                        "summary": "No valid challenges to process",
                        "value": {
                            "message": "분석 작업을 요청할 유효한 챌린지가 없습니다."
                        }
                    },
                    'application/json_invalid_ids_provided': {
                        "summary": "Invalid or non-existent challenge IDs provided",
                        "value": {
                             "message": "제공된 챌린지 ID가 유효하지 않거나 존재하지 않습니다.",
                             "invalid_ids": [998, 999]
                        }
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = TriggerWeeklyAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            challenge_ids = data.get('challenge_ids')
            week_start_input = data.get('week_start_date')
            week_end_input = data.get('week_end_date')

            tasks_triggered_count = 0
            triggered_for_all_active = False

            if challenge_ids is not None and len(challenge_ids) > 0:
                # 특정 챌린지 ID가 제공된 경우
                logger.info(f"Manual trigger for specific challenges: {challenge_ids} with dates: {week_start_input} - {week_end_input}")
                
                # 날짜가 제공되지 않았으면, 지난주를 기준으로 계산
                if not week_start_input or not week_end_input:
                    today = date.today()
                    target_date_for_week_calc = today - timedelta(days=7)
                    week_start_obj, week_end_obj = get_week_start_end_dates(target_date_for_week_calc)
                else:
                    week_start_obj, week_end_obj = week_start_input, week_end_input
                
                week_start_str = week_start_obj.isoformat()
                week_end_str = week_end_obj.isoformat()

                # 실제 존재하는 챌린지 ID인지 확인 (선택적이지만 권장)
                valid_challenge_ids = list(Challenge.objects.filter(id__in=challenge_ids).values_list('id', flat=True))
                invalid_ids = set(challenge_ids) - set(valid_challenge_ids)
                if invalid_ids:
                    logger.warning(f"Invalid or non-existent challenge IDs provided: {invalid_ids}")
                
                for challenge_id in valid_challenge_ids:
                    finalize_weekly_challenge_analysis.delay(challenge_id, week_start_str, week_end_str)
                    tasks_triggered_count += 1

            else:
                # challenge_ids가 제공되지 않거나 빈 리스트인 경우 (모든 활성 챌린지 대상)
                logger.info("Manual trigger for all active challenges for the last week.")
                trigger_chunked_finalize_weekly_analyses.delay()
                triggered_for_all_active = True
                # 이 경우 실제 작업 수는 trigger_chunked_finalize_weekly_analyses 내부에서 결정됨
            
            if triggered_for_all_active:
                return Response({"message": "모든 활성 챌린지에 대한 지난주 분석 작업이 성공적으로 요청되었습니다."}, status=status.HTTP_202_ACCEPTED)
            
            elif tasks_triggered_count > 0:
                 return Response({
                    "message": f"{tasks_triggered_count}개의 챌린지에 대한 주간 분석 작업이 성공적으로 요청되었습니다.",
                    "triggered_challenge_ids": valid_challenge_ids,
                    "week_start": week_start_str,
                    "week_end": week_end_str
                }, status=status.HTTP_202_ACCEPTED)
            else:
                # 이 경우는 challenge_ids는 제공했으나 valid_challenge_ids가 비어있는 등의 예외적 상황
                return Response({"message": "분석 작업을 요청할 유효한 챌린지가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

