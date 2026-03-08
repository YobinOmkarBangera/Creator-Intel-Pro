import os
import polars as pl
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_id(url):
    if "youtube.com/@" in url:
        handle = url.split("@")[1].split("/")[0]
        res = youtube.search().list(q=handle, type='channel', part='id').execute()
        return res['items'][0]['id']['channelId']
    return url.split("channel/")[1] if "channel/" in url else url.split("/")[-1]

def fetch_creator_full_audit(url):
    try:
        c_id = get_channel_id(url)
        c_res = youtube.channels().list(part="snippet,statistics", id=c_id).execute()['items'][0]
        v_res = youtube.search().list(channelId=c_id, part="id", order="date", maxResults=30, type="video").execute()
        v_ids = [item['id']['videoId'] for item in v_res['items']]
        video_stats = youtube.videos().list(id=",".join(v_ids), part="statistics,snippet").execute()['items']
        
        views = [int(v['statistics'].get('viewCount', 0)) for v in video_stats]
        likes = [int(v['statistics'].get('likeCount', 0)) for v in video_stats]
        comments_count = [int(v['statistics'].get('commentCount', 0)) for v in video_stats]
        titles = [v['snippet']['title'] for v in video_stats]

        com_res = youtube.commentThreads().list(part="snippet", videoId=v_ids[0], maxResults=500).execute()
        raw_comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in com_res.get('items', [])]
        authors = [item['snippet']['topLevelComment']['snippet']['authorDisplayName'] for item in com_res.get('items', [])]

        return {
            "name": c_res['snippet']['title'],
            "logo": c_res['snippet']['thumbnails']['high']['url'],
            "subs": int(c_res['statistics']['subscriberCount']),
            "total_views": int(c_res['statistics']['viewCount']),
            "video_count": int(c_res['statistics']['videoCount']),
            "avg_views": sum(views)//len(views),
            "avg_likes": sum(likes)//len(likes),
            "avg_comments": sum(comments_count)//len(comments_count),
            "comment_data": pl.DataFrame({"author": authors, "text": raw_comments}),
            "recent_performance": pl.DataFrame({"Title": titles, "Views": views, "Likes": likes})
        }
    except Exception:
        return None