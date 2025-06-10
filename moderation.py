from services.db_service import fetch_inappropriate_posts, get_member_info, update_inappropriate
from services.like_comments_with_no_api import comment_with_no_api
from services.openai_services import send_prompt
from dotenv import load_dotenv
import requests
import random
import time
import os
load_dotenv()
mod_prompt = """You are a content moderation assistant. When given a post title, your job is to scan it for inappropriate or offensive words and replace each such word with
asterisks of the same length (e.g., "damn" → "****"). Do not change any other part of the text. Return only the cleaned post title, with no explanations, comments, or 
additional output. if the title is fine then just return the exact same input"""
community_id = os.getenv("COMMUNITY_ID")
CIRCLE_KEY = os.getenv("CIRCLE_API")
HEADERS = {
'Authorization': f'Token {CIRCLE_KEY}'
}


mods = [ # must manually add the mods email
    'qezxhm5203@atminmail.com',
    'kjtdcv1822@atminmail.com',
    'tqpyji1267@atminmail.com',
    'nfmuuw7313@atminmail.com',
    'svfgry4022@atminmail.com',
    'tabkzm6301@atminmail.com',
    'brdwhj1411@atminmail.com',
    'asyhgx2362@atminmail.com',
    'siqnrp2900@atminmail.com',
    ]


def mod_comment(post_id, body, user_email):
    url = "https://app.circle.so/api/v1/comments?"
    payload = {"community_id": community_id,
               "post_id": post_id,
               "body": body,
               "user_email": user_email}
    try:
        response = comment_with_no_api(email=user_email, post_id=post_id, comment=body)
        print("comment created with no api call")
        return 
    except Exception as e:
        print(e)
        response = requests.post(url, headers=HEADERS, data=payload)
    if response.status_code == 200:
        if response.json()['success'] == True:
            print("Comment Created")
            return 
        else:
            print("Comment Not Created")
    else:
        print("Comment Not Created")
        return 


def update_posts(post_data, moderator):
    post_id = post_data[-1]
    link = f"https://app.circle.so/api/v1/posts/{post_id}"
    comment = "Your post violates our community guidelines — please review the rules to avoid further action."
    mod_comment(post_id, comment, moderator[0])
    title = post_data[1]
    if not post_data[1]:
        title = "Removed Post"
    title = send_prompt(mod_prompt, title)
    data = {
        "internal_custom_html": f"<b>post content has been removed by moderator {moderator[1]}</b>",
        "name": title,
        "is_comments_closed": True,
        "is_liking_enabled": False}
    requests.patch(link, data=data, headers=HEADERS)
    update_inappropriate(post_id)


while True:
    posts = fetch_inappropriate_posts()
    if posts:
        for x in posts:
            try:
                moderator_email = random.choice(mods)
                name = get_member_info(moderator_email)[0][0]
                moderator = [moderator_email, name]
                update_posts(x, moderator)
            except Exception as e:
                print(e)
    print('yay sleep time')
    time.sleep(1800)