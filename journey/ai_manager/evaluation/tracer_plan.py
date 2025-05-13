from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
import os
from dotenv import load_dotenv
import json
from langfuse.callback import CallbackHandler


load_dotenv()
os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

langfuse_handler = CallbackHandler()


llm = ChatVertexAI(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    model_name="gemini-2.5-flash-preview-04-17",
    max_output_tokens=65535,
    temperature=0.7,
)

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
    
    반드시 아래와 같은 JSON 형식으로 출력해주세요. 키는 계획 번호(숫자), 값은 간결하고 구체적인 계획 내용이어야 합니다.
    
    예시:
    {{
        "1": "매일 아침 6시에 기상하여 30분간 개념 복습하기",
        "2": "방과 후 2시간 동안 '쎈' 교재 문제 풀이 집중하기",  
        "3": "일주일에 3회, 1시간씩 오답노트 정리 및 복습하기"
    }}
    
    출력은 반드시 위와 같은 JSON 형식이어야 합니다. JSON 외의 추가 텍스트는 포함하지 마세요.
    """
)

def trace_plan():
    pipeline = prompt_template | llm
    
    # Load challenges from JSON file
    try:
        with open('ai_manager/evaluation/challenges.json', 'r', encoding='utf-8') as f:
            challenges = json.load(f)
    except FileNotFoundError:
        print("Error: challenges.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode challenges.json.")
        return

    # Iterate through each challenge and invoke the pipeline
    for i, challenge_item in enumerate(challenges):
        try:
            # Parse the 'output' field which is a JSON string
            challenge_data = json.loads(challenge_item['output'])
            
            challenge_name = challenge_data.get("challenge_name", "N/A")
            challenge_description = challenge_data.get("challenge_description", "N/A")
            user_context = ""  # Set user_context to empty string
            item_count = 3      # Keep item_count as 3

            # Create a unique trace/span for each challenge if needed, or just invoke
            # For simplicity, invoking directly here. Consider creating spans if needed.
            print(f"--- Processing Challenge {i+1} ---")
            print(f"Name: {challenge_name}")
            print(f"Description: {challenge_description}")

            response = pipeline.invoke({
                "challenge_name": challenge_name,
                "challenge_description": challenge_description,
                "user_context": user_context,
                "item_count": item_count
            }, config={"callbacks": [langfuse_handler], "tags": [f"plan_trace_eval"]})
            response_text = response.content
            print("Raw response:")
            print(response_text)
            print("-" * 20) # Separator for readability

        except json.JSONDecodeError:
            print(f"Error: Could not decode 'output' field for challenge {i+1}.")
            continue
        except KeyError as e:
            print(f"Error: Missing key {e} in challenge data for challenge {i+1}.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred for challenge {i+1}: {e}")
            continue


if __name__ == "__main__":
    trace_plan()