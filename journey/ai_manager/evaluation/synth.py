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
    model_name="gemini-2.5-pro-preview-05-06",
    max_output_tokens=65535,
    temperature=0.7,
)

template_str = (Path(__file__).parent.parent / "templates" / "synthesize_challenge_prompt.txt").read_text()
synthesize_challenge_template = PromptTemplate(
    template=template_str
)


def synthesize_challenge():
    pipeline = synthesize_challenge_template | llm
    response = pipeline.invoke({}, config={"callbacks": [langfuse_handler], "tags": [f"synth_challenge"]})
    # parse JSON list and save to JSON Lines
    # Extract content from AIMessage object
    response_text = response.content
    print("Raw response:")
    print(response_text)
    
    # Try to clean response if needed - remove any non-JSON prefix/suffix
    try:
        # Find the first '[' and last ']' for JSON array
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_text = response_text[start_idx:end_idx]
            challenges = json.loads(json_text)
        else:
            # If we can't find JSON array markers, try the whole response
            challenges = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("Failed to parse challenges. Creating an empty file.")
        challenges = []
    # Construct path relative to the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'challenges.json')
    
    # Save the entire list of challenges to a single JSON file
    # Format for deepeval: a list of {"input": "", "output": "{json_string_of_challenge_data}"}
    deepeval_formatted_challenges = [
        {"input": "", "output": json.dumps(c, ensure_ascii=False)} 
        for c in challenges
    ]
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(deepeval_formatted_challenges, f, ensure_ascii=False, indent=4)

    print(f"Saved challenges to {json_file}")

if __name__ == "__main__":
    synthesize_challenge()