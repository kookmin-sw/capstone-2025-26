import os
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from .serializers import (
    LLMRequestSerializer, LLMResponseSerializer, AIQuerySerializer,
    GenerateKpiRequestSerializer, KpiOutputSerializer, GeneratePlanRequestSerializer, KpiListResponseSerializer,
    GenerateNextPlanSerializer
)
from .permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .services.kpi_generator import generate_kpis_for_challenge
from .services.plan_generator import generate_plan_from_challenge, generate_plan_from_retrospect
from retrospect.models import Challenge, Plan, Retrospect
from retrospect.serializers import PlanSerializer, PlanResponseSerializer
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

# Langchain 관련 임포트 
from langchain.chains import LLMChain
from langchain_google_vertexai.chat_models import ChatVertexAI
from langchain.prompts import PromptTemplate

# Import LangChain components with Vertex AI
import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION"),
    staging_bucket=os.getenv("BUCKET_NAME"),
)

llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",  # e.g., 'us-central1'
    model_name="gemini-2.0-flash-lite-001",
    max_output_tokens=1024,
    temperature=0.7,
)
# Initialize Langfuse handler
from langfuse.callback import CallbackHandler
# .env 파일에서 환경변수 지정해줘야함.
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"), 
)


class LLMViewSet(viewsets.ViewSet):
    """
    API endpoint for handling LLM requests.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["query_text"],
        properties={
            "query_text": openapi.Schema(type=openapi.TYPE_STRING, description="Input query text")
        }
    )
)
    @action(detail=False, methods=['post'], url_path='dummy', permission_classes=[permissions.AllowAny])
    def dummy(self, request):
        serializer = AIQuerySerializer(data=request.data)
        if (serializer.is_valid()):
            query_text = serializer.validated_data['query_text']

            # prompt 템플릿 생성: BasePromptTemplate 인스턴스를 사용
            prompt_template = PromptTemplate(
                template="Query: {query}\nResponse:",
                input_variables=["query"]
            )

            # 체인 구성: prompt는 query_text를 포함하는 형식으로 작성
            chain = LLMChain(llm=llm, prompt=prompt_template)

            try:
                # LLM 요청 실행
                response = chain.invoke({"query": query_text}, config={"callbacks": [langfuse_handler]})
                
                response_serializer = LLMResponseSerializer(data={'response': response})
                response_serializer.is_valid()  # 별도 유효성 검증 없이 데이터를 반환
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            201: KpiListResponseSerializer,
            400: "Bad request, invalid input parameters",
            404: "Challenge not found",
            500: "Server error during KPI generation"
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
                schema=PlanResponseSerializer
            ),
            400: "Bad request, invalid input parameters",
            404: "Challenge not found",
            500: "Server error during plan generation"
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
            generated_plans = generate_plan_from_challenge(challenge, user_context, item_count)
        
            # 새로운 직렬화 클래스로 응답 생성
            response_serializer = PlanResponseSerializer(generated_plans)
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
                schema=PlanResponseSerializer
            ),
            400: "잘못된 요청 파라미터",
            403: "권한 없음",
            404: "챌린지 또는 회고 찾을 수 없음",
            500: "계획 생성 중 서버 오류"
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
        

