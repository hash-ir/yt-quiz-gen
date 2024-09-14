import os
import json
from typing import List

import gradio as gr
from llama_index.llms.nvidia import NVIDIA
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.groq import Groq
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
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
llm = Groq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)

# initialize topics dictionary and gradio dropdown element
# for storing the topics
topics_dict = {}
dropdown_options = []


# Pydantic model for parsing output of llm
class Topic(BaseModel):
    """Data model for a topic in a YouTube video"""

    name: str
    description: str


def analyze_video(url):
    transcript = get_video_transcript(url, return_str=True)
    if not transcript:
        raise ValueError(f"Unable to retrieve transcript for url: {url}")

    print(
        f"Fetched transcript with {len(transcript)} characters, approx {len(transcript) // 4} tokens."
    )

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

    return topics_dict


def generate_quiz(topic: str, desc: str):
    qa_prompt = f"""
    Given the topic and description of a YouTube video transcript:
    
    {topic}

    {desc}

    Understand the description and generate a multiple choice Q&A.
    The Q&A should be such that it will test the knowledge of human 
    who watched the YouTube video and particularly this segment/topic of the
    video. Keep in mind to use only the description to generate MCQs. 
    Generate a set of 5 questions."""

    quiz = llm.complete(qa_prompt)

    return quiz


def create_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# YouTube Quiz Generator")

        with gr.Row():
            url_input = gr.Textbox(label="YouTube Video URL")
            analyze_button = gr.Button("Submit")
            clear_button = gr.Button("Clear")

        topics_dropdown = gr.Dropdown(
            label="Select a topic to start quizzing",
            choices=["Placeholder 1", "Placeholder 2"],
            interactive=False,
        )
        topic_selection_button = gr.Button("Start Quiz")

        quiz_output = gr.Textbox(label="Generated Q&A")

        def handle_url_submit(url_input):
            global dropdown_options, topics_dict
            topics_dict = analyze_video(url_input)
            dropdown_options = list(topics_dict.keys())
            return gr.update(
                choices=dropdown_options, value=dropdown_options[0], interactive=True
            )

        def handle_dropdown_submit(dropdown_selection):
            topic_desc = topics_dict[dropdown_selection]
            quiz = generate_quiz(dropdown_selection, topic_desc)
            return quiz

        def clear_inputs():
            global dropdown_options
            dropdown_options = []
            return "", gr.update(choices=[], interactive=False), ""

        analyze_button.click(
            fn=handle_url_submit,
            inputs=url_input,
            outputs=topics_dropdown,
        )

        topic_selection_button.click(
            fn=handle_dropdown_submit, inputs=topics_dropdown, outputs=quiz_output
        )

        clear_button.click(
            fn=clear_inputs, outputs=[url_input, topics_dropdown, quiz_output]
        )

    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch()
