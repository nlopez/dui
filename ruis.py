#!/usr/bin/env python
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from pprint import pprint
from requests import Session
from slugify import slugify
from time import time
from urllib.parse import urlparse
import concurrent.futures
import configparser
import os
import praw
import requests
import sys


def process_submission(cache_session, submission, headers):
    if getattr(submission, 'post_hint', None) == 'image':
        response = cache_session.get(submission.url, headers=headers)
        if response.status_code == 200:
            root, ext = os.path.splitext(submission.url)
            subreddit = submission.subreddit.display_name
            created_utc = int(submission.created_utc)
            download_dir = os.path.join(
                os.getcwd(), 'ruis', subreddit)
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            title_id = slugify("{}-{}".format(submission.title, submission.id))
            filename = "{}{}".format(title_id, ext)
            download_path = os.path.join(download_dir, filename)
            with open(download_path, 'wb') as f:
                f.write(response.content)
            # Set access time to now
            # Set modified time to the created timestamp of the Reddit post
            now = int(time())
            os.utime(download_path, (now, created_utc))
            return download_path


config = configparser.ConfigParser()
config_file = os.getenv('RUIS_INI', 'ruis.ini')
config.read(config_file)
if not 'ruis' in config.sections():
    print("missing \"ruis\" section in {}".format(config_file))
    sys.exit(1)

cache_session = CacheControl(
    requests.Session(), FileCache(config['ruis']['cache_dir']))
headers = {'user-agent': config['ruis']['user_agent']}

reddit = praw.Reddit(
    username=config['ruis']['reddit_username'],
    password=config['ruis']['reddit_password'],
    client_id=config['ruis']['reddit_client_id'],
    client_secret=config['ruis']['reddit_client_secret'],
    user_agent=config['ruis']['user_agent']
)
me = reddit.user.me()
upvoted = me.upvoted(limit=int(config['ruis']['upvoted_limit']))
thread_count = int(config['ruis']['thread_count'])
timeout_seconds = int(config['ruis']['timeout_seconds'])

with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
    future_to_url = {executor.submit(
        process_submission, cache_session, s, headers): s for s in upvoted}
    for future in concurrent.futures.as_completed(future_to_url, timeout=timeout_seconds):
        url = future_to_url[future]
        try:
            print(future.result())
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
