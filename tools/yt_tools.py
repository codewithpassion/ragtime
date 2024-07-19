import json
import os
import re
import argparse
import youtube_dl
from dotenv import load_dotenv

from tools.transcript_util import get_video_data, get_video_id


def get_env_or_query(var_name, prompt):
    """Gets an environment variable or prompts the user for input.

    Args:
        var_name: The name of the environment variable.
        prompt: The prompt to display to the user if the environment variable is not set.

    Returns:
        The value of the environment variable or the user's input.
    """

    value = os.getenv(var_name)
    if value is not None:
        return value

    value = input(prompt + " ")
    return value


def get_channel_videos(channel_url):
    ydl_opts = {"ignoreerrors": True, "extract_flat": True, "quiet": True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        if "entries" in result:
            return [video["url"] for video in result["entries"]]
    return []


def download_audio(video_urls):
    ydl_opts = {"format": "bestaudio/best", "quiet": False}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_urls)


def main():
    load_dotenv()
    api_key = get_env_or_query("YOUTUBE_API_KEY", "Please enter your YouTube API key:")

    parser = argparse.ArgumentParser(description="yt-tools - download channel lists and video transcripts")

    parser.add_argument("url", help="YouTube channel/playlist/video URL")
    parser.add_argument("--list", action="store_true", help="List all videos in the channel")
    parser.add_argument("--comments", action="store_true", help="Include comments for the video")
    parser.add_argument("--lang", default="en", help="Language for the transcript (default: English)")
    parser.add_argument("--audio", action="store_true", help="Download audio")

    args = parser.parse_args()

    if args.url is None:
        print("Error: No URL provided.")
        return

    video_id = get_video_id(args.url)
    if video_id is None:
        videos = get_channel_videos(args.url)
        if len(videos) == 0:
            print("Error: No videos found.")
            return

        if args.list:
            for video in videos:
                print(f"https://www.youtube.com/watch?v={video}")
            return

        output_dir = None

        if args.audio:
            urls = [f"https://www.youtube.com/watch?v={video}" for video in videos]
            download_audio(urls)
            return

        for video in videos:
            data = get_video_data(video, api_key, args)

            if output_dir is None:
                # make a directory for the channel
                channel_name = data["metadata"]["channel"]
                os.makedirs(channel_name, exist_ok=True)
                output_dir = channel_name

            # save the data to a file
            title = data["metadata"]["title"]
            # sanitize the title
            title = re.sub(r"[^\w\s]", "_", title)
            title = title.replace(" ", "_")

            published_at = data["metadata"]["published_at"]
            published_at = re.sub(r"[^\w\s]", "_", published_at)

            id = data["metadata"]["id"]
            file_name = f"{channel_name}/{published_at}_{title}_{id}.json"

            with open(file_name, "w") as f:
                f.write(str(json.dumps(data, indent=2)))
                print(f"Created {file_name}")

        return

    else:
        data = get_video_data(video_id, api_key, args)
        print(json.dumps(data, indent=2))
