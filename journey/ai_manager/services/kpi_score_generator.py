import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from retrospect.models import Plan, Challenge, Kpi, KpiDataType, KpiResult, Retrospect
from ai_manager.serializers import KpiOutputSerializer
import os
import re
import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import difflib
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

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

def is_similar(keyword1, keyword2, threshold=0.5):
    ratio = difflib.SequenceMatcher(None, keyword1, keyword2).ratio()
    return ratio >= threshold

def extract_meaning_units(text: str) -> List[Dict[str, Any]]:
    """
    회고 텍스트에서 행동/성과/문제 등 의미 단위 추출 (LLM 사용)
    예: [{"category": "행동", "keyword": "공부", "value": "3시간"}, {"category": "성과", "keyword": "몰입", "value": "낮음"}]
    """
    template_str = (Path(__file__).parent.parent / "templates" / "extract_meaning_units_prompt.txt").read_text()
    prompt = PromptTemplate(
        input_variables=["text"],
        template=template_str
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
    matched = []
    kpi_keywords = [kpi.name, kpi.definition]

    for unit in units:
        for kw in kpi_keywords:
            if is_similar(unit["keyword"], kw):
                matched.append(unit)
                break  # 중복 매칭 방지
    return matched


def score_matched_units(units: List[Dict[str, Any]]) -> float:
    """
    매핑된 의미 단위들을 기반으로 KPI 스코어 계산
    - 간단히 키워드 기준 점수 부여 또는 정규화
    """
    if not units:
        return 0.3
    
    scores = []
    for unit in units:
        val = unit["value"]
        if "완료" in val or "100%" in val:
            scores.append(1.0)
        elif "절반" in val or "50%" in val:
            scores.append(0.5)
        elif m := re.match(r"(\d+)\s*시간", val):
            hours = float(m.group(1))
            scores.append(min(hours / 5.0, 1.0))
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


# 전날 회고 조회 후 비교해서 kpi 점수 부여
def get_previous_retrospect(current_retrospect):
    previous_day = current_retrospect.created_at.date() - timedelta(days=1)
    return Retrospect.objects.filter(
        user=current_retrospect.user,
        challenge=current_retrospect.challenge,
        created_at__date=previous_day
    ).order_by('-created_at').first()


def build_improvement_evaluator(llm_instance) -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["prev", "curr", "kpi_name"],
        template=(
            "KPI 항목: {kpi_name}\n"
            "사용자의 전날 회고:\n{prev}\n\n"
            "사용자의 오늘 회고:\n{curr}\n\n"
            "이 KPI 기준으로 사용자가 개선되었는지 평가해줘. 세 가지 중 하나만 출력해:\n"
            "- IMPROVED: 명확히 더 나아짐\n"
            "- SAME: 변화 없음\n"
            "- WORSENED: 악화됨\n"
            "다른 말은 하지 말고 위 단어 중 하나만 출력해."
        )
    )
    return LLMChain(prompt=prompt, llm=llm_instance)


def evaluate_improvement_with_llm(prev_text: str, curr_text: str, kpi_name: str, chain: LLMChain) -> float:
    try:
        result = chain.run(prev=prev_text, curr=curr_text, kpi_name=kpi_name).strip().upper()
        if result == "IMPROVED":
            return 0.1
        elif result == "SAME":
            return 0.0
        elif result == "WORSENED":
            return -0.1
        else:
            return 0.0
    except Exception as e:
        print(f"[evaluate_improvement_with_llm] Error: {e}")
        return 0.0

def compare_retrospects(prev, curr, kpi, chain):
    """전날과 오늘 회고 비교하여 KPI 개선 여부 판단"""
    return evaluate_improvement_with_llm(
        prev_text=prev.content,
        curr_text=curr.content,
        kpi_name=kpi.name,
        chain=chain
    )
def score_kpis_from_retrospect(retrospect, llm):
    print(f"\n[INFO] 🔍 KPI 평가 시작 - 회고 ID: {retrospect.id}")
    
    challenge = retrospect.challenge
    user = retrospect.user
    retrospect_text = retrospect.content

    print(f"[DEBUG] 유저: {user.username}, 챌린지: {challenge.challenge_name}")
    
    # 1. 평가 대상 KPI 조회
    kpis = Kpi.objects.filter(challenge=challenge, user=user)
    print(f"[DEBUG] 평가 대상 KPI 수: {kpis.count()}개")

    if not kpis.exists():
        print(f"[WARN] 평가할 KPI가 없습니다. 회고 ID: {retrospect.id}")
        return []

    prev_retrospect = get_previous_retrospect(retrospect)
    if prev_retrospect:
        print(f"[DEBUG] 전날 회고 있음 → ID: {prev_retrospect.id}")
    else:
        print(f"[DEBUG] 전날 회고 없음")

    results = []

    for kpi in kpis:
        print(f"\n[INFO] → KPI 평가 중: {kpi.name}")

        try:
            # 기본 점수 계산
            score, matched_units = score_kpi_using_meaning_units(kpi, retrospect_text)
            print(f"[DEBUG] 기본 점수: {score}, 매칭된 의미 단위 수: {len(matched_units)}")

            # 개선 여부 판단 및 보정 점수
            if prev_retrospect is not None:
                improvement_score = compare_retrospects(prev_retrospect, retrospect, kpi, llm)
                score = min(score + improvement_score, 1.0)
                print(f"[DEBUG] 개선 점수: {improvement_score} → 최종 점수: {score}")
            else:
                print(f"[DEBUG] 개선 비교 생략 (전날 회고 없음)")

            feedback = generate_feedback(kpi, matched_units, score)

            # KPIResult 저장
            result = KpiResult.objects.create(
                user=user,
                challenge=challenge,
                kpi=kpi,
                retrospect=retrospect,
                score=score,
                comment=feedback
            )
            results.append(result)
            print(f"[SUCCESS] KPIResult 저장 완료 → ID: {result.id}, 점수: {score:.2f}")

        except Exception as e:
            print(f"[ERROR] KPI '{kpi.name}' 평가 중 오류 발생: {e}")
            continue

    print(f"\n[INFO] ✅ KPI 평가 종료 - 총 {len(results)}개 저장됨")
    return results

'''
Input: 1일치 회고 (Retrospect), LLM 인스턴스
↓
1. 관련 KPI 조회
↓
2. 의미 단위 기반 기본 점수 평가 (오늘 회고 단독 기준)
↓
3. 전날 회고 존재 여부 확인
    ↓ 있음 → LLM 기반 비교 평가 → 보정 점수 계산
    ↓ 없음 → 0.0 보정 점수 계산
↓
4. 점수 보정 및 feedback 생성
↓
5. KpiResult 저장
↓
Output: KPI 평가 결과 리스트
'''



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


