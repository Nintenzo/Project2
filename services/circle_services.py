import requests
import openai
from .db_service import insert_post, get_random_user_email, get_post_data
from services.like_comments_with_no_api import like_with_no_api
from services.like_comments_with_no_api import comment_with_no_api
from dotenv import load_dotenv
from .db_service import get_gender
from .seo_service import get_seo
from settings.system_prompts import get_system_prompt
from math import floor
import os
import random
import time

load_dotenv()
circle_key = os.getenv("CIRCLE_API")
circle_headers = {
    'Authorization': f'Token {circle_key}'
}
community_id = os.getenv("COMMUNITY_ID")
def send_to_gpt(message, final_identity, original_identity, is_youtube=False, is_post=False, n=30, previous_openings=None, link=None, post_id=None, is_introduction=False):
    prompt = get_system_prompt(final_identity=final_identity, original_identity=original_identity,
                               is_youtube=is_youtube, is_post=is_post, n=n, previous_openings=previous_openings,
                               link=link, post_id=post_id, is_introduction=is_introduction)

    openai.api_key = os.getenv("GPT_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": prompt
                },
            {"role": "user", "content": message}
        ]
    )
    
    rewrite = response["choices"][0]["message"]["content"]
    
    if is_post or is_youtube:
        sentiment = rewrite.split('\n')[0]
        title = rewrite.split('\n')[1]
        description = ''.join(rewrite.split('\n')[2:])
        seo = get_seo(title, description)
        post_category = "reddit" if is_post else "youtube"
        return sentiment, title, description, seo, post_category
    else:
        seo = get_seo(title='', description=rewrite)
        post_category = "introduction" if is_introduction else "comment"
        return rewrite, seo, post_category


def like_post(post_id, email):
    post_data = get_post_data(post_id)
    poster_email = post_data[0]
    while email == poster_email:
        email = get_random_user_email()
    url = f"https://app.circle.so/api/v1/posts/{post_id}/likes?user_email={email}"
    try:
        data = requests.post(url,headers=circle_headers)
    except Exception:
        time.sleep(10)
        data = requests.post(url,headers=circle_headers)
    if data.json()['message'] == "Post has been liked":
        print(data.json()['message'])
    else:
        print(data.json()['message'])
    return data.json()


# def get_post_data(post_id, community_id): bfetch el data mn el database di useless delwaty
#     """
#     This function fetches the post data from Circle API.
#     It returns the post data in JSON format.
#     """
#     url = f"https://app.circle.so/api/v1/posts/{post_id}?community_id={community_id}"
#     try:
#         response = requests.get(url, headers=circle_headers)
#     except Exception:
#         time.sleep(10)
#         response = requests.get(url, headers=circle_headers)
#     return response.json()


def comment_on_post(space_id, post_id, user_email, previous_openings=None):
    """
    This function comments on a post.
    It first fetches the post and then sends the post to GPT to get a comment.
    It then creates a comment on the post.
    """
    post_data = get_post_data(post_id)
    while user_email == post_data[0]:
        user_email = get_random_user_email()
    post_category = post_data[1]
    gender = get_gender(user_email)
    final_identity = gender[0][0]
    original_identity = gender[0][1]
    title = post_data[2]
    description = post_data[3]

    message = f"""
Title: {title}
Description: {description}
"""
    if post_category == "introduction":
        message = f"""
        This is a post of someone introducing himself to the tubiit hubs community , please write a comment that is related to the that DO NOT USE EMOJIES.
        Title: {title}
        Description: {description}
        """
    body = send_to_gpt(message=message, is_post=False, final_identity=final_identity, original_identity=original_identity, n=random.randint(10,70), previous_openings=previous_openings, post_id=post_id)[0]
    url = "https://app.circle.so/api/v1/comments?"
    payload = {"community_id": community_id,
               "space_id": space_id,
               "post_id": post_id,
               "body": body,
               "user_email": user_email}
    try:
        response = comment_with_no_api(email=user_email, post_id=post_id, comment=body)
        print("comment created with no api call")
        return body
    except Exception:
        response = requests.post(url, headers=circle_headers, data=payload)
    if response.status_code == 200:
        if response.json()['success'] == True:
            print("Comment Created")
            return body
    else:
        print("Comment Not Created")
        return None

def assign_comments(sen, needed_likes):
    sen = sen.lower().strip()
    if sen == "educational" or sen == "reference":
        return needed_likes * random.uniform(0.04, 0.07)
    elif sen == "question" or sen == "emotional":
        return needed_likes * random.uniform(0.12, 0.18)
    elif sen == "polls" or sen == "hot":
        return needed_likes * random.uniform(0.20, 0.30)
    else:
        return needed_likes * random.uniform(0.03, 0.08)
    

def remove_external_link(string_to_remove,text_to_scan):
    description_checker = text_to_scan.strip()[-abs(len(string_to_remove)):]
    if description_checker == string_to_remove:
        description = text_to_scan[:-abs(len(string_to_remove))]
        return description
    return text_to_scan


