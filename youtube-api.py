import requests

API_KEY = 'AIzaSyDBLX9OgrMQQ_042Zfm4_e-4KvAS5PDl_U'
VIDEO_ID = 'XgbAE0ijBNU'
BASE_URL = 'https://www.googleapis.com/youtube/v3/commentThreads'

def get_comments(video_id, api_key):
    comments = []
    next_page_token = None
    while True:
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'key': api_key,
            'maxResults': 100,
            'pageToken': next_page_token
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        # Extract comments
        for item in data['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        
        # Check if there's a next page token
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    
    return comments

# Run the function
all_comments = get_comments(VIDEO_ID, API_KEY)
# for comment in all_comments:
#     print(comment)
print(len(all_comments))