import os

import gradio as gr
from llama_index.llms.nvidia import NVIDIA
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import json
from quiz.topics import extract_topics
from quiz.generator import generate_quiz
from quiz.evaluator import change_difficulty

# fastest inference among all the llm inference APIs but
# unfortunately, also comes with rate-limits. (see https://console.groq.com/docs/rate-limits)
load_dotenv(override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_API_KEY = os.environ["GROQ_API_KEY"]
llm = Groq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)

# initialize topics dictionary and gradio dropdown element
# for storing the topics
topics_dict = {}
dropdown_options = []

# set difficulty level of quiz (start level)
current_difficulty = "Medium"
rounds = 0

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
                topic_selection_button = gr.Button(
                    "Start Quiz", visible=False, variant="primary"
                )

        questions = [gr.Radio(choices=[], label="", visible=False) for _ in range(5)]
        continue_button = gr.Button("Continue", visible=False, variant="primary")
        quit_button = gr.Button("Quit", visible=False, variant="stop")

        quiz_output = gr.Markdown(label="Quiz Report", visible=False)

        @analyze_button.click(
            inputs=url_input, outputs=[topics_dropdown, topic_selection_button]
        )
        def handle_url_submit(url_input):
            global dropdown_options, topics_dict
            with open("data/raw/video.json","r") as f:
                try:
                    j = json.load(f)  # Try loading the JSON data
                except json.JSONDecodeError:
                    j = {} 
                if url_input in j:
                    print("Found in cache")
                    topics_dict=j[url_input]
                else:
                    print("Not found in cache.Loading...")
                    topics_dict = extract_topics(llm, url_input)
            
            j[url_input] = topics_dict

            
            with open("data/raw/video.json", "w") as f:
                json.dump(j, f, indent=4)  

            
            dropdown_options = list(topics_dict.keys())
            return gr.update(
                choices=dropdown_options,
                value=dropdown_options[0],
                visible=True,
                interactive=True,
            ), gr.update(visible=True)

        @topic_selection_button.click(
            inputs=topics_dropdown, outputs=[*questions, continue_button]
        )
        def handle_dropdown_submit(dropdown_selection):
            global quiz, topic
            topic = dropdown_selection
            topic_desc = topics_dict[topic]
            quiz = generate_quiz(llm, dropdown_selection, topic_desc, current_difficulty)
            questions = [item[0] for item in quiz]
            options = [item[1] for item in quiz]

            radios = []
            for i in range(5):
                radios.append(
                    gr.update(
                        choices=options[i],
                        label=questions[i],
                        visible=True,
                        interactive=True,
                    )
                )

            return *radios, gr.update(visible=True)

        @continue_button.click(inputs=questions, outputs=[*questions, quit_button])
        def handle_continue_submit(*questions):
            global current_difficulty, rounds
            user_answers = questions
            correct_answers = [item[2] for item in quiz]

            score = 0
            for user_answer, correct_answer in zip(user_answers, correct_answers):
                if user_answer == correct_answer:
                    score += 1
            
            current_difficulty = change_difficulty(current_difficulty, score)
            
            topic_desc = topics_dict[topic]
            new_quiz = generate_quiz(llm, topic, topic_desc, current_difficulty)  
            questions = [item[0] for item in new_quiz]
            options = [item[1] for item in new_quiz]

            radios = []
            for i in range(5):
                radios.append(
                    gr.update(
                        choices=options[i],
                        label=questions[i],
                        visible=True,
                        interactive=True,
                    )
                )

            rounds += 1
            quit_button_visible = False
            if rounds > 0:
                quit_button_visible = True

            return *radios, gr.update(visible=quit_button_visible)    

        @quit_button.click(inputs=questions, outputs=quiz_output)
        def handle_quiz_submit(*questions):
            user_answers = questions
            correct_answers = [item[2] for item in quiz]
            explanations = [item[3] for item in quiz]

            report = []
            score = 0

            for i, (user_answer, correct_answer, expl) in enumerate(
                zip(user_answers, correct_answers, explanations), 1
            ):
                report.append(f"## Question {i}\n")
                if user_answer == correct_answer:
                    report.append("**Correct**.\n")
                    score += 1
                else:
                    report.append(
                        f"**Incorrect**. The correct answer is **{correct_answer}**.\n"
                    )

                report.append(f"**Explanation**: {expl}\n\n")

            report.append(f"### Final Score: **{score}/{len(quiz)}**\n")
            return gr.update(value="\n".join(report), visible=True)

        @clear_button.click(
            outputs=[
                url_input,
                topics_dropdown,
                quiz_output,
                *questions,
                topic_selection_button,
                continue_button,
                quit_button,
            ]
        )
        def clear_inputs():
            global dropdown_options
            dropdown_options = []
            radios = [
                gr.update(choices=[], label="", visible=False) for _ in range(len(quiz))
            ]
            return (
                "",
                gr.update(choices=[], interactive=False),
                "",
                *radios,
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
            )

    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch(debug=True, show_error=True)
