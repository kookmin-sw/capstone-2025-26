import deepeval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import PromptAlignmentMetric

import pytest
from deepeval.models import GeminiModel
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

template="""
        You are a world class Challenge Synthesizer.
        Use your knowledge to synthesize a challenge from the given information.
        You must reason step by step to synthesize the challenge.

        Every challenge should have a name, description, and KPI.
        The challenge should be SMART.
        The challenge should be achievable.
        The challenge should be measurable.
        The challenge should be relevant.        
        
        Your output must me in JSON List format.
        Your output must be in Korean.
        Your output must be in JSON List format.
        Your output must be in Korean.
        DO NOT add any other text to your output.

        Make 100 challenges in total.


        example:
        [
        {{
          "challenge_name": "8주 독서 챌린지",
          "challenge_description": "8주 동안 매주 1권씩 자기계발서 또는 교양 도서를 읽어 지식과 관점을 확장한다",
          "kpi_info": "8주 내 총 8권 독서 및 독서 노트 작성 완료",
          "retrospect_content": ""
        }}, 
        {{
          "challenge_name": "매일 5km달리기 챌린지",
          "challenge_description": "매일 오전 7시에 5km 달리기를 하고, 달리기 앱으로 기록한다",
          "kpi_info": "매일 5km 달리기 완료",
          "retrospect_content": ""
        }}, 
        {{
          "challenge_name": "8주 영어 팟케스트 청취 챌린지",
          "challenge_description": "8주동안 주 3회, 회당 15분 이상 팟캐스트를 듣고 주요 어휘 및 표현을 노트에 정리해 영어 청취 능력을 향상시킨다.",
          "kpi_info": "8주 내 총 24회 팟캐스트 청취 및 주요 어휘 및 표현 정리 완료",
          "retrospect_content": ""
        }}, 
        {{
          "challenge_name": "명상 습관 형성 챌린지",
          "challenge_description": "매일 최소 10분씩 명상 앱 또는 유튜브 가이드를 따라 마음을 진정시키고 집중력을 향상시킨다.",
          "kpi_info": "8주 내 총 24회 팟캐스트 청취 및 주요 어휘 및 표현 정리 완료",
          "retrospect_content": "하루 10분 이상 명상 완료"
        }}
        ]
    """


dataset = EvaluationDataset()

model = GeminiModel(
    model_name="gemini-2.5-pro-preview-05-06",
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    temperature=0
)


dataset.add_test_cases_from_json_file(
    file_path="ai_manager/evaluation/challenges.json",
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