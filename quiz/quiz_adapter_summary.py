import re
import json
from typing import List

from pydantic import BaseModel, parse_obj_as




QUIZ_ADAPTER_PROMPT = """
You an AI assistant that helps another LLM ,which generates MCQ for a user, to understand what is the current knowledge of user in given topic.
<questions>
{questions}
</questions>
<options>
{options}
</options>
<correct_answers>
{correct_answers}
</correct_answers>
<user_answers>
{user_answers}
</user_answers>
You are given above the Questions within <questions> tags,their MCQ options within <options>,their correct answer within <correct_answers> and user selected answer within <user_answers>.
Now i want you create a summary based on user performance which tell which kind of questions/subtopics user has knowledge of and which kind of questions/subtopics user don't have knowledge about.
The report should help another llm to  understand in which kind of questions/subtopics should the difficulty of generated MCQ should increase where user is well versed in that domain and for which kind the difficulty should decrease if user is not able to answer those questions.
Remove the preamble.
"""


def generate_quiz_adapter_summary(llm,questions,options,correct_answers,user_answers):
    prompt = QUIZ_ADAPTER_PROMPT.format(questions=questions, options=options, correct_answers=correct_answers,user_answers=user_answers)
    response = llm.complete(prompt)

    return response
