import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from retrospect.models import Plan, Challenge, Kpi, KpiDataType, KpiResult
from ai_manager.serializers import KpiOutputSerializer
import os
import re
import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import dotenv

dotenv.load_dotenv()

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

def extract_meaning_units(text: str) -> List[Dict[str, Any]]:
    """
    회고 텍스트에서 행동/성과/문제 등 의미 단위 추출 (LLM 사용)
    예: [{"category": "행동", "keyword": "공부", "value": "3시간"}, {"category": "성과", "keyword": "몰입", "value": "낮음"}]
    """
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        다음은 사용자의 회고 텍스트입니다. 이 텍스트에서 의미 있는 단위(행동, 성과, 문제, 시간 등)를 JSON 리스트로 추출하세요.

        [예시]
        입력: "3시간 공부했지만 집중력이 떨어졌다"
        출력: [
        {{ "category": "행동", "keyword": "공부", "value": "3시간" }},
        {{ "category": "성과", "keyword": "집중력", "value": "낮음" }}
        ]

        회고 텍스트:
        {text}

        JSON 출력만 하세요.
        """
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        response = chain.invoke({"text": text})
        match = re.search(r'\[.*?\]', response.get("text", ""), re.DOTALL)
        return json.loads(match.group(0)) if match else []
    except Exception as e:
        logger.warning(f"의미 단위 추출 실패: {e}")
        return []

def match_meaning_units_to_kpi(kpi: Kpi, units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    KPI와 의미 단위를 매핑 (직접/간접/의미 기반)
    """
    # 유사도 계산 .... 
    matched = []
    kpi_keywords = [kpi.name, kpi.definition]
    for unit in units:
        for kw in kpi_keywords:
            if unit["keyword"] in kw:
                matched.append(unit)
                
    return matched


def score_matched_units(units: List[Dict[str, Any]]) -> float:
    """
    매핑된 의미 단위들을 기반으로 KPI 스코어 계산
    - 간단히 키워드 기준 점수 부여 또는 정규화
    """
    scores = []
    for unit in units:
        val = unit["value"]
        if "완료" in val or "100%" in val:
            scores.append(1.0)
        elif "절반" in val or "50%" in val:
            scores.append(0.5)
        elif re.match(r'\d+\s*시간', val):
            hours = float(re.search(r'\d+', val).group(0))
            scores.append(min(hours / 5.0, 1.0))  # 5시간 이상이면 1.0
        elif "못했다" in val or "실패" in val:
            scores.append(0.0)
        else:
            scores.append(0.5)
    return sum(scores) / len(scores) if scores else 0.0

def score_kpi_using_meaning_units(kpi: Kpi, retrospect_text: str) -> float:
    units = extract_meaning_units(retrospect_text)
    matched_units = match_meaning_units_to_kpi(kpi, units)
    score = score_matched_units(matched_units)
    return score, matched_units

def score_kpis_from_retrospect(retrospect):
    challenge = retrospect.challenge
    user = retrospect.user
    retrospect_text = retrospect.content

    kpis = Kpi.objects.filter(challenge=challenge, user=user)

    results = []

    for kpi in kpis:
        score, matched_units = score_kpi_using_meaning_units(kpi, retrospect_text)
        feedback = generate_feedback(kpi, matched_units, score)

        result = KpiResult.objects.create(
            user=user,
            challenge=challenge,
            kpi=kpi,
            retrospect=retrospect,
            score=score,
            comment=feedback
        )
        results.append(result)

    return results

## 카테고리 만들어서 프롬프트에 가이드로 추가
## 더 자세하게 추가하면 좋을것같기도 하고.... 
def determine_kpi_category(kpi: Kpi) -> str:
    """KPI 이름과 설명을 기반으로 KPI 카테고리 결정"""
    text = f"{kpi.name} {kpi.definition}".lower()

    if any(keyword in text for keyword in ["달리기", "운동", "피트니스", "러닝", "걷기"]):
        return "운동"
    elif any(keyword in text for keyword in ["공부", "학습", "독서", "리서치"]):
        return "학습"
    elif any(keyword in text for keyword in ["식단", "영양", "섭취", "식사"]):
        return "식습관"
    elif any(keyword in text for keyword in ["수면", "잠", "취침"]):
        return "수면"
    else:
        return "기타"


def get_style_hint(category: str) -> str:
    # KPI 카테고리에 따른 문체 가이드 반환
    if category == "운동":
        return "활동적이고 동기부여 되는 문장으로"
    elif category == "학습":
        return "친절하고 격려하는 문장으로"
    elif category == "식습관":
        return "습관 개선을 부드럽게 권유하는 문장으로"
    elif category == "수면":
        return "편안하고 건강을 강조하는 문장으로"
    else:
        return "일반적인 코칭 스타일로"   
    
def generate_feedback(kpi: Kpi, units: List[Dict[str, Any]], score: float) -> str:
    """
    KPI와 의미 단위, 스코어를 기반으로 자연어 피드백 생성
    """
    category = determine_kpi_category(kpi)
    style_hint = get_style_hint(category)
        
    prompt = PromptTemplate(
        input_variables=["kpi_name", "units", "score"],
        template="""
        KPI 이름: {kpi_name}
        의미 단위: {units}
        점수: {score}
        문체 가이드: {style_hint}

        위 정보를 바탕으로 사용자의 행동을 칭찬하거나, 개선하거나, 격려하는 자연어 피드백 문장을 작성하세요.
        - 가능하면 구체적인 행동과 수치를 반영하세요.
        - 점수가 낮으면 개선 제안을 포함하세요.
        - 점수가 높으면 칭찬 위주의 문장을 작성하세요.

        한 문장 내외로 작성하세요.
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        response = chain.invoke({
            "kpi_name": kpi.name,
            "units": json.dumps(units, ensure_ascii=False),
            "score": f"{score:.2f}",
            "style_hint": style_hint
        })
        return response.get("text", "").strip()
    
    except Exception as e:
        logger.warning(f"피드백 생성 실패: {e}")
        return "좋은 시도였어요! 다음에도 도전해보세요."


