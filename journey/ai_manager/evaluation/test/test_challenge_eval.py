import deepeval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import PromptAlignmentMetric

import pytest
from deepeval.models import GeminiModel
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

template = (Path(__file__).parent.parent.parent / "templates" / "synthesize_challenge_prompt.txt").read_text()

dataset = EvaluationDataset()

model = GeminiModel(
    model_name="gemini-2.5-flash-preview-04-17",
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    temperature=0
)


dataset.add_test_cases_from_json_file(
    file_path=str(Path(__file__).parent.parent / "synthesizer" / "challenges.json"),
    input_key_name="input",
    actual_output_key_name="output",
)

@pytest.mark.parametrize(
    "test_case",
    dataset,
)
def test_challenge_synthesizer(test_case: LLMTestCase):
    prompt_alignment_metric = PromptAlignmentMetric(
        prompt_instructions=template,
        model=model,
        include_reason=True,
    )
    assert_test(test_case, [prompt_alignment_metric])

@deepeval.on_test_run_end
def function_to_be_called_after_test_run():
    print("Test finished!")