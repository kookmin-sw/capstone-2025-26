import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from retrospect.models import Plan, Kpi
import os
import re
import json

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
        
        print("Extracted JSON String:", json_str)

        plan_json = json.loads(json_str)
        print("Parsed Plan JSON:", plan_json)
        plan = Plan.objects.create(plan_list=plan_json)
        
        return plan

    except Exception as e:
        raise RuntimeError(f"계획 생성 실패: {str(e)}")
