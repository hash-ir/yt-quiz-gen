import re
import json
from typing import List

from pydantic import BaseModel, parse_obj_as

from api.transcript import get_video_transcript


# Data model for parsing output of llm
class Topic(BaseModel):
    """Data model for a topic in a YouTube video"""

    name: str
    description: str


TOPIC_PROMPT = """
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


def extract_topics(llm, transcript: str):
    # transcript = get_video_transcript(url, return_str=True)
    # if not transcript:
    #     raise ValueError(f"Unable to retrieve transcript for url: {url}")

    # print(
    #     f"Fetched transcript with {len(transcript)} characters, approx {len(transcript) // 4} tokens."
    # )

    prompt = TOPIC_PROMPT.format(transcript=transcript)
    response = llm.complete(prompt)

    try:
        response_text = re.sub(r"(```|json)", "", response.text)
        json_response = json.loads(response_text)
        topics_list = parse_obj_as(List[Topic], json_response)
        topics_dict = {topic.name: topic.description for topic in topics_list}
    except Exception as e:
        raise e

    return topics_dict
