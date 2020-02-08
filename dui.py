#!/usr/bin/env python
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from pprint import pprint
from requests import Session
from time import time
from urllib.parse import urlparse
import concurrent.futures
import configparser
import os
import praw
import requests
import sys
from pebble import ProcessPool
from concurrent.futures import TimeoutError


def process_submission(cache_session, submission, headers, data_dir):
    if getattr(submission, 'post_hint', None) == 'image':
        response = requests.get(submission.url, headers=headers)
        if response.status_code == 200:
            root, ext = os.path.splitext(submission.url)
            subreddit = submission.subreddit.display_name
            created_utc = int(submission.created_utc)

            # directories by subreddit name
            download_dir = os.path.join(data_dir, subreddit)
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            # filename from permalink + submission id
            name = submission.permalink.strip('/').split('/')[-1]
            filename = "{}-{}{}".format(name, submission.id, ext)
            download_path = os.path.join(download_dir, filename)
            with open(download_path, 'wb') as f:
                f.write(response.content)

            # Set access time to now
            # Set modified time to the created timestamp of the Reddit post
            now = int(time())
            os.utime(download_path, (now, created_utc))

            return download_path

def task_done(future):
    try:
        result = future.result()  # blocks until results are ready
        print(result)
    except TimeoutError as error:
        print("Function took longer than %d seconds" % error.args[1])
    except Exception as error:
        print("Function raised %s" % error)
        print(error.traceback)  # traceback of the function


config = configparser.ConfigParser()
config_file = os.getenv('DUI_INI', 'config/dui.ini')
config.read(config_file)
if not 'dui' in config.sections():
    print("missing \"dui\" section in {}".format(config_file))
    sys.exit(1)

cache_dir = config['dui']['cache_dir']
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
cache_session = CacheControl(requests.Session(), cache=FileCache(cache_dir))
headers={'user-agent': config['dui']['user_agent']}

reddit=praw.Reddit(
    username=config['dui']['reddit_username'],
    password=config['dui']['reddit_password'],
    client_id=config['dui']['reddit_client_id'],
    client_secret=config['dui']['reddit_client_secret'],
    user_agent=config['dui']['user_agent']
)
me=reddit.user.me()
upvoted=me.upvoted(limit=int(config['dui']['upvoted_limit']))
thread_count=int(config['dui']['thread_count'])
timeout_seconds=int(config['dui']['timeout_seconds'])
data_dir=config['dui']['data_dir']

with ProcessPool(max_workers=thread_count) as pool:
    for post in upvoted:
        args = [cache_session, post, headers, data_dir]
        future = pool.schedule(process_submission, args=args, timeout=timeout_seconds)
        future.add_done_callback(task_done)
