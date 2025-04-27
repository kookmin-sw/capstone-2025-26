import os
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import AIQuerySerializer, LLMResponseSerializer
from .permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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
        if serializer.is_valid():
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
                schema=PlanSerializer
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
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            raise NotFound("해당 챌린지를 찾을 수 없습니다.")

        try:
            retrospect = Retrospect.objects.get(id=retrospect_id, challenge=challenge)
        except Retrospect.DoesNotExist:
            raise NotFound("회고가 존재하지 않거나 이 챌린지에 속하지 않습니다.")

        if retrospect.user != user:
            raise PermissionDenied("이 회고에 대한 접근 권한이 없습니다.")

        try:
            plan = generate_plan_from_retrospect(challenge, retrospect)
            # 회고의 외래키에 생성한 Plan을 할당하고 저장
            retrospect.plan = plan
            retrospect.save(update_fields=['plan'])
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        plan_serializer = PlanSerializer(plan)
        return Response({"plan": plan_serializer.data}, status=201)
