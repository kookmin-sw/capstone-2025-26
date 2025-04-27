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

logger = logging.getLogger(__name__)

# LangChain LLM 설정
llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    model_name="gemini-2.0-flash-lite-001",
    max_output_tokens=1024,
    temperature=0.7,
)

# Langfuse 핸들러 - 토큰 사용량 데이터 형식 문제 해결
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


def generate_plan_from_retrospect(challenge, retrospect):
    """
    회고 내용을 바탕으로 다음날 계획(Plan)을 생성하고 DB에 저장
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
    
    # 프롬프트
    prompt_template = PromptTemplate(
    input_variables=["challenge_name", "kpi_info", "retrospect_content"],
    template="""
        아래는 사용자의 회고 챌린지 정보입니다.

        [챌린지명]
        {challenge_name}

        [KPI 기준]
        {kpi_info}

        [최근 회고 내용]
        {retrospect_content}

        위 정보를 기반으로, 사용자가 내일 실천할 수 있는 **간단하고 구체적인 행동 계획**을 2~3개 작성해주세요.
        계획은 번호를 붙여서 명확하게 작성해주세요.
        
        예시:
        1. 아침에 10분간 KPI 점검하기
        2. 퇴근 후 오늘의 회고 작성
        3. 회고한 내용을 메모 앱에 기록
    """
    )

    # 🔹 2. LLMChain 생성
    chain = LLMChain(llm=llm, prompt=prompt_template)

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
        response_str = str(response).strip()
        logger.info(f"Generated Plan: {response_str[:200]}...")

        # 응답이 dict 형태이고 "text" 키가 있다면 해당 값을 사용
        if isinstance(response, dict) and "text" in response:
            response_str = str(response["text"]).strip()
        else:
            response_str = str(response).strip()

        logger.debug("Response String for Parsing: %s", response_str[:200])
        
        # 코드 블록 제거 (있는 경우)
        if response_str.startswith("```") and response_str.endswith("```"):
            response_str = response_str[3:-3].strip()
            if response_str.startswith("json"):
                response_str = response_str[4:].strip()
        
        # 텍스트 계획으로 저장
        plan = Plan.objects.create(
            plan_text=response_str,
            user=retrospect.user,
            challenge=challenge
        )
        
        return plan

    except Exception as e:
        logger.error(f"계획 생성 실패: {str(e)}", exc_info=True)
        raise RuntimeError(f"계획 생성 실패: {str(e)}")

def generate_plan_from_challenge(challenge, user_context="", item_count=3):
    """
    챌린지 정보와 사용자 컨텍스트를 바탕으로 계획(Plan)을 생성하고 DB에 저장
    
    :param challenge: Challenge 객체
    :param user_context: 사용자가 제공한 추가 컨텍스트 (선택적)
    :param item_count: 생성할 계획 항목 수 (기본값: 3, 범위: 1-5)
    :return: 생성된 Plan 객체
    """
    # 항목 수 제한
    item_count = max(1, min(item_count, 5))  # 1-5 사이의 값으로 제한
    
    # 한글 프롬프트로 수정
    prompt_template = PromptTemplate(
        input_variables=["challenge_name", "challenge_description", "user_context", "item_count"],
        template="""
        다음은 사용자의 챌린지 정보입니다.

        [챌린지명]
        {challenge_name}

        [챌린지 설명]
        {challenge_description}

        [추가 컨텍스트]
        {user_context}

        위 정보를 바탕으로, 사용자가 챌린지를 성공적으로 달성하기 위한 구체적인 실행 계획을 정확히 {item_count}개 작성해 주세요.
        
        각 행동 계획은 구체적이고 실행 가능해야 하며, 한국어로 작성해야 합니다.
        정확히 {item_count}개의 행동 계획을 번호와 함께 제공하세요.

        예시:
        1. 매일 아침 6시에 기상하여 30분간 개념 복습하기
        2. 방과 후 2시간 동안 '쎈' 교재 문제 풀이 집중하기  
        3. 일주일에 3회, 1시간씩 오답노트 정리 및 복습하기
        """
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
        
        # 코드 블록 제거 (있는 경우)
        if response_str.startswith("```") and response_str.endswith("```"):
            response_str = response_str[3:-3].strip()
            if response_str.startswith("json"):
                response_str = response_str[4:].strip()
        
        # 텍스트 계획으로 저장
        user = None
        if challenge.owner_type == 'USER':
            user = challenge.user
            
        plan = Plan.objects.create(
            plan_text=response_str,
            user=user,
            challenge=challenge
        )
        
        return plan
        
    except Exception as e:
        logger.error(f"계획 생성 오류: {str(e)}", exc_info=True)
        raise RuntimeError(f"계획 생성 실패: {str(e)}")
