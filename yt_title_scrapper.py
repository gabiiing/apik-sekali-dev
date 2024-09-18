import datetime as dt
import logging
import os
import random
import re
import time

import requests
import urllib3
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from rich.console import Console
from rich.logging import RichHandler
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console(record=True)
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0"
}

timeout = 100
delay = (5,12)

def get_retry_session(retries, session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        status_forcelist=[500, 521, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.verify = False
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def print_response_info(response):
    console.log(response.request.method, response.request.path_url,
                response.status_code, response.elapsed)

def scrap():
    url = "https://www.youtube.com/results?search_query=youtube+scrapper+with+beautifulsoup"
    session = get_retry_session(retries=3)
    response = session.get(url, headers=headers, timeout=timeout)
    print_response_info(response)

    if response.ok:
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        # Extract video renderer
        video_renderer = soup.find('ytd-video-renderer')

        if video_renderer:
            # Extract video title
            title_tag = video_renderer.find('a', id='video-title')
            title = title_tag.get('title') if title_tag else 'No title found'
            
            # Extract video URL
            video_url = title_tag.get('href') if title_tag else 'No URL found'
            video_url = 'https://www.youtube.com' + video_url

            # Extract thumbnail URL
            thumbnail_tag = video_renderer.find('img')
            thumbnail_url = thumbnail_tag.get('src') if thumbnail_tag else 'No thumbnail found'

            # Extract channel name
            channel_tag = video_renderer.find('a', class_='yt-simple-endpoint')
            channel_name = channel_tag.get_text() if channel_tag else 'No channel name found'

            # Extract view count and publish date
            meta_block = video_renderer.find('ytd-video-meta-block')
            metadata_line = meta_block.find('div', id='metadata-line')
            if metadata_line:
                metadata_items = metadata_line.find_all('span', class_='inline-metadata-item')
                view_count = metadata_items[0].get_text() if len(metadata_items) > 0 else 'No view count found'
                publish_date = metadata_items[1].get_text() if len(metadata_items) > 1 else 'No publish date found'
            else:
                view_count = 'No view count found'
                publish_date = 'No publish date found'

            # Print the extracted data
            print(f"Title: {title}")
            print(f"URL: {video_url}")
            print(f"Thumbnail URL: {thumbnail_url}")
            print(f"Channel Name: {channel_name}")
            print(f"View Count: {view_count}")
            print(f"Publish Date: {publish_date}")
        else:
            print("No video renderer found")
    else:
        console.log("Failed to fetch the page")

def main():
    scrap()


if __name__ == "__main__":
    main()