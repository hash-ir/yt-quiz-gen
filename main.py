import os
import re
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


class Question(BaseModel):
    """Data model for a quiz question"""

    question: str
    options: List[str]
    answer: str
    explanation: str


def analyze_video(url):
    transcript = get_video_transcript(url, return_str=True)
    if not transcript:
        raise ValueError(f"Unable to retrieve transcript for url: {url}")

    print(
        f"Fetched transcript with {len(transcript)} characters, approx {len(transcript) // 4} tokens."
    )

    topic_extractor_prompt = f"""
    Given the transcript of a YouTube video tutorial:

    {transcript}

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
    # global topics_dict
    try:
        response_text = re.sub(r"(```|json)", "", response.text)
        json_response = json.loads(response_text)
        topics_list = parse_obj_as(List[Topic], json_response)
        topics_dict = {topic.name: topic.description for topic in topics_list}
    except Exception as e:
        raise e

    return topics_dict


def generate_quiz(topic: str, desc: str):
    qa_prompt = f"""
    Given the topic and description of a YouTube video transcript:
    
    {topic}

    {desc}

    Understand the description and generate a multiple choice Q&A.
    The Q&A should be such that it will test the knowledge of human 
    who watched the YouTube video and particularly this segment/topic of the
    video. 
    
    Format your response as a JSON array of objects, where each object
    has three fields:
    - "question": The question about the topic
    - "options": The four options to answer the question 
        (exactly one of them will be correct) 
    - "answer": The correct option/answer to the question
    - "explanation": The explanation about the answer

    Example format:
    [
        {{
            "question": "Question 1",
            "options": [
                "a) option 1",
                "b) option 2",
                "c) option 3",
                "d) option 4"
            ],
            "answer": "Answer 1",
            "explanation": "Explanation 1"
        }},
        {{
            "question": "Question 2",
            "options": [
                "a) option 1",
                "b) option 2",
                "c) option 3",
                "d) option 4"
            ],
            "answer": "Answer 2",
            "explanation": "Explanation 2"
        }}
    ]
    
    Keep in mind to use only the description to generate MCQs. 
    Generate a set of 5 questions. Remove the preamble and ensure
    your output is valid JSON."""

    response = llm.complete(qa_prompt)

    try:
        response_text = re.sub(r"(```|json)", "", response.text)
        json_response = json.loads(response_text)
        quiz = parse_obj_as(List[Question], json_response)
        qna = [
            (item.question, item.options, item.answer, item.explanation)
            for item in quiz
        ]
    except Exception as e:
        raise e

    return qna


def create_interface():
    with gr.Blocks(theme=gr.themes.Default()) as interface:
        gr.Markdown("# YouTube Quiz Generator")

        with gr.Row():
            with gr.Column(scale=1):
                url_input = gr.Textbox(label="YouTube Video URL")
                with gr.Row():
                    analyze_button = gr.Button("Submit", variant="primary")
                    clear_button = gr.Button("Clear")

            with gr.Column(scale=1):
                topics_dropdown = gr.Dropdown(
                    label="Select a topic to start quizzing",
                    choices=[],
                    visible=True,
                    interactive=False,
                )
                topic_selection_button = gr.Button("Start Quiz", visible=False, variant="primary")

        questions = [gr.Radio(choices=[], label="", visible=False) for _ in range(5)]
        quiz_submit_button = gr.Button("Submit", visible=False, variant="primary")

        quiz_output = gr.Markdown(label="Quiz Report", visible=False)

        @analyze_button.click(inputs=url_input, outputs=[topics_dropdown, topic_selection_button])
        def handle_url_submit(url_input):
            global dropdown_options, topics_dict
            topics_dict = analyze_video(url_input)
            dropdown_options = list(topics_dict.keys())
            return gr.update(
                choices=dropdown_options, 
                value=dropdown_options[0], 
                visible=True,
                interactive=True
            ), gr.update(visible=True)

        @topic_selection_button.click(inputs=topics_dropdown, outputs=[*questions, quiz_submit_button])
        def handle_dropdown_submit(dropdown_selection):
            global quiz
            topic_desc = topics_dict[dropdown_selection]
            quiz = generate_quiz(dropdown_selection, topic_desc)
            questions = [item[0] for item in quiz]
            options = [item[1] for item in quiz]

            radios = []
            for i in range(5):
                radios.append(
                    gr.update(
                        choices=options[i], 
                        label=questions[i], 
                        visible=True, 
                        interactive=True
                    )
                )

            return *radios, gr.update(visible=True)

        @quiz_submit_button.click(inputs=questions, outputs=quiz_output)
        def handle_quiz_submit(*questions):
            user_answers = questions
            correct_answers = [item[2] for item in quiz]
            explanations = [item[3] for item in quiz]

            report = []
            score = 0

            for i, (user_answer, correct_answer, expl) in enumerate(zip(user_answers, correct_answers, explanations), 1):
                report.append(f"## Question {i}\n")
                if user_answer == correct_answer:
                    report.append("**Correct**.\n")
                    score += 1
                else:
                    report.append(f"**Incorrect**. The correct answer is **{correct_answer}**.\n")
                
                report.append(f"**Explanation**: {expl}\n\n")

            report.append(f"### Final Score: **{score}/{len(quiz)}**\n")
            return gr.update(value="\n".join(report), visible=True)

        @clear_button.click(outputs=[url_input, topics_dropdown, quiz_output, *questions, topic_selection_button, quiz_submit_button])
        def clear_inputs():
            global dropdown_options
            dropdown_options = []
            radios = [gr.update(choices=[], label="", visible=False) for _ in range(len(quiz))]
            return "", gr.update(choices=[], interactive=False), "", *radios, gr.update(visible=False), gr.update(visible=False)

    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch(debug=True, show_error=True)
