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
import math

from collections import Counter
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
    

# 새로운 코사인 유사도 계산 함수
def get_cosine_similarity(text1: str, text2: str) -> float:
    """두 텍스트 간의 코사인 유사도를 계산합니다 (Bag-of-Words 기반)."""
    
    # 텍스트를 단어 빈도 벡터로 변환하는 내부 헬퍼 함수
    def text_to_vector(text: str) -> Counter:
        words = re.findall(r'\w+', text.lower()) # 간단한 토큰화 (알파벳, 숫자만)
        return Counter(words)

    vec1 = text_to_vector(text1)
    vec2 = text_to_vector(text2)

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def match_meaning_units_to_kpi(kpi: Kpi, units: List[Dict[str, Any]], threshold: float = 0.3) -> List[Dict[str, Any]]:
    """
    KPI의 이름 및 정의와 의미 단위의 키워드 간의 코사인 유사도를 기반으로 매칭합니다.
    """
    matched_units_list = []
    
    # KPI에서 비교할 텍스트 목록 (이름, 정의)
    kpi_comparison_texts = []
    if isinstance(kpi.name, str) and kpi.name.strip():
        kpi_comparison_texts.append(kpi.name)
    # kpi 객체에 definition 속성이 있고, 문자열이며, 비어있지 않은 경우에만 추가
    if hasattr(kpi, 'definition') and isinstance(kpi.definition, str) and kpi.definition.strip():
        kpi_comparison_texts.append(kpi.definition)

    if not kpi_comparison_texts: # KPI 이름이나 정의가 없으면 매칭할 대상이 없음
        return []
            
    for unit in units:
        unit_keyword = unit.get("keyword", "")
        # 의미 단위의 키워드가 문자열이고 비어있지 않은 경우에만 처리
        if not isinstance(unit_keyword, str) or not unit_keyword.strip():
            continue
            
        for kpi_text in kpi_comparison_texts:
            similarity_score = get_cosine_similarity(unit_keyword, kpi_text)
            
            if similarity_score >= threshold:
                matched_units_list.append(unit)
                # 이 의미 단위는 현재 KPI와 매칭되었으므로, 다음 의미 단위로 넘어감
                break 
                
    return matched_units_list