def check_image(link):
    global html
    try:
        extension = link.split('?')[0].split('.')[-1]
        valid_image_extensions = ['jpg','jpeg','tiff','png','gif','bmp']
        valid_video_extension = ['mp4', 'webm' ,'ogg']
        if extension in valid_image_extensions:
            response = requests.get(link)
            if response.status_code == 200:
                html.append(f"<img src={link}>")
                return True
        
        elif extension in valid_video_extension or link.lower().startswith('https://www.youtube.com/'):
            response = requests.get(link)
            if response.status_code == 200:
                html.append((
    "<iframe width='560' height='315' "
    f"src={link} "
    "frameborder='0' "
    "allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' "
    "allowfullscreen></iframe>"
    ))      
                return True
        return False
    except Exception as e:
        return False


def description_cleaner(description):
    global html
    links = []
    delimiters = [' ', '\n']
    start_index = description.find('https://preview')
    while start_index != -1:
        start_index = description.find('https://preview')
        if start_index == -1:
            break
        end_index = [description.find(x, start_index) for x in delimiters]
        value_to_remove = -1
        while value_to_remove in end_index:
            end_index.remove(value_to_remove)

        if end_index == []:
            end_index = [len(description)]
        
        link = description[start_index:(min(end_index))]
        links.append(link)
        description = ''.join(description.split(link))
    for x in links:
        check_image(x)
    return description


def create_post(space_id, email, html_to_add=[], is_youtube=False, title='', description='', external_link='', url='', link='', is_introduction=False, introduction_message=None):
    global html
    html = []
    original_title = title
    original_description = description
    description = description_cleaner(description)
    message = f"""
Title: '{title}'
Description: {description}
External_Link: {external_link}
"""
    html.extend(html_to_add)
    gender = get_gender(email)
    final_identity = gender[0][0]
    original_identity = gender[0][1]
    circle_url = "https://app.circle.so/api/v1/posts?"
    if external_link:
        description += external_link
    if is_youtube:
        message = f"""
Title: {title}
Transcript: {description}
Video Link: {link}
"""
        sen, title, description, seo, post_category = send_to_gpt(message=message, is_youtube=True, final_identity=final_identity, original_identity=original_identity, n=random.randint(100, 280), link=link)
        check_image(link)
    elif is_introduction:
        long = random.randint(0, 100)
        if long <= 80:
            lines = f"1 sentence only with a max of 12 words"
            long = random.randint(0, 100)
            if long >= 60:
                lines = f"{random.randint(1, 4)} lines"
        else:
            lines = f"{random.randint(5, 11)} lines"
        print(lines)
        description, seo, post_category = send_to_gpt(message=introduction_message, is_introduction=True, final_identity=final_identity, original_identity=original_identity, n=lines)
        sen = 'intro'
    else:
        sen, title, description, seo, post_category = send_to_gpt(message=message, is_post=True, final_identity=final_identity, original_identity=original_identity,n=random.randint(200, 500))
    payload = {
                "space_id": space_id,
                "community_id": os.getenv("COMMUNITY_ID"),
                "user_email": email,
                "slug": seo.get('slug'),
                "meta_title": seo.get('meta_title'),
                "opengraph_title": seo.get('opengraph_title'),
                "opengraph_description": seo.get('opengraph_description'),
                "meta_description": seo.get('meta_description'),
                "cover_image": "",
                "is_comments_enabled": True,
                "is_liking_enabled": True,
                "name": title,
                "body": description
            }

    if check_image(external_link) and external_link:
        description = remove_external_link(external_link, description)
        payload["body"] = description
        if is_youtube:
            payload["internal_custom_html"] = f''.join(f'{ht}\n' for ht in html)

    elif html:
        if is_youtube:
            payload["internal_custom_html"] = f''.join(f'{ht}\n' for ht in html)  

    if 'false' in (sen.lower().strip(), title.lower().strip(), description.lower().strip()):
        print('falsing')
        return 'false'
    try:
        response = requests.request("POST", circle_url, headers=circle_headers, data=payload)
    except Exception:
        time.sleep(10)
        response = requests.request("POST", circle_url, headers=circle_headers, data=payload)
    if response.status_code == 200:
        print("Post Created")
        data = response.json() 
        post_id = data['post']['id']
        needed_likes = random.randint(60, 400)
        try:
            needed_comments = floor(assign_comments(sen, needed_likes))
        except Exception:
            delete_url = f"https://app.circle.so/api/v1/posts/{post_id}?community_id={community_id}"
            response = requests.delete(delete_url, headers=circle_headers)
            print("Error during comment assignment")
            return "false"
        if is_youtube:
            description = f"""Note this is a Youtube video I will send the post Description + the Video Transcript return a comment that is related to the description and transcript
Post Description: {description}
************************************************************
Transcript: {original_description}
"""
        insert_post(email, original_title, original_description, title, description, post_id, space_id, url, needed_likes=needed_likes, needed_comments=needed_comments, post_category=post_category)
        try:
            like_with_no_api(email, post_id, remove=True)
        except Exception as e:
            print(f'error in mimick {e}')
            pass
        return "not false"