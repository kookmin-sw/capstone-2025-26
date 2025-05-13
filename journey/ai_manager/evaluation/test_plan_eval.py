import deepeval
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import PromptAlignmentMetric

from deepeval.models import GeminiModel
from dotenv import load_dotenv
import os
from langfuse import Langfuse

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["DEEPEVAL_RESULTS_DIR"] = "./"
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

model = GeminiModel(
    model_name="gemini-2.5-flash-preview-04-17",
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    temperature=0
)

langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

def load_test_cases_from_langfuse():
    dataset = EvaluationDataset()
    traces_data = langfuse.fetch_traces(page=1,
                                        tags="plan_trace_eval",
                                        limit=100
                                    ).data
    print("traces_data length: ", len(traces_data))
    if not traces_data:
        print("No traces found in Langfuse. The evaluation dataset will be empty.")
    else:
        print(f"Fetched {len(traces_data)} traces from Langfuse. Populating dataset...")
        for i, trace in enumerate(traces_data):
            trace_id = getattr(trace, 'id', f'index_{i}')
            if (hasattr(trace, 'input') and hasattr(trace, 'output')
                and isinstance(trace.input, dict)
                and isinstance(trace.output, dict)
                and 'content' in trace.output
                and isinstance(trace.output['content'], str)):
                try:
                    formatted_input_string = template.format(**trace.input)
                except KeyError as e:
                    print(f"  Skipping trace {trace_id} due to missing key in input for template formatting: {e}")
                    continue

                llm_test_case = LLMTestCase(
                    input=formatted_input_string,
                    actual_output=trace.output['content']
                )
                llm_test_case.metadata = {"trace_id": trace_id}
                dataset.add_test_case(llm_test_case)
            else:
                print(f"  Skipping trace {trace_id} due to missing or malformed input/output.")
    print(f"Dataset populated with {len(dataset)} test cases from Langfuse traces.")
    return dataset

def run_evaluation():
    dataset = load_test_cases_from_langfuse()
    print(f"Loaded {len(dataset)} test cases.")

    for test_case in dataset:
        trace_id = test_case.metadata.get("trace_id")
        print(f"Evaluating trace {trace_id}...")

        prompt_alignment_metric = PromptAlignmentMetric(
            prompt_instructions=template,
            model=model,
            include_reason=True,
        )
        prompt_alignment_metric.measure(test_case)

        score = prompt_alignment_metric.score
        reason = getattr(prompt_alignment_metric, 'reason', None)
        if score is None:
            print(f"Warning: PromptAlignmentMetric.score is None for trace {trace_id}, skipping Langfuse scoring.")
            continue

        comment = reason or ""
        try:
            langfuse.score(
                trace_id=trace_id,
                name="PromptAlignmentScore",
                value=score,
                comment=comment
            )
            print(f"Score {score} for trace {trace_id} sent to Langfuse.")
        except Exception as e:
            print(f"Error sending score to Langfuse for trace {trace_id}: {e}")

    function_to_be_called_after_test_run()

@deepeval.on_test_run_end
def function_to_be_called_after_test_run():
    print("Test finished!")

if __name__ == "__main__":
    run_evaluation()