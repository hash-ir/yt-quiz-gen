import os

import gradio as gr
from llama_index.llms.nvidia import NVIDIA

from data.transcript import get_video_transcript


if os.getenv("NVIDIA_API_KEY") is None:
    raise ValueError("NVIDIA API KEY environment variable is not set")

API_KEY = os.environ["NVIDIA_API_KEY"]
print(API_KEY)

llm = NVIDIA(
    model="meta/llama-3.1-405b-instruct",
    api_key=API_KEY,
    temperature=0.3,
    top_p=0.6,
    max_tokens=1024,
)


def analyze_video(url):
    transcript = get_video_transcript(url)
    if not transcript:
        return f"Unable to retrieve transcript for url: {url}"

    topic_extractor_prompt = f"""<context>{transcript}</context>

    Focus on the video script given between <context><context> tags. 
    You have to understand what this video was about and then identify 
    the main topics that the was talked in the lecture. Topics should be 
    such that the provided video script can be divided easily under 
    those topics. Make sure Topics are not ambiguous and do have some 
    meaninful segregation of content."""

    topics = llm.complete(topic_extractor_prompt)
    # print(topics)

    qa_prompt = f"""<context>{topics}</context>

    Focus on the topic of a YouTube video provided between the
    <context><context> tags. You have to understand what this video was
    about and then create multiple choice Q&A. The Q&A should be such 
    that it will test the knowledge of human who has watched the video.
    Keep in mind to use only the context to generate MCQs. Generate a set
    of 5 questions"""

    qas = llm.complete(qa_prompt)
    # print(qas)

    return topics, qas


iface = gr.Interface(
    fn=analyze_video,
    inputs=gr.Textbox(label="YouTube Video URL"),
    outputs=[gr.Textbox(label="Video Topics"), gr.Textbox(label="Generated Q&A")],
    title="YouTube Quiz Generator",
    description="Enter a YouTube video to create a quiz.",
)


if __name__ == "__main__":
    iface.launch()
