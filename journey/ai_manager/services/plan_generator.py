import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from retrospect.models import Plan
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

# Langfuse 핸들러
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)


def generate_plan_from_retrospect(challenge, retrospect):
    """
    회고 내용을 바탕으로 다음날 계획(Plan)을 생성하고 DB에 저장
    """
    # 프롬프트
    prompt_template = PromptTemplate(
    input_variables=["challenge_name", "kpi", "retrospect_content"],
    template="""
        아래는 사용자의 회고 챌린지 정보입니다.

        [챌린지명]
        {challenge_name}

        [KPI 기준]
        {kpi}

        [최근 회고 내용]
        {retrospect_content}

        위 정보를 기반으로, 사용자가 내일 실천할 수 있는 **간단하고 구체적인 행동 계획**을 2~3개 작성해주세요.

        **다음 조건을 반드시 지켜야 합니다:**
        1. 출력은 무조건 JSON 형식의 오브젝트여야 합니다.
        2. JSON 외 텍스트(설명, 인사말, 라벨 등)는 절대 포함하지 마세요.
        3. 키는 "1", "2", "3" 형태로 작성하고, 값은 행동 계획을 문자열로 작성하세요.

        **형식 예시:**
        {{
            "1": "아침에 10분간 KPI 점검하기",
            "2": "퇴근 후 오늘의 회고 작성",
            "3": "회고한 내용을 메모 앱에 기록"
        }}

        **주의:** JSON 외의 출력이 발생하면 시스템에서 에러로 간주됩니다.  
        """
    )


    # 🔹 2. LLMChain 생성
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # 🔹 3. 입력값 구성
    input_data = {
        "challenge_name": challenge.challenge_name,
        "kpi": json.dumps(challenge.kpi_metrics, ensure_ascii=False),
        "retrospect_content": retrospect.content,
    }

    # 🔹 4. LLM 실행 + Plan 저장
    try:
        response = chain.invoke(input_data, config={"callbacks": [langfuse_handler]})
        response_str = str(response).strip()
        print(f"Generated Plan: {response}")

        # 응답이 dict 형태이고 "text" 키가 있다면 해당 값을 사용
        if isinstance(response, dict) and "text" in response:
            response_str = str(response["text"]).strip()
        else:
            response_str = str(response).strip()

        print("Response String for Parsing:", response_str)
        
        if response_str.startswith("```json"):
            lines = response_str.splitlines()
            # ```로 시작하는 줄은 모두 제거
            cleaned_lines = [line for line in lines if not line.strip().startswith("```")]
            cleaned_response = "\n".join(cleaned_lines).strip()
        else:
            cleaned_response = response_str
        
        print("Cleaned Response:", cleaned_response)

        # 정규표현식으로 JSON 객체 추출 (전체 응답이 JSON 객체라면 match가 전체 문자열)
        match = re.search(r'\{(?:.|\n)*\}', cleaned_response, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = cleaned_response  # 매칭 실패 시 전체 문자열 사용
        
        print("Extracted JSON String:", json_str)

        plan_json = json.loads(json_str)
        print("Parsed Plan JSON:", plan_json)
        plan = Plan.objects.create(plan_list=plan_json)
        
        return plan

    except Exception as e:
        raise RuntimeError(f"계획 생성 실패: {str(e)}")