def score_matched_units(units: List[Dict[str, Any]]) -> float:
    """
    매핑된 의미 단위들을 기반으로 KPI 스코어 계산 (개선된 범용 로직)
    """
    if not units:
        return 30  # 매칭된 단위가 없으면 30점

    unit_scores = []

    positive_keywords = ["완료", "달성", "성공", "충분히", "잘함", "잘 했음", "개선", "늘었", "100%", "성장", "해냄", "만족", "좋았","완수됨", "이루어짐", "성취", 
                         "만점", "탁월함", "훌륭함", "우수함", "뛰어남", "빛남", "완벽함", "자부심", "기대이상", "감사함", "즐거움", "행복함", "뿌듯함", "자신감", 
                         "안정감", "열정적", "노력함", "성장함", "발전함", "향상됨", "진전", "원활함", "순조로움", "원숙함", "조화로움", "효율적", "생산적", "적극적", 
                         "의욕적", "몰입", "집중", "완성", "기여함", "지원됨", "발휘됨", "권장", "축하", "추천", "강화됨", "강력함", "명확함", "이해도증가", 
                         "통과", "합격", "통달", "해소됨", "보완됨"]
    negative_keywords = ["못했다", "못 했음", "실패", "부족", "미흡", "문제", "어려움", "0%", "힘들었", "안 함", "놓침", "불만족", "아쉽"]

    for unit in units:
        value_str = str(unit.get("value", "")).lower()
        keyword_str = str(unit.get("keyword", "")).lower()
        category_str = str(unit.get("category", "")).lower()
        
        base_score = 50  # 각 단위의 기본 점수는 50 (중립)

        # 1. 긍정/부정 키워드 확인 (value와 keyword 모두에서)
        combined_text = value_str + " " + keyword_str
        
        has_positive = any(p_kw in combined_text for p_kw in positive_keywords)
        has_negative = any(n_kw in combined_text for n_kw in negative_keywords)

        if has_positive and not has_negative:
            base_score += 35 # 긍정적 표현이 있으면 점수 상승폭 약간 더
        elif has_negative and not has_positive:
            base_score -= 35 # 부정적 표현이 있으면 점수 하락폭 약간 더
        elif has_positive and has_negative: # 긍정, 부정 혼재 시 중립에 가깝게 (약간 긍정)
            base_score += 15
        # 둘 다 없으면 base_score (50) 유지


        # 2. 수치 데이터 처리 (시간, 횟수 등)
        # 시간 처리 (예: "3시간", "2 hours")
        # 정규식에서 소수점도 인식하도록 수정: (\d+(\.\d+)?)
        time_match = re.search(r'(\d+(?:\.\d+)?)\s*(시간|hour|hr)', value_str)
        if time_match:
            hours = float(time_match.group(1))
            # 3시간 이상 활동 시 만점에 가깝게 (40점 추가), 그 이하는 비례적으로
            # KPI의 성격에 따라 기준 시간(여기서는 30)은 조절 필요
            time_score_adjustment = (hours / 30) * 40 
            base_score += min(time_score_adjustment, 40) # 최대 40점까지만 반영
        
        # 횟수 처리 (예: "3회", "5 times", "세 번")
        count_match = re.search(r'(\d+)\s*(회|번|times|count|개)', value_str)
        if count_match:
            count = int(count_match.group(1))
            # KPI 성격에 따라 횟수에 대한 점수 부여 방식은 매우 달라질 수 있음
            if count >= 5: # 5회 이상이면 높은 가산점
                base_score += 20
            elif count >= 3: # 3-4회면 가산점
                base_score += 10
            elif count == 1: # 1회면 KPI에 따라 감점 또는 낮은 점수
                base_score -= 10 
            # 0회는 negative_keywords에서 "안 함" 등으로 처리되거나, units에 포함되지 않을 수 있음

        # 퍼센트 처리 (예: "80%", "달성률 50퍼센트")
        percent_match = re.search(r'(\d+)\s*(%|퍼센트|프로)', value_str)
        if percent_match:
            percent_val = int(percent_match.group(1))
            # 100%는 positive_keywords 에서도 처리될 수 있지만, 여기서 직접 점수화
            percent_score_adjustment = (percent_val / 100.0) * 5 # 100% 달성 시 5점 추가 기여
            base_score += percent_score_adjustment


        # 3. 특정 카테고리 또는 키워드에 따른 가중치 (선택적 확장)
        if category_str == "성과" and has_positive:
            base_score += 10 # 긍정적 성과는 추가점
        if category_str == "문제": # '문제' 카테고리 자체로 약간 감점
            base_score -= 10
            if has_negative: # 문제가 부정적 키워드와 함께면 더 감점
                 base_score -= 10


        # 점수는   0 에서 100 사이로 제한
        unit_scores.append(max(0, min(100, base_score)))

    # 모든 단위 점수의 평균 계산
    if not unit_scores: # 이 경우는 거의 없지만, 방어 코드
        return 30 

    final_score = sum(unit_scores) / len(unit_scores)
    return round(final_score, 2)

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


def build_improvement_evaluator(llm) -> LLMChain:
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
    return LLMChain(prompt=prompt, llm=llm)


def evaluate_improvement_with_llm(prev_text: str, curr_text: str, kpi_name: str, chain: LLMChain) -> float:
    try:
        result = chain.run(prev=prev_text, curr=curr_text, kpi_name=kpi_name).strip().upper()
        if result == "IMPROVED":
            return 10
        elif result == "SAME":
            return 0
        elif result == "WORSENED":
            return -10
        else:
            return 0
    except Exception as e:
        print(f"[evaluate_improvement_with_llm] Error: {e}")
        return 0

def compare_retrospects(prev, curr, kpi, chain):
    """전날과 오늘 회고 비교하여 KPI 개선 여부 판단"""
    return evaluate_improvement_with_llm(
        prev_text=prev.content,
        curr_text=curr.content,
        kpi_name=kpi.name,
        chain=chain
    )

