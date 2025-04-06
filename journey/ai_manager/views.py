# views.py
import os
from django.http import JsonResponse
from django.views import View

# Langchain 관련 임포트 (기본 Langchain 및 langchain_community 사용 예)
from langchain.llms import BaseLLM
from langchain.chains import LLMChain

# Import LangChain components with Vertex AI
from langchain_google_vertexai import ChatVertexAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# SerpAPI를 통한 Google 검색 결과 보강 (옵션)
from langchain.utilities import GoogleSearchAPIWrapper

# Langfuse 트레이싱 임포트 (가상의 예시)
from langfuse import LangfuseClient

# Langfuse 클라이언트 초기화 (환경변수에서 API 키를 가져온다고 가정)
lf_client = LangfuseClient(api_key=os.getenv("LANGFUSE_API_KEY"))

class LLMRequestView(View):
    def post(self, request, *args, **kwargs):
        # 클라이언트로부터 요청 데이터 가져오기
        input_text = request.POST.get("input", "")
        
        # (옵션) 검색 보강: GoogleSearchAPIWrapper 사용
        google_search = GoogleSearchAPIWrapper(api_key=os.getenv("SERPAPI_API_KEY"),
                                               engine="google")
        search_results = google_search.run(input_text)  # 간단한 검색 호출
        
        # Gemini Flash Lite 2.0 호출: langchain_community나 자체 래퍼 사용
        llm = GeminiFlashLiteLLM(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_version="flash_lite_2.0",
            extra_context=search_results  # 검색 결과를 컨텍스트에 포함 (옵션)
        )
        
        # 체인 구성: 예시로 간단한 체인을 사용 (실제 체인은 요구사항에 맞게 구성)
        chain = LLMChain(llm=llm, prompt_template="Input: {input}\nResponse:")
        
        # Langfuse에 요청 시작 로그 기록
        lf_client.log_event(event_type="llm_request_start", details={"input": input_text})
        
        try:
            # LLM 요청 실행
            response = chain.run({"input": input_text})
            
            # Langfuse에 성공 로그 기록
            lf_client.log_event(event_type="llm_request_success", details={"response": response})
            
            return JsonResponse({"response": response})
        except Exception as e:
            # Langfuse에 에러 로그 기록
            lf_client.log_event(event_type="llm_request_error", details={"error": str(e)})
            return JsonResponse({"error": str(e)}, status=500)
