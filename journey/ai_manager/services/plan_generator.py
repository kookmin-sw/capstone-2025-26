import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from retrospect.models import Plan, Kpi
import os
import re
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
import dotenv

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# LangChain LLM 설정
llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    model_name="gemini-2.0-flash-lite-001",
    max_output_tokens=1024,
    temperature=0.7,
)

# Langfuse 핸들러 초기화
try:
    langfuse_handler = CallbackHandler(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
except Exception as e:
    print(f"Langfuse 핸들러 초기화 오류: {str(e)}")
    # Langfuse 핸들러 초기화 실패 시 None으로 설정
    langfuse_handler = None


def parse_llm_response(response_text: str) -> Dict[str, str]:
    """LLM 응답을 파싱하여 계획 항목 딕셔너리를 반환하는 유틸리티 함수"""
    logger.info(f"Parsing LLM response: {response_text[:200]}...")
    
    # 1. 직접 JSON 파싱 시도
    try:
        plan_data = json.loads(response_text)
        if isinstance(plan_data, dict):
            return plan_data
    except json.JSONDecodeError:
        pass  # 다음 방법으로 넘어감
    
    # 2. 정규 표현식으로 JSON 추출 시도
    match = re.search(r'\{.*?\}', response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass  # 파싱 실패
    
    # 모든 파싱 방법 실패
    raise ValueError("LLM 응답에서 유효한 계획 데이터를 추출할 수 없습니다.")


def generate_plan_from_retrospect(challenge, retrospect):
    """
    회고 내용을 바탕으로 다음날 계획(Plan)을 생성하고 DB에 저장
    각 계획 항목을 별도의 Plan 레코드로 저장
    """
    # 현재 챌린지에 대한 KPI 데이터 가져오기 (새로운 모델 구조 반영)
    kpis = Kpi.objects.filter(challenge=challenge, user=retrospect.user)
    
    # KPI 정보를 포맷팅하여 프롬프트에 포함할 문자열 생성
    kpi_info = []
    for kpi in kpis:
        kpi_info.append({
            "name": kpi.name,
            "definition": kpi.definition,
            "measurement_unit": kpi.measurement_unit,
            "data_type": kpi.data_type
        })
    
    # 프롬프트 - JSON 형식 출력을 요청하도록 수정
    template_str = (Path(__file__).parent.parent / "templates" / "plan_from_retrospect_prompt.txt").read_text(encoding="utf-8")
    prompt = PromptTemplate(
        input_variables=["challenge_name", "kpi_info", "retrospect_content"],
        template=template_str
    )

    # 🔹 2. LLMChain 생성
    chain = prompt | llm

    # 🔹 3. 입력값 구성
    input_data = {
        "challenge_name": challenge.challenge_name,
        "kpi_info": json.dumps(kpi_info, ensure_ascii=False) if kpi_info else "KPI 정보가 없습니다.",
        "retrospect_content": retrospect.content,
    }

    # 🔹 4. LLM 실행 + Plan 저장
    try:
        # Langfuse 핸들러가 None이면 콜백 없이 실행
        callbacks = [langfuse_handler] if langfuse_handler else []
        response = chain.invoke(input_data, config={"callbacks": callbacks})
        
        # 응답이 dict 형태이고 "text" 키가 있다면 해당 값을 사용
        if isinstance(response, dict) and "text" in response:
            response_str = str(response["text"]).strip()
        else:
            response_str = str(response).strip()

        logger.debug("Response String for Parsing: %s", response_str[:200])
        
        # 응답을 JSON으로 파싱
        plan_items = parse_llm_response(response_str)
        
        # 반환할 계획 목록
        plans = []
        
        # 각 계획 항목을 별도의 Plan 레코드로 저장
        for _, plan_text in plan_items.items():
            plan = Plan.objects.create(
                plan_text=plan_text,
                user=retrospect.user,
                challenge=challenge
            )
            plans.append(plan)
            
        logger.info(f"총 {len(plans)}개의 계획 항목이 생성되었습니다. (사용자: {retrospect.user.id}, 챌린지: {challenge.id})")
        
        return plans

    except Exception as e:
        logger.error(f"계획 생성 실패: {str(e)}", exc_info=True)
        raise RuntimeError(f"계획 생성 실패: {str(e)}")


def generate_plan_from_challenge(challenge, user_context="", item_count=3):
    """
    챌린지 정보와 사용자 컨텍스트를 바탕으로 계획(Plan)을 생성하고 DB에 저장
    각 계획 항목을 별도의 Plan 레코드로 저장
    
    :param challenge: Challenge 객체
    :param user_context: 사용자가 제공한 추가 컨텍스트 (선택적)
    :param item_count: 생성할 계획 항목 수 (기본값: 3, 범위: 1-5)
    :return: 생성된 첫번째 Plan 객체 (호환성을 위해)
    """
    # 항목 수 제한
    item_count = max(1, min(item_count, 5))  # 1-5 사이의 값으로 제한
    
    # JSON 형식 프롬프트로 수정
    template_str = (Path(__file__).parent.parent / "templates" / "plan_from_challenge_prompt.txt").read_text(encoding="utf-8")
    prompt_template = PromptTemplate(
        input_variables=["challenge_name", "challenge_description", "user_context", "item_count"],
        template=template_str
    )

    # LLMChain 생성
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # 입력값 구성
    input_data = {
        "challenge_name": challenge.challenge_name,
        "challenge_description": challenge.description or "설명 없음",
        "user_context": user_context or "추가 컨텍스트 없음",
        "item_count": item_count,
    }

    # LLM 실행 + Plan 저장
    try:
        callbacks = [langfuse_handler] if langfuse_handler else []
        response = chain.invoke(input_data, config={"callbacks": callbacks})
        
        # 응답 처리
        if isinstance(response, dict) and "text" in response:
            response_str = str(response["text"]).strip()
        else:
            response_str = str(response).strip()
            
        logger.info(f"Generated Plan: {response_str[:200]}...")
        
        # 응답을 JSON으로 파싱
        plan_items = parse_llm_response(response_str)
        
        # 사용자 설정 (USER 타입 챌린지인 경우에만)
        user = None
        if challenge.owner_type == 'USER':
            user = challenge.user
        
        # 반환할 계획 목록
        plans = []
        
        # 각 계획 항목을 별도의 Plan 레코드로 저장
        for _, plan_text in plan_items.items():
            plan = Plan.objects.create(
                plan_text=plan_text,
                user=user,
                challenge=challenge
            )
            plans.append(plan)
            
        logger.info(f"총 {len(plans)}개의 계획 항목이 생성되었습니다. (챌린지: {challenge.id})")
        
        return plans
        
    except Exception as e:
        logger.error(f"계획 생성 오류: {str(e)}", exc_info=True)
        raise RuntimeError(f"계획 생성 실패: {str(e)}")
