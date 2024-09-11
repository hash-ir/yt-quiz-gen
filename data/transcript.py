from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(url):
    """Extract the video ID from a YouTube URL.

    Args:
        url (str): video url
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query)["v"][0]
        if parsed_url.path[:7] == "/embed/":
            return parsed_url.path.split("/")[2]
        if parsed_url.path[:3] == "/v/":
            return parsed_url.path.split("/")[2]
    return None


def get_transcript(url, languages=("en",)):
    """Retrieve transcript of a YouTube video.

    Note:
        * Automagically generated captions are also extracted

    Args:
        url (str): video url

    Returns:
        list: list of dicts containing the 'text',
            'start', and 'duration' keys
    """
    video_id = get_video_id(url)
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    return transcript


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=u4xNUpE0SJ0&t"
    languages = ("hi", "en")  # try to fetch in this order of languages

    try:
        transcript = get_transcript(video_url, languages)
    except Exception as e:
        transcript = None
        print(e)

    if transcript is not None:
        text = ""
        for item in transcript:
            text += item["text"]

        print(text)