def score_kpis_from_retrospect(retrospect: Retrospect, llm_chain: ChatVertexAI) -> List[KpiResult]:
    """
    회고(Retrospect) 데이터를 기반으로 KPI 점수(KpiResult)를 생성하고 저장합니다.

    Args:
        retrospect: 점수를 매길 대상이 되는 Retrospect 인스턴스
        llm_chain: 개선 여부 평가를 위한 LLM 체인 인스턴스

    Returns:
        생성된 KpiResult 객체들의 리스트
    """
    
    # 로깅: KPI 점수 생성 시작 알림
    logger.info(f"Start KPI scoring for Retrospect ID={retrospect.id}")

    # 해당 회고의 챌린지와 사용자에 연결된 KPI 목록 조회
    kpis = Kpi.objects.filter(challenge=retrospect.challenge, user=retrospect.user)
    if not kpis:
        logger.warning("No KPIs to score.")
        return []

    # 전날 회고 조회 (개선 여부 평가용)
    prev = get_previous_retrospect(retrospect)
    
    # 개선 여부 평가에 사용할 LLM 체인 생성
    improvement_chain = build_improvement_evaluator(llm)
    results = []  # 저장된 KpiResult 객체를 담을 리스트

    # 각 KPI에 대해 점수 계산 및 저장 반복
    for kpi in kpis:
        try:
            
            units = extract_meaning_units(retrospect.content) # 1) 의미 단위 추출
            matched = match_meaning_units_to_kpi(kpi, units) # 2) KPI 정의와 의미 단위 매칭 
            base_score = score_matched_units(matched) # 3) 매칭된 단위 기반 기본 점수 계산

            if prev:  
                adj = evaluate_improvement_with_llm(prev.content, retrospect.content, kpi.name, improvement_chain) # 4) 전날 회고가 있으면 개선 여부 평가하여 점수 보정
                score = min(base_score + adj, 100)
            else:
                score = base_score

            feedback = generate_feedback(kpi, matched, score) # 5) 자연어 피드백 생성 (generate_feedback 함수 사용)

            
            result = KpiResult.objects.create( 
                user=retrospect.user,
                challenge=retrospect.challenge,
                kpi=kpi,
                retrospect=retrospect,
                score=score,
                comment=feedback
            ) # 6) KpiResult 모델에 결과 저장
            results.append(result)
            
            logger.info(f"Saved KpiResult ID={result.id}, score={score:.2f}")
                        

                        
        except Exception as e:
            
            logger.error(f"Error scoring KPI '{kpi.name}': {e}") # 오류 발생 시 로그 남기고 예외 재발생하여 트랜잭션 롤백 유도
            raise

    
    logger.info(f"Completed KPI scoring: {len(results)} results.") # 완료 로그 및 결과 반환
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
    ↓ 없음 → 0 보정 점수 계산
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
        다음은 사용자의 회고 내용에서 추출된 의미 단위(행동, 성과, 문제 등)입니다. 이를 기반으로 KPI에 대한 피드백 문장을 생성해야 합니다.

        [KPI 정보]
        - 이름: {kpi_name}
        - 점수: {score} (0 ~ 100 사이의 값)

        [의미 단위 목록]
        {units}

        [문체 가이드]
        {style_hint}

        [작성 지침]
        - 의미 단위에서 드러난 행동, 수치, 감정, 키워드 등을 적극 반영합니다.
        - 점수가 낮으면 개선 제안을 포함하고, 점수가 높으면 칭찬 위주의 문장을 사용합니다.
        - 피드백은 사용자의 동기부여를 높이도록 구성합니다.
        - 반드시 "문장 형태"로 작성합니다. 제목, 목록, 해설, 주석 등은 절대 포함하지 마세요.
        - 절대 예시나 설명을 넣지 마세요. 피드백 문장 하나만 생성하세요.
        - 오직 하나의 문장 또는 두 문장 이내로 작성합니다. 줄바꿈 없이 출력하세요.

        [출력 형식]
        피드백 문장만 출력하세요. 여는 문구, 설명, 형식 지시 없이 피드백만 단독으로 생성해야 합니다.
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        response = chain.invoke({
            "kpi_name": kpi.name,
            "units": json.dumps(units, ensure_ascii=False), # units를 JSON 문자열로 변환
            "score": f"{score:.2f}",
            "style_hint": style_hint # style_hint 변수 전달
        })
        feedback_text = response.get("text", "").strip()

        # 후처리 로직: 특정 패턴 제거 (예시)
        patterns_to_remove = [
            r"^## 피드백 문장 예시:\s*",
            r"^\*\*점수 \d\.\d+:\*\*\s*",
            r"^\*\*피드백:\*\*\s*",
            r"^\s*피드백:\s*",
        ]
        for pattern in patterns_to_remove:
            feedback_text = re.sub(pattern, "", feedback_text, flags=re.IGNORECASE | re.MULTILINE).strip()
        
        # 추가적으로, 응답이 너무 길 경우 자르거나, 특정 키워드로 시작하지 않으면 기본 메시지 반환 등의 로직도 가능
        if not feedback_text: # 후처리 후 비어있으면 기본 메시지
             logger.warning(f"피드백 생성 후처리 결과 비어있음. KPI: {kpi.name}")
             return "결과를 바탕으로 다음 행동을 계획해보세요!"
        
        return feedback_text
    
    except Exception as e:
        logger.warning(f"피드백 생성 실패 (KPI: {kpi.name}): {e}")
        return "좋은 시도였어요! 다음에도 도전해보세요." # 기본 피드백 메시지 유지 또는 변경
