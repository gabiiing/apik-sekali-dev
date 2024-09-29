import pandas as pd
import time
from googleapiclient.discovery import build
from rich.console import Console
from rich.logging import RichHandler

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyDBLX9OgrMQQ_042Zfm4_e-4KvAS5PDl_U"

console = Console(record=False)

youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)
def search_videos(youtube, query, max_results=100):
    videos = []
    next_page_token = None
    
    while len(videos) < max_results:
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=min(50, max_results - len(videos)),
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            video_id = item['id']['videoId']
            video_title = item['snippet']['title']
            video_date = item['snippet']['publishedAt']
            videos.append({
                'id': video_id,
                'title': video_title,
                'date': video_date
            })
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
        
        time.sleep(1)  # Avoid hitting API rate limits
    
    return videos
def get_video_comments(youtube, video_id, max_comments=100):
    comments = []
    next_page_token = None
    
    while len(comments) < max_comments:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments)),
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
              
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textOriginal'],
                    'date': comment['publishedAt']
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
            
            time.sleep(1)  # Avoid hitting API rate limits
        except Exception as e:
            print(f"Error retrieving comments: {e}")
            break
    
    return comments


def write_to_csv(data, filename):
    console.log(f"[yellow] Writing data to comments.csv")

    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=["video_id", "video_title", "video_date", "comment_text", "comment_date"])

    # Check if the file exists
    try:
        existing_df = pd.read_csv(filename, error_bad_lines=False)
        df = pd.concat([existing_df, df], ignore_index=True)
        header = False  # Don't write header if file already exists
    except FileNotFoundError:
        header = True  # Write header if it's a new file
    except pd.errors.ParserError as e:
        console.log(f"[red] Error reading {filename}: {e}")
        header = True  # Write header if there's an error reading the file

    # Write to CSV
    df.to_csv(filename, mode='a', header=header, index=False)
    console.log(f"[green] Data written to comments.csv")


def pandas_to_csv(data, new_df):
    with open('comments.csv',  'a', encoding = 'utf=8') as file:
     new_df.to_csv(file)

def get_data_from_youtube(query, max_video, max_comment):
    console.rule()
    youtube_data = []
    console.log(f"[yellow] [bold]Searching for videos on YouTube for query: {query}")
    videos = search_videos(youtube, query, max_results=max_video)
    console.log(f"[green] Found {len(videos)} videos")
    for video in videos:
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
            # write_to_csv(youtube_data, "comments.csv")
     
        console.log(f"[green] Data collection complete for video: {video_title}")
        console.rule()
    new_df = pd.DataFrame(youtube_data)
    pandas_to_csv(youtube_data, new_df)
    console.rule()

if __name__ == "__main__":
    query = "Mulyono"
    get_data_from_youtube(query, 1, 1000)