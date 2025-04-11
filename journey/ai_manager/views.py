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



