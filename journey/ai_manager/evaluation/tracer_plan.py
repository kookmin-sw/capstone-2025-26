from langchain.prompts import PromptTemplate
from langchain_google_vertexai.chat_models import ChatVertexAI
import os
from dotenv import load_dotenv
import json
from langfuse.callback import CallbackHandler
from pathlib import Path


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

template_str = (Path(__file__).parent.parent / "templates" / "plan_from_challenge_prompt.txt").read_text()
prompt_template = PromptTemplate(
    input_variables=["challenge_name", "challenge_description", "user_context", "item_count"],
    template=template_str
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