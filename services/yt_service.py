import requests
import urllib.parse
import random
import os
from .db_service import check_if_posted, create_post_db
from supadata import Supadata
#from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from dotenv import load_dotenv
import time
load_dotenv()

supadata = Supadata(api_key=os.getenv("SUPADATA_KEY"))

def get_transcript(video_id):
    # for x in range(3):
    #     try:
    #         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US', 'en-GB', 'en-AU', 'en-CA', 'en'])
    #         message = ' '.join(entry['text'] for entry in transcript)
    #         p40 = int(len(message) * 0.5)
    #         if len(message) >= 20000:
    #             return message[:10000]
    #         else:
    #             return message[:p40]
    #     except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
    #         print("error in getting video transcript")
    #         return "error"
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")
    #         time.sleep(10)
    try:
        transcript = supadata.youtube.transcript(video_id=video_id, lang="en",text=True)
        p40 = int(len(transcript.content) * 0.5)
        if len(transcript.content) <= 200:
            return "error"
        if len(transcript.content) >= 20000:
            return transcript.content[:10000]
        else:
            return transcript.content[:p40]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "error"

def get_yt_link(keyword):
    try:
        conn, cursor = create_post_db()
        api_key = os.getenv('YT_KEY')
        orders = ['rating', 'ViewCount', 'relevance']
        order = random.choice(orders)
        search = urllib.parse.quote(keyword)
        url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={search}&type=video&videoDuration=medium&regionCode=US&maxResults=50&order={order}&videoEmbeddable=true&videoCaption=closedCaption&relevanceLanguage=en&key={api_key}'
        response = requests.get(url)
        links = {'links': []}
        content = {}
        while True:
            for x in response.json()['items']:
                links['links'].append((x['id']['videoId'], x['snippet']['title']))
            id = random.choice(links['links'])
            if check_if_posted(id[0], cursor):
                continue
            link = f'https://www.youtube.com/embed/{id[0]}/'
            content['link'] = link 
            content['title'] = id[1] 
            content['transcript'] = get_transcript(id[0]) 
            if content['transcript'] == "error":
                [links['links'].pop(y) for y, x in enumerate(links['links']) if x[0] == id[0]]
                continue
            break
        return content
    except Exception as e:
        print(e)
        return 'false'
