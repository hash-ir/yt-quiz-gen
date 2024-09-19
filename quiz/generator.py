import re
import json
from typing import List

from pydantic import BaseModel, parse_obj_as


# Data model for parsing output of llm
class Question(BaseModel):
    """Data model for a quiz question"""

    question: str
    options: List[str]
    answer: str
    explanation: str


QUIZ_PROMPT = """
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
Generate a set of 5 questions at {difficulty} difficulty level. 
Remove the preamble and ensure your output is valid JSON.
"""


def generate_quiz(llm, topic: str, desc: str, current_difficulty: str):
    prompt = QUIZ_PROMPT.format(topic=topic, desc=desc, difficulty=current_difficulty)
    response = llm.complete(prompt)

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
