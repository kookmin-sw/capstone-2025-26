import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from retrospect.models import Plan, Challenge, Kpi, KpiDataType
from ai_manager.serializers import KpiOutputSerializer
import os
import re
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# LangChain LLM 설정
llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    model_name="gemini-2.0-flash-lite-001",
    max_output_tokens=1024,
    temperature=0.7,
)

# Langfuse 핸들러 초기화
langfuse_handler = None
try:
    langfuse_handler = CallbackHandler(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
except Exception as e:
    logger.warning(f"Langfuse 핸들러 초기화 오류: {str(e)}. 토큰 사용량 추적이 비활성화됩니다.")


def parse_llm_response(response_text: str) -> List[Dict[str, Any]]:
    """LLM 응답을 파싱하여 KPI 데이터 리스트를 반환하는 유틸리티 함수"""
    logger.info(f"Parsing LLM response: {response_text[:200]}...")
    
    # 1. 직접 JSON 파싱 시도
    try:
        kpi_data_list = json.loads(response_text)
        if isinstance(kpi_data_list, list):
            return kpi_data_list
    except json.JSONDecodeError:
        pass  # 다음 방법으로 넘어감
    
    # 2. 정규 표현식으로 JSON 추출 시도
    match = re.search(r'\[\s*\{.*?\}\s*\]', response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass  # 파싱 실패
    
    # 모든 파싱 방법 실패
    raise ValueError("LLM 응답에서 유효한 KPI 데이터를 추출할 수 없습니다.")


def validate_kpi_data(kpi_data: Dict[str, Any]) -> bool:
    """KPI 데이터의 유효성을 검사하는 함수"""
    # 필수 키 검사
    required_keys = {"name", "definition", "measurement_unit", "data_type"}
    if not required_keys.issubset(kpi_data.keys()):
        logger.warning(f"유효하지 않은 KPI 데이터: 필수 필드 누락 - {kpi_data}")
        return False
    
    # data_type 유효성 검사
    llm_data_type = kpi_data.get("data_type", "").upper()
    if llm_data_type not in KpiDataType.values:
        logger.warning(f"유효하지 않은 KPI 데이터: 잘못된 data_type '{llm_data_type}' - {kpi_data}")
        return False
    
    return True


def get_plans_data(plan_ids: List[int]) -> List[Dict[str, Any]]:
    """
    여러 계획 ID를 받아 해당하는 계획 데이터 목록을 반환하는 함수
    
    :param plan_ids: 계획 ID 목록
    :return: 계획 데이터 목록 (각 계획 번호와 내용을 포함)
    """
    plans_data = []
    for i, plan_id in enumerate(plan_ids, 1):
        try:
            plan = Plan.objects.get(id=plan_id)
            plans_data.append({
                "number": i,
                "id": plan_id,
                "text": plan.plan_text
            })
        except Plan.DoesNotExist:
            logger.warning(f"Plan ID {plan_id}에 해당하는 계획을 찾을 수 없습니다.")
    
    return plans_data


def generate_kpis_for_challenge(challenge: Challenge, plan_ids: List[int], user_context: str, user, item_count: int = 3):
    """
    Generates KPIs for a given challenge, plans, and context using an LLM,
    parses the response, and saves them to the database.

    :param challenge: The Challenge object.
    :param plan_ids: List of Plan IDs associated with the challenge.
    :param user_context: Optional additional context from the user.
    :param user: The user requesting the KPI generation.
    :param item_count: Number of KPIs to generate.
    :return: A list of created Kpi objects.
    """
    # Langfuse 트레이스 생성
    trace_id = f"kpi_gen_{challenge.id}_{user.id}_{str(os.urandom(4).hex())}"
    callbacks = []
    if langfuse_handler:
        langfuse_handler.langfuse.trace(
            name="generate_kpis",
            id=trace_id,
            tags=["kpi_generation"],
            metadata={"challenge_id": challenge.id, "user_id": user.id}
        )
        callbacks = [langfuse_handler]
    
    # 계획 데이터 조회
    plans_data = get_plans_data(plan_ids)
    if not plans_data:
        raise ValueError("유효한 계획 데이터가 없습니다. 적어도 하나의 계획이 필요합니다.")
    
    prompt_template = PromptTemplate(
        input_variables=["challenge_name", "challenge_description", "plans", "user_context", "item_count"],
        template="""
        당신은 사용자의 챌린지에 대한 핵심성과지표(KPI)를 정의하는 AI 어시스턴트입니다.
        제공된 챌린지 세부정보, 계획 목록, 사용자 컨텍스트를 바탕으로, 정확히 {item_count}개의 관련 KPI를 생성하세요.

        **챌린지 정보:**
        이름: {challenge_name}
        설명: {challenge_description}

        **사용자의 계획 목록:**
        {plans}

        **추가 사용자 컨텍스트:**
        {user_context}

       **지시사항:**
        1. 챌린지 목표, 계획 목록, 컨텍스트를 분석하세요.
        2. 정확히 {item_count}개의 구체적이고, 측정 가능하며, 달성 가능하고, 관련성 있으며, 시간 제한이 있는(SMART) KPI를 정의하세요.
        3. 각 KPI에 대해 다음 정보를 제공하세요:
            * `name`: KPI의 간결한 이름 (예: "일일 학습 시간", "문제 풀이 정확도").
            * `definition`: KPI가 측정하는 대상에 대한 간략한 설명.
            * `measurement_unit`: 측정 단위 (예: "시간", "퍼센트", "개수", "점수", "참/거짓"). 완료 여부는 "참/거짓"을 사용하세요.
            * `data_type`: 기록될 값의 데이터 유형. 다음 중 하나를 선택: {data_type_options}.
        4. 출력은 반드시 JSON 리스트 형식이어야 합니다. JSON 리스트 외부에는 어떠한 텍스트도 포함하지 마세요(설명, 인사말 등 제외).
        5. 모든 내용은 한국어로 작성하세요.

        **출력 형식 예시:**
        [
          {{
            "name": "개념 원리 챕터 점수 ",
            "definition": "'개념 원리' 챕터 끝 퀴즈에서 달성한 점수",
            "measurement_unit": "점수",
            "data_type": "INTEGER"
          }},
          {{
            "name": "일일 문제 풀이 수수",
            "definition": "매일 푼 '쎈' 문제 수.",
            "measurement_unit": "개수",
            "data_type": "INTEGER"
          }},
          {{
            "name": "야간 자율 학습 참석석",
            "definition": "저녁 자습('야자')에 참석했는지 여부.",
            "measurement_unit": "boolean",
            "data_type": "BOOLEAN"
          }}
        ]

        **Constraint:** The output MUST be only the JSON list.
        """
    )

    # 입력 데이터 준비
    plans_formatted = []
    for plan in plans_data:
        plans_formatted.append(f"계획 {plan['number']}: {plan['text']}")
    
    plans_str = "\n".join(plans_formatted)
    data_type_options = ", ".join([dt[0] for dt in KpiDataType.choices])
    input_data = {
        "challenge_name": challenge.challenge_name,
        "challenge_description": challenge.description,
        "plans": plans_str,
        "user_context": user_context or "None provided.",
        "data_type_options": data_type_options,
        "item_count": item_count,
    }

    # LLM 체인 생성 및 실행
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    try:
        # LLM 호출 및 응답 처리
        response = chain.invoke(input_data, config={"callbacks": callbacks})
        response_text = response.get("text", str(response)).strip()
        logger.info(f"KPI 생성을 위한 LLM 응답 수신: {len(response_text)} 자")
        
        if langfuse_handler:
            langfuse_handler.langfuse.span(
                trace_id=trace_id,
                name="llm_response_received",
                metadata={"response_length": len(response_text)}
            )
        
        # 응답 파싱
        kpi_data_list = parse_llm_response(response_text)
        
        # KPI 생성
        created_kpis = []
        for kpi_data in kpi_data_list:
            # KPI 데이터 유효성 검사
            if not validate_kpi_data(kpi_data):
                continue
            
            # 대문자로 통일
            llm_data_type = kpi_data.get("data_type", "").upper()
                
            # DB에 KPI 생성 또는 업데이트
            try:
                kpi_instance, created = Kpi.objects.update_or_create(
                    challenge=challenge,
                    user=user,
                    name=kpi_data["name"],
                    defaults={
                        'definition': kpi_data.get("definition", ""),
                        'measurement_unit': kpi_data.get("measurement_unit", ""),
                        'data_type': llm_data_type,
                        'measurement_method': kpi_data.get("measurement_method", "")
                    }
                )
                created_kpis.append(kpi_instance)
                
                # Langfuse에 생성된 KPI 기록
                if langfuse_handler:
                    status = "created" if created else "updated"
                    langfuse_handler.langfuse.event(
                        trace_id=trace_id, 
                        name=f"kpi_{status}",
                        metadata={
                            "kpi_id": kpi_instance.id,
                            "kpi_name": kpi_instance.name,
                            "data_type": kpi_instance.data_type
                        }
                    )
                
                logger.info(f"KPI {'생성' if created else '업데이트'}: {kpi_instance.name} (사용자 {user.id}, 챌린지 {challenge.id})")
            except Exception as db_err:
                logger.error(f"KPI '{kpi_data.get('name')}' 저장 실패: {db_err}")
                if langfuse_handler:
                    langfuse_handler.langfuse.event(
                        trace_id=trace_id,
                        name="kpi_save_error",
                        metadata={"error": str(db_err), "kpi_name": kpi_data.get("name", "")}
                    )

        # 결과 검증 및 반환
        if not created_kpis:
            error_msg = "KPI 생성 실패: 유효한 KPI 데이터를 생성하지 못했습니다."
            logger.error(error_msg)
            if langfuse_handler:
                langfuse_handler.langfuse.event(trace_id=trace_id, name="kpi_gen_failed", 
                                              metadata={"reason": "no_valid_kpis"})
            raise RuntimeError(error_msg)
        
        # 성공 로깅
        if langfuse_handler:
            langfuse_handler.langfuse.event(
                trace_id=trace_id, 
                name="kpi_gen_success",
                metadata={"kpi_count": len(created_kpis)}
            )
        
        return created_kpis

    except Exception as e:
        error_msg = f"KPI 생성 중 오류 발생: {e}"
        logger.error(error_msg)
        
        # Langfuse에 오류 기록
        if langfuse_handler:
            langfuse_handler.langfuse.event(
                trace_id=trace_id,
                name="kpi_gen_error",
                metadata={"error": str(e)}
            )
        
        # 원래 예외를 유지하면서 사용자 친화적 메시지 제공
        raise RuntimeError(f"KPI 생성 실패: {e}")
