from services.circle_services import create_post
from services.db_service import get_random_user_email, create_post_db, check_if_posted
import schedule
import time
import os
import praw
import random
from dotenv import load_dotenv
from get_reddits import get_subs
from settings.spaces_keywords import subreddits as all_subreddits
from services.seen_service import last_seen
from services.yt_service import get_yt_link
load_dotenv()

max_post = 18

def gallery(post):
    gallery_data = []
    if hasattr(post, "gallery_data") and hasattr(post, "media_metadata"):
        try:
            for item in post.gallery_data["items"]:
                media_id = item["media_id"]
                if media_id in post.media_metadata:
                    image_url = post.media_metadata[media_id]["s"]["u"]
                    gallery_data.append(f'<img src="{image_url}" style="max-width:100%;"><br>')                  
        except Exception as e:
            print(f"Failed to extract gallery images: {e}")
    try:
        if hasattr(post, 'media') and post.media:
            video = post.media.get('reddit_video')['fallback_url']
            gallery_data.append((
"<iframe width='560' height='315' "
f"src={video} "
"frameborder='0' "
"allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' "
"allowfullscreen></iframe>"
)) 
    except Exception as e:
        print(f"Failed to extract videos: {e}")
    
    return gallery_data



def setup_scrapper():
     reddit = praw.Reddit(
         client_id= os.getenv('CLIENT_ID'),
         client_secret= os.getenv('CLIENT_SECRET'),
         user_agent= os.getenv('USER_AGENT'),
     )
 
     return reddit


def main():
    global gallery_data
    scraped = 0
    reddit = setup_scrapper()
    conn, cursor = create_post_db()
    subs_post_plan, avg_sleep_time = get_subs()
    print(f"Subreddits to scrape: {subs_post_plan}")
    for sub_key, num_posts in subs_post_plan.items():        
        if sub_key not in all_subreddits:
            print(f"Skipping {sub_key} - not found in all_subreddits.")
            continue

        sub_data = all_subreddits[sub_key]
        original_subreddit_name = sub_data.get('original')
        space_id = sub_data.get('space_id', 9999)
        keywords = sub_data.get('keywords', [])
        if not original_subreddit_name:
            print(f"Skipping {sub_key} - missing 'original' subreddit name.")
            continue

        for _ in range(num_posts):
            if scraped >= max_post:
                break

            try:
                subreddit = reddit.subreddit(original_subreddit_name)
                if not keywords:
                    print("No keywords found.")
                else:
                    keyword = random.choice(keywords)
                    chance = random.randint(10,20)
                    reddit_chance = 100 - chance
                    res = random.randint(1,100)
                    print(f"Searching keyword: {keyword}")
                    for post in subreddit.search(keyword, sort=random.choice(["new", "relevance"])):
                        if  res <= reddit_chance:
                            youtube = False
                            reddit_link = post.permalink
                            original_title = post.title
                            try:
                                external_link = post.url
                            except Exception:
                                external_link = None

                            gallery_data = gallery(post)
                            startwith = ("https://www.reddit.com", "https://v.redd.it/")
                            valid_image_extensions = ('jpg','jpeg','tiff','png','gif','bmp', 'mp4', 'webm' ,'ogg', 'gifv')
                            original_description = post.selftext
                            if len(original_description) <= 5 and external_link.endswith(valid_image_extensions) or \
                                len(original_description) <= 5 and external_link == None or \
                                len(original_description) <= 5 and external_link.find('redd') != -1 or \
                                original_description.startswith('https://') or \
                                external_link.find('youtu') != -1 or \
                                external_link.find('imgur') != -1:
                                continue

                            if external_link.startswith(startwith):
                                external_link = None

                            author = post.author.name if post.author else "[deleted]"
                            post_info = f"-- Found Post: {original_title}"
                            if author == 'AutoModerator':
                                print("Skipping AutoModerator post.")
                                continue

                            if check_if_posted(reddit_link, cursor):
                                print("Skipping: Already posted.")
                                continue
                            print(f"{post_info}")
                            print(f"Link: {reddit_link}")
                        else:
                            youtube = True
                            content = get_yt_link(keyword=keyword)
                            if content == 'false' or len(content['transcript']) <= 5:
                                
                                continue
                        try:
                            random_email = get_random_user_email()
                            if not random_email:
                                print("Error: Could not fetch random email. Skipping post.")
                                continue

                            print(f"Processing and Posting to Circle using email: {random_email}...")
                            if not youtube:
                                status = create_post(
                                    space_id = space_id,
                                    email = random_email,
                                    title = original_title,
                                    description = original_description,
                                    external_link = external_link,
                                    url = reddit_link,
                                    html_to_add = gallery_data,
                                )

                                if status == "false":
                                    continue
                            else:
                                status = create_post(
                                    space_id = space_id,
                                    email = random_email,
                                    is_youtube = youtube,
                                    title = content['title'],
                                    link = content['link'],
                                    description = content['transcript']
                                )
                                if status == "false":
                                    continue

                        except Exception as e:
                            print(f"Error during Circle processing/posting: {e}")
                        print("--- Done with this keyword ---")
                        sleep_time = random.randint(avg_sleep_time - 900, avg_sleep_time + 250)
                        print(sleep_time)
                        time.sleep(sleep_time)
                        break

            except praw.exceptions.PRAWException as e:
                print(f"Error accessing subreddit {original_subreddit_name}: {e}")
            except Exception as e:
                err_msg = (
                    f"An unexpected error occurred for {original_subreddit_name}"
                )
                print(f"{err_msg}: {e}")
    print(f"Finished processing.")
    if conn:
        conn.close()

schedule.every().day.at("04:00").do(main)

while True:
    schedule.run_pending()
    time.sleep(60)
