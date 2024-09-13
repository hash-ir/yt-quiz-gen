import os
import json
from typing import List

import gradio as gr
from llama_index.core.callbacks import TokenCountingHandler
from llama_index.llms.nvidia import NVIDIA
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.groq import Groq 
from transformers import AutoTokenizer
from pydantic import BaseModel, parse_obj_as

from data.transcript import get_video_transcript


# if os.getenv("NVIDIA_API_KEY") is None:
#     raise ValueError("NVIDIA API KEY environment variable is not set")

# llm = NVIDIA(
#     model="nvidia/llama3-chatqa-1.5-70b",
#     api_key=API_KEY,
#     temperature=0.3,
#     top_p=0.6,
#     max_tokens=1024,
# )

# fastest inference among all the llm inference APIs but
# unfortunately, also comes with rate-limits. (see https://console.groq.com/docs/rate-limits)
GROQ_API_KEY = os.environ['GROQ_API_KEY']
llm = Groq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)

# use an associated tokenizer based on the llm above
# to count the tokens of the prompt 
tokenizer = AutoTokenizer.from_pretrained("ICTNLP/Llama-3.1-8B-Omni")
token_counter = TokenCountingHandler(
    tokenizer=tokenizer.encode
)

# Pydantic model for parsing output of llm
class Topic(BaseModel):
    """Data model for a topic in a YouTube video"""
    name: str
    description: str


def analyze_video(url):
    transcript = get_video_transcript(url, return_str=True)
    if not transcript:
        return f"Unable to retrieve transcript for url: {url}"

    print(f"Fetched transcript with {len(transcript)} characters, approx {len(transcript) // 4} tokens.")

    topic_extractor_prompt = f"""
    Given the transcript of a YouTube video tutorial:

    {transcript[:-100000]}

    Understand what this video is about and identify the main topics.
    Include as much description as possible for each topic.
    Make sure topics are not ambiguous and have meaningful segregation of content.

    Format your response as a JSON array of objects, where each object has two fields:
    - "name": The name of the topic (a short, concise title)
    - "description": A detailed description of the topic

    Example format:
    [
    {{
        "name": "Topic 1",
        "description": "Detailed description of Topic 1..."
    }},
    {{
        "name": "Topic 2",
        "description": "Detailed description of Topic 2..."
    }}
    ]

    Remove the preamble and ensure your output is valid JSON. 
    """

    response = llm.complete(topic_extractor_prompt)

    global topics_dict
    try:
        json_response = json.loads(response.text)
        topics_list = parse_obj_as(List[Topic], json_response)
        topics_dict = {topic.name: topic.description for topic in topics_list}
    except json.JSONDecodeError:
        print("Error: The LLM output was not valid JSON.")
    except ValueError:
        print("Error: The LLM output did not match the expected format.")

    topics = list(topics_dict.keys())
    print(topics)

    return topics, ""
    # topics_out = f"""I have identified the following topics from the video: {topics}"""

def generate_quiz(topic):
    topic_desc = topics_dict[topic]
    qa_prompt = f"""<context>{topic_desc}</context>

    Focus on the topic of a YouTube video provided between the
    <context><context> tags. You have to understand what this video was
    about and then create multiple choice Q&A. The Q&A should be such 
    that it will test the knowledge of human who has watched the video.
    Keep in mind to use only the context to generate MCQs. Generate a set
    of 5 questions"""

    qas = llm.complete(qa_prompt)

    return qas

def create_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# YouTube Quiz Generator")

        url_input = gr.Textbox(label="YouTube Video URL")
        analyze_button = gr.Button("Submit")
        error_output = gr.Textbox(label="Status", visible=True)
        topics_dropdown = gr.Dropdown(
            label="Select a topic to start quizzing", 
            choices=["Placeholder 1", "Placeholder 2"], 
            interactive=False,
            allow_custom_value=True
        )
        quiz_button = gr.Button("Start Quiz", interactive=False)
        qa_output = gr.Textbox(label="Generated Q&A")

        analyze_button.click(
            fn=analyze_video,
            inputs=url_input,
            outputs=[topics_dropdown, error_output],
        )

        topics_dropdown.change(
            lambda x: gr.Dropdown(choices=x, interactive=True, allow_custom_value=True), 
            inputs=[topics_dropdown]
        )

        def on_quiz_click(topic):
            return generate_quiz(topic)

        quiz_button.click(
            fn=on_quiz_click,
            inputs=topics_dropdown,
            outputs=qa_output
        )

    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch()
