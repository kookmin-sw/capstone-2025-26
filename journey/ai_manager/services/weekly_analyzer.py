import os
import json
import re
import logging
from typing import List, Dict

from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langchain.chains import LLMChain
from langfuse.callback import CallbackHandler
from dotenv import load_dotenv

# Assuming Challenge model path, adjust if necessary
from retrospect.models import Challenge 

logger = logging.getLogger(__name__)

load_dotenv()

# --- LLM and Langfuse Setup for Weekly Analysis --- #
# We'll initialize these on demand to avoid issues with initialization timing
_weekly_llm = None
_langfuse_handler_weekly = None

def get_weekly_llm():
    """Get or initialize the weekly LLM instance"""
    global _weekly_llm
    if _weekly_llm is None:
        try:
            # 명시적 경로 확인 및 로깅
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            logger.info(f"Using credentials from: {credentials_path}")
            
            # Vertex AI 프로젝트 ID 확인
            project_id = os.getenv("PROJECT_ID")
            if not project_id:
                logger.error("PROJECT_ID environment variable is not set")
                raise ValueError("PROJECT_ID environment variable is not set")
            
            logger.info(f"Initializing Vertex AI with project: {project_id}")
            
            _weekly_llm = ChatVertexAI(
                project=project_id,
                location="us-central1",
                model_name="gemini-2.0-flash-lite-001",
                max_output_tokens=4000,
                temperature=0.7,
                request_timeout=120,  # 타임아웃 설정 추가
            )
            logger.info("Weekly LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize weekly LLM: {str(e)}", exc_info=True)
            raise e
    return _weekly_llm

def get_langfuse_handler():
    """Get or initialize the Langfuse handler"""
    global _langfuse_handler_weekly
    if _langfuse_handler_weekly is None:
        try:
            # 환경 변수 확인 및 로깅
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            host = os.getenv("LANGFUSE_HOST")
            
            if not secret_key or not public_key:
                logger.warning("Langfuse keys are missing. Skipping Langfuse initialization.")
                return None
            
            logger.info(f"Initializing Langfuse with host: {host}")
            
            _langfuse_handler_weekly = CallbackHandler(
                secret_key=secret_key,
                public_key=public_key,
                host=host,
            )
            logger.info("Langfuse handler initialized successfully")
        except Exception as e:
            logger.warning(f"Langfuse handler initialization error: {str(e)}. Token usage tracking disabled.")
            _langfuse_handler_weekly = None
    return _langfuse_handler_weekly


