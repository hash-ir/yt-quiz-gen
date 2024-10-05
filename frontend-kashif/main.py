import os
import sys
sys.path.append("..")
from typing import List
import logging
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from llama_index.llms.nvidia import NVIDIA
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.groq import Groq
from dotenv import load_dotenv

from mcq_generator import generate_mcqs
from api.transcript import *
from quiz.topics import extract_topics
from quiz.generator import generate_quiz
from quiz.evaluator import change_difficulty
from quiz.quiz_adapter_summary import generate_quiz_adapter_summary
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

load_dotenv(override=True)
app = FastAPI()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = Groq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)

topics_dict = {}
quiz=[]
selectedTopics=[]

class TopicRequest(BaseModel):
    selectedTopics: List[str]

class ResponseData(BaseModel):
    user_answers: List[str]

# Mount the static files (for serving CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates (HTML files stored in the 'templates' directory)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=JSONResponse)
async def homepage(request: Request):
    # Render the main homepage template
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_topics", response_class=JSONResponse)
async def generate_topics(url: str = Form(...)):
    global dropdown_options, topics_dict
    
    file_path = "../data/raw/video.json"
    
    # Initialize cache_data
    cache_data = {}
    
    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                cache_data = json.load(f)  # Try loading the JSON data
            except json.JSONDecodeError:
                print("Error decoding JSON, starting with empty cache.")

    # Check if the URL exists in cache_data
    if url in cache_data:
        print("Found in cache")
        topics_dict = cache_data[url]
    else:
        print("Not found in cache. Loading...")
        topics_dict = extract_topics(llm, url)
        
        # Update the cache with the new URL and its topics
        cache_data[url] = topics_dict

        # Write back the updated cache_data to the file
        with open(file_path, "w") as f:
            json.dump(cache_data, f, indent=4)


    dropdown_options = list(topics_dict.keys())
    return {"topics":dropdown_options}

@app.post("/generate_mcq", response_class=JSONResponse)
async def generate_mcq(request: TopicRequest):
    
    global quiz, topics_dict, selectedTopics
    selectedTopics=request.selectedTopics
    topic_desc = [topics_dict[topic] for topic in selectedTopics]
    quiz_adapter_response="This is the starting of quiz,so we don't have any previous feedback based on user performance,so generate questions randomly for now from the given topic"
    quiz = generate_quiz(llm, selectedTopics, topic_desc, quiz_adapter_response)
    
    mcqs = [
        {
            "question": f"{item[0]}",
            "options": item[1]
        }
        for item in quiz  # Just take the first 5 topics for demo
    ]
   
    return {"mcqs": mcqs}

@app.post("/show_responses", response_class=JSONResponse)
async def show_responses(request: ResponseData):
    global quiz

    correct_answers = [item[2] for item in quiz]
    descriptions = [item[3] for item in quiz]  # Assuming each quiz item has a description
    questions = [item[0] for item in quiz]
    options = [item[1] for item in quiz]

    # Here we return the user responses along with the correct answers and explanations
    return {
        "questions": questions,
        "user_answers": request.user_answers,
        "correct_answers": correct_answers,
        "descriptions": descriptions
    }


@app.post("/adaptive_feedback", response_class=JSONResponse)
async def adaptive_feedback(request: ResponseData):
    global quiz, selectedTopics

    # Extracting the user answers from the request
    user_answers = request.user_answers

    # Check if quiz has been generated
    if not quiz:
        return JSONResponse(status_code=400, content={"message": "Quiz not generated. Please select topics and generate MCQs first."})

    # Extract correct answers and questions from the current quiz
    correct_answers = [item[2] for item in quiz]  # Assuming item[2] contains the correct answer
    questions = [item[0] for item in quiz]        # Assuming item[0] contains the question
    options = [item[1] for item in quiz]          # Assuming item[1] contains the options
    topic_desc = [topics_dict[topic] for topic in selectedTopics]
    # Generate adaptive feedback based on the user’s performance
    # This function needs to be defined based on your LLM logic.
    quiz_adapter_response = generate_quiz_adapter_summary(llm, questions, options, correct_answers, user_answers)

    #print("Quiz adapter response:", quiz_adapter_response)  # Debugging output

    # Update the quiz with new questions based on adaptive feedback
    # This assumes you have some logic to modify `selected_topics` and `quiz_adapter_response`.
    quiz = generate_quiz(llm, selectedTopics ,topic_desc, quiz_adapter_response)
    logger.debug(quiz)
    # Construct the response with the new MCQs
    mcqs = [
        {
            "question": item[0],
            "options": item[1]
        }
        for item in quiz
    ]

    return {"mcqs": mcqs}  # Return the new set of MCQs

@app.post("/submit_responses", response_class=JSONResponse)
async def submit_responses(questions: list[str], responses: list[str]):
    # Process the responses and provide feedback (for now just return the responses)
    global quiz
    
    correct_options=[item[2] for item in quiz]
    descriptions=[item[3] for item in quiz]
   
    result = {"questions": questions, "responses": responses,'correct_options':correct_options,'descriptions':descriptions}
    return {"result": result}