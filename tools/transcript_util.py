import io
import json
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
import csv
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(url):
    # Extract video ID from URL
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_video_data(url: str, api_key: str, options):
    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        video_id = get_video_id(url)
        if (video_id is None) and len(url) > 0:
            video_id = url

        # Get video details
        video_response = youtube.videos().list(id=video_id, part="contentDetails,snippet").execute()

        # Extract video duration and convert to minutes
        duration_iso = video_response["items"][0]["contentDetails"]["duration"]
        duration_seconds = isodate.parse_duration(duration_iso).total_seconds()
        duration_minutes = round(duration_seconds / 60)
        # Set up metadata
        metadata = {}
        metadata["id"] = video_response["items"][0]["id"]
        metadata["title"] = video_response["items"][0]["snippet"]["title"]
        metadata["channel"] = video_response["items"][0]["snippet"]["channelTitle"]
        metadata["published_at"] = video_response["items"][0]["snippet"]["publishedAt"]

        # Get video transcript
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[options.lang])
            transcript_text = " ".join([item["text"] for item in transcript_list])
            transcript_text = transcript_text.replace("\n", " ")

            # Create CSV output for transcript with timestamps
            transcript_data = [["start", "duration", "text"]]
            for item in transcript_list:
                transcript_data.append([item["start"], item["duration"], item["text"]])

            transcript_ts_output = io.StringIO()
            csv_writer = csv.writer(transcript_ts_output, quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerows(transcript_data)
            # transcript_ts_text = transcript_ts_output.getvalue()
            transcript_ts_output.close()

        except Exception as e:
            transcript_text = f"Transcript not available in the selected language ({options.lang}). ({e})"

        # Get comments if the flag is set
        comments = []
        if options.comments:
            comments = get_comments(youtube, video_id)

        # Output based on options
        output = {}
        output["transcript"] = transcript_text
        output["transcript-ts"] = transcript_list
        output["duration"] = duration_minutes
        output["comments"] = comments
        output["metadata"] = metadata

        return output
    except HttpError as e:
        print(f"Error: Failed to access YouTube API. Please check your YOUTUBE_API_KEY and ensure it is valid: {e}")


def get_comments(youtube, video_id):
    comments = []

    try:
        # Fetch top-level comments
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100,  # Adjust based on needs
        )

        while request:
            response = request.execute()
            for item in response["items"]:
                # Top-level comment
                topLevelComment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(topLevelComment)

                # Check if there are replies in the thread
                if "replies" in item:
                    for reply in item["replies"]["comments"]:
                        replyText = reply["snippet"]["textDisplay"]
                        # Add incremental spacing and a dash for replies
                        comments.append("    - " + replyText)

            # Prepare the next page of comments, if available
            if "nextPageToken" in response:
                request = youtube.commentThreads().list_next(previous_request=request, previous_response=response)
            else:
                request = None

    except HttpError as e:
        print(f"Failed to fetch comments: {e}")

    return comments
