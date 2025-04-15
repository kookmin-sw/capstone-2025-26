import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
from langfuse.callback import CallbackHandler
from retrospect.models import Plan
import os

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

        위 정보를 바탕으로 사용자가 내일 수행할 수 있는 간단하고 실천 가능한 계획을 2~3가지 JSON 형식으로 추천해주세요.

        예시:
        {{
          "1": "하루 15분간 집중 회고 작성",
          "2": "하루 중 가장 만족스러웠던 순간 정리"
        }}
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
        plan_json = json.loads(str(response))  # 문자열로 들어올 경우를 대비해 json 파싱

        plan = Plan.objects.create(plan_list=plan_json)
        return plan

    except Exception as e:
        raise RuntimeError(f"계획 생성 실패: {str(e)}")
