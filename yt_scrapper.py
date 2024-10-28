import pandas as pd
import time
from googleapiclient.discovery import build
from rich.console import Console
import sys

# YouTube API setup
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyBzCdGirVnRwEWIn7QaWzvMzdK6iBmKqg4"

console = Console(record=False)
youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)

def search_videos(youtube, query, max_results):
    videos = []
    next_page_token = None
    while True:
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=min(max_results, 100),
            publishedAfter='2023-09-01T00:00:00Z',
            publishedBefore='2024-05-31T23:59:59Z',
            order='viewCount',
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            videos.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'date': item['snippet']['publishedAt']
            })
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token or len(videos) >= max_results:
            break
        
        time.sleep(1)  # Menghindari batas rate API
    
    return videos

def get_video_comments(youtube, video_id, max_comments):
    comments = []
    next_page_token = None
    
    while True:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=next_page_token,
                textFormat="plainText",
                maxResults=min(max_comments, 100)
            )
            response = request.execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textOriginal'].replace('\n', '\\n').replace('\r', '\\r'),
                    'date': comment['publishedAt']
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(comments) >= max_comments:
                break
            
            time.sleep(1)
        except Exception as e:
            console.log(f"[red]Error retrieving comments: {e}")
            break
    
    return comments

def write_to_csv(data, filename):
    try:
        df = pd.DataFrame(data)
        # Menulis data dengan encoding utf-8
        df.to_csv(filename, mode='a', index=False, header=not pd.io.common.file_exists(filename), encoding='utf-8')
        console.log(f"[green] Data successfully written to {filename}")
    except Exception as e:
        console.log(f"[red]Error writing to CSV: {e}")

def get_data_from_youtube(query, max_video, max_comment):
    console.rule()
    youtube_data = []
    console.log(f"[yellow] [bold]Searching for videos on YouTube for query: {query}")
    videos = search_videos(youtube, query, max_results=max_video)
    console.log(f"[green] Found {len(videos)} videos")
    
    for video in videos:
        youtube_data = []
        video_id = video['id']
        video_title = video['title']
        video_date = video['date']
        console.rule()
        console.log(f"[blue] [bold]Getting comments for video: {video_title}")
        
        comments = get_video_comments(youtube, video_id, max_comments=max_comment)
        console.log(f"[green] Found {len(comments)} comments")
        
        for comment in comments:
            youtube_data.append({
                'video_id': video_id,
                'video_title': video_title,
                'video_date': video_date,
                'comment_text': comment['text'],
                'comment_date': comment['date']
            })
        
        console.log(f"[green] Data collection complete for video: {video_title}")
        console.rule()
        csv_filename = f"data-{query.replace(' ', '_')}.csv"
        write_to_csv(youtube_data, csv_filename) 
        console.rule()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 yt_video_comment_getter.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    get_data_from_youtube(query, 1000000, 1000000)