def generate_weekly_llm_summary(challenge: Challenge, weekly_kpi_scores: List[Dict], daily_feedback_snippets: List[str], week_start_str: str, week_end_str: str) -> Dict:
    """
    Calls LLM to generate weekly comment, challenge comment, and qualitative assessment.
    """
    try:
        # Get LLM and Langfuse handler lazily
        weekly_llm = get_weekly_llm()
        langfuse_handler_weekly = get_langfuse_handler()

        # Create prompt template
        prompt_template_str = """
        당신은 사용자의 주간 챌린지 진행 상황을 분석하고 종합적인 피드백을 제공하는 AI 코치입니다.

        챌린지 정보:
        - 이름: {challenge_name}
        - 설명: {challenge_description}
        - 분석 주간: {week_start} ~ {week_end}

        주간 KPI 성과 (평균 점수, 0.0 ~ 1.0 사이):
        {kpi_summary_list}

        이번 주 동안 기록된 일일 KPI 피드백 하이라이트:
        {daily_feedback_list}

        요청사항:
        위 정보를 바탕으로 다음 항목을 포함하는 JSON 응답을 생성해주세요:
        1.  `comment`: 이번 주 챌린지 수행에 대한 전반적인 격려와 통찰을 담은 피드백 (3-4 문장).
        2.  `summary`: 해당 챌린지에 대한 이번 주의 핵심 진행 상황이나 특징을 요약한 한 문장.
        3.  `assessment`: 이번 주 성과에 대한 질적 평가 (예: "훌륭한 진전", "꾸준한 노력 필요", "목표 초과 달성").

        모든 내용은 한국어로 작성하고, 반드시 요청된 JSON 형식으로만 응답해주세요. 추가적인 설명이나 인사말은 제외합니다.
        JSON 형식 예시:
        {{ "comment": "이번 주 [챌린지 명] 도전에 꾸준히 참여하며 특히 [긍정적 KPI 명]에서 좋은 성과를 보여주셨네요. [개선점이나 다음 주 격려]...", "summary": "[챌린지 명]을 통해 사용자는 이번 주 [핵심 성과/경험]을 달성했습니다.", "assessment": "좋은 시도" }}
        """
        
        prompt = PromptTemplate(
            input_variables=["challenge_name", "challenge_description", "week_start", "week_end", "kpi_summary_list", "daily_feedback_list"],
            template=prompt_template_str
        )
        chain = prompt | weekly_llm

        # Prepare input data
        kpi_summary_str = "- 데이터 없음" 
        if weekly_kpi_scores:
            kpi_summary_str = "".join([f"- {item['name']}: {item['avg_score']:.2f}\\n" for item in weekly_kpi_scores])
        
        daily_feedback_str = "- 피드백 없음"
        if daily_feedback_snippets:
            daily_feedback_str = "".join([f"- {snippet}\\n" for snippet in daily_feedback_snippets[:15]]) # Max 15 daily snippets

        input_data = {
            "challenge_name": challenge.challenge_name,
            "challenge_description": challenge.description or "N/A",
            "week_start": week_start_str,
            "week_end": week_end_str,
            "kpi_summary_list": kpi_summary_str,
            "daily_feedback_list": daily_feedback_str,
        }

        # Set up callbacks
        callbacks = []
        if langfuse_handler_weekly:
            callbacks.append(langfuse_handler_weekly)
            logger.info("Langfuse callback handler added")

        # Log detailed debug information
        logger.info(f"Starting LLM invocation for challenge: {challenge.id}")
        logger.info(f"Input data preview: challenge={challenge.challenge_name}, kpi_count={len(weekly_kpi_scores)}, feedback_count={len(daily_feedback_snippets)}")
        
        # Invoke LLM
        response_text = chain.invoke(input_data, config={"callbacks": callbacks} if callbacks else {})
        
        # Process response
        if hasattr(response_text, "content"):
            response_text = response_text.content
            logger.info(f"Received LLM response as AIMessage object")
        else:
            logger.info(f"Received LLM response of type: {type(response_text)}")
        
        logger.info(f"Raw LLM response (first 200 chars): {str(response_text)[:200]}...")
        
        # Try to extract JSON from response
        match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
            logger.info("Successfully extracted JSON from code block")
        else:
            json_str = response_text
            logger.info("No JSON code block found, using raw response")
        
        # Parse JSON
        llm_output = json.loads(json_str)
        logger.info(f"Successfully parsed JSON output with keys: {list(llm_output.keys())}")
        
        return llm_output
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error in weekly_analyzer for challenge {challenge.id}: {e}. Response: {response_text[:500]}")
        return {"comment": "분석 중 오류가 발생했습니다. JSON 파싱 실패", "summary": "데이터 처리 오류", "assessment": "평가 불가"}
    except Exception as e:
        logger.error(f"Error in weekly_analyzer for challenge {challenge.id}: {e}", exc_info=True)
        return {"comment": "분석 중 오류가 발생했습니다.", "summary": "기술적 문제 발생", "assessment": "평가 불가"}
    finally:
        # Ensure Langfuse handler is flushed
        try:
            langfuse_handler = get_langfuse_handler()
            if langfuse_handler:
                langfuse_handler.flush()
                logger.info("Langfuse handler flushed")
        except Exception as e:
            logger.warning(f"Error flushing Langfuse handler: {e}")
