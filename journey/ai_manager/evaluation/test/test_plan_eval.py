import deepeval
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import PromptAlignmentMetric

from deepeval.models import GeminiModel
from dotenv import load_dotenv
import os
from langfuse import Langfuse
from pathlib import Path

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["DEEPEVAL_RESULTS_DIR"] = "./"
template = (Path(__file__).parent.parent.parent / "templates" / "plan_from_challenge_prompt.txt").read_text()

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