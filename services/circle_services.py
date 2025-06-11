from services.like_comments_with_no_api import comment_with_no_api, like_with_no_api
from .db_service import insert_post, get_random_user_email, get_post_data
from settings.cathmart_products import cathmart_products
from settings.system_prompts import get_system_prompt
from services.openai_services import send_prompt
from settings.tubiit_surgeries import surgeries
from .db_service import get_member_info
from .seo_service import get_seo
from dotenv import load_dotenv
from math import floor
import requests
import markdown
import random
import time
import json
import os

load_dotenv()
circle_key = os.getenv("CIRCLE_API")
circle_headers = {
    'Authorization': f'Token {circle_key}'
}
community_id = os.getenv("COMMUNITY_ID")
days = 10

def send_to_gpt(name, message, final_identity, original_identity, is_inappropriate=False, author_gender=None, is_youtube=False, is_post=False, n=30,
                previous_openings=None, link=None, post_id=None, is_introduction=False, is_cathmart_post=False, is_cathmart_comment=False,
                is_tubiit_post=False, is_tubiit_comment=False, model="gpt-4o-mini"):
    system_prompt = get_system_prompt(
        is_tubiit_comment=is_tubiit_comment,
        is_cathmart_comment=is_cathmart_comment,
        is_cathmart_post=is_cathmart_post,
        is_tubiit_post=is_tubiit_post,
        author_gender=author_gender,
        final_identity=final_identity,
        original_identity=original_identity,
        is_youtube=is_youtube,
        is_post=is_post,
        n=n,
        previous_openings=previous_openings,
        link=link,
        post_id=post_id,
        is_introduction=is_introduction,
        name=name,
        is_inappropriate=is_inappropriate
    )

    rewrite = send_prompt(system_prompt=system_prompt, message=message, model=model)
    while rewrite == "quota":
        time.sleep(3600)
        rewrite = send_prompt(system_prompt=system_prompt, message=message)
    if is_post or is_youtube or is_inappropriate or is_cathmart_post or is_tubiit_post:
        sentiment = rewrite.strip().split('\n')[0]
        title = rewrite.strip().split('\n')[1]
        description = ''.join(rewrite.strip().split('\n')[2:])
        seo = get_seo(title, description)
        post_category = ("reddit" if is_post else 
                         "inappropriate" if is_inappropriate else
                         "cathmart" if is_cathmart_post else
                         "tubiit" if is_tubiit_post else
                         "youtube")
        
        return sentiment, title, description, seo, post_category
    # elif is_inappropriate:
    #     sentiment = rewrite.split('\n')[0]
    #     title = rewrite.split('\n')[1]
    #     description = ''.join(rewrite.split('\n')[2:])
    #     seo = get_seo(title, description)
    #     post_category = "inappropriate"
    #     return sentiment, title, description, seo, post_category
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
    author_data = get_member_info(post_data[0])
    author_gender = f"Final Identity: {author_data[0][1]} Birth Identity: {author_data[0][2]}"
    post_category = post_data[1]
    member_data = get_member_info(user_email)
    name = member_data[0][0]
    final_identity = member_data[0][1]
    original_identity = member_data[0][2]
    role = member_data[0][3]
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
    if post_category == "cathmart":
        body = send_to_gpt(
            model="gpt-4.1-nano",
            is_cathmart_comment=True,
            author_gender=author_gender,
            name=name,
            message=message,
            is_post=False,
            final_identity=final_identity,
            original_identity=original_identity,
            n=random.randint(1, 70),
            previous_openings=previous_openings,
            post_id=post_id
        )[0]
    elif post_category == "tubiit":
        body = send_to_gpt(
            model="gpt-4.1-nano",
            is_tubiit_comment=True,
            author_gender=author_gender,
            name=name,
            message=message,
            is_post=False,
            final_identity=final_identity,
            original_identity=original_identity,
            n=random.randint(1, 70),
            previous_openings=previous_openings,
            post_id=post_id
        )[0]
    else:
        body = send_to_gpt(
            model="gpt-4.1-nano",
            author_gender=author_gender,
            name=name,
            message=message,
            is_post=False,
            final_identity=final_identity,
            original_identity=original_identity,
            n=random.randint(1, 70),
            previous_openings=previous_openings,
            post_id=post_id
        )[0]
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

def assign_comments(sen, likes):
    global needed_likes
    needed_likes = likes
    sen = sen.lower().strip()
    if sen == "educational" or sen == "reference":
        return needed_likes * random.uniform(0.04, 0.07)
    elif sen == "question" or sen == "emotional":
        return needed_likes * random.uniform(0.12, 0.18)
    elif sen == "polls" or sen == "hot":
        return needed_likes * random.uniform(0.20, 0.30)
    else:
        needed_likes = random.randint(30, 150)
        return needed_likes * random.uniform(0.03, 0.08)
    
def remove_external_link(string_to_remove, text_to_scan):
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
    to_remove = ["https://preview", "https://imgur", " https://i.imgur"]
    for x in to_remove:
        start_index = description.find(x)
        while start_index != -1:
            start_index = description.find(x)
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


def create_post(space_id, email, html_to_add=[], is_youtube=False, title='', description='', external_link='', url='', link='', is_introduction=False,
                is_inappropriate=False, introduction_message=None, post_thumbnail=False, is_cathmart_post=False, is_tubiit_post=False):
    global html, needed_likes
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
    member_data = get_member_info(email)
    name = member_data[0][0]
    final_identity = member_data[0][1]
    original_identity = member_data[0][2]
    role = member_data[0][3]
    circle_url = "https://app.circle.so/api/v1/posts?"
    if external_link:
        description += external_link
    if is_youtube and not any([is_inappropriate, is_cathmart_post, is_tubiit_post]):
        message = f"""
    Title: {title}
    Transcript: {description}
    Video Link: {link}
    """
        sen, title, description, seo, post_category = send_to_gpt(
            name=name,
            message=message,
            is_youtube=True,
            final_identity=final_identity,
            original_identity=original_identity,
            n=random.randint(100, 280),
            link=link
        )
        check_image(link)

    elif is_introduction:
        long = random.randint(0, 100)
        if long <= 80:
            lines = "1 sentence only with a max of 12 words"
            long = random.randint(0, 100)
            if long >= 60:
                lines = f"{random.randint(1, 4)} lines"
        else:
            lines = f"{random.randint(5, 11)} lines"

        description, seo, post_category = send_to_gpt(
            name=name,
            message=introduction_message,
            is_introduction=True,
            final_identity=final_identity,
            original_identity=original_identity,
            n=lines
        )
        sen = 'intro'

    elif is_inappropriate:
        sen, title, description, seo, post_category = send_to_gpt(
            model="gpt-4o",
            is_inappropriate=True,
            name=name,
            message=message,
            final_identity=final_identity,
            original_identity=original_identity
        )

    elif is_cathmart_post:
        item = random.choice(cathmart_products)
        message = f"""Author Gender: {final_identity} {original_identity}
Product: {item}"""
        sen, title, description, seo, post_category = send_to_gpt(
            is_cathmart_post=True,
            name=name,
            message=message,
            final_identity=final_identity,
            original_identity=original_identity
        )

    elif is_tubiit_post:
        type = random.choice(surgeries)
        message = f"""Gender: {final_identity} {original_identity}
type: {type}"""
        sen, title, description, seo, post_category = send_to_gpt(
            is_tubiit_post=True,
            name=name,
            message=message,
            final_identity=final_identity,
            original_identity=original_identity,
            n=random.randint(30, 200)
        )
    else:
        sen, title, description, seo, post_category = send_to_gpt(
            name=name,
            message=message,
            is_post=True,
            final_identity=final_identity,
            original_identity=original_identity,
            n=random.randint(200, 500)
        )
    
    html_output = markdown.markdown(description)
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
                "internal_custom_html": html_output
            }
    
    if check_image(external_link) and external_link:
        description = remove_external_link(external_link, description)
        html_output = markdown.markdown(description)
        payload["internal_custom_html"] = f"{html_output}\n"
    elif html:
        payload["internal_custom_html"] = f"{html_output}\n"

    if is_youtube:
        payload["internal_custom_html"] += f''.join(f'{ht}\n' for ht in html)
            
    if not title:
        payload["body"] = description
        payload["internal_custom_html"] = ""
        
    if description == external_link and external_link.strip().startswith('http'):
        payload["internal_custom_html"] = f"<a href={external_link}>{external_link}</a>"
        if post_thumbnail:
            payload["internal_custom_html"] += post_thumbnail

    # if 'false' in (sen.lower().strip(), title.lower().strip(), description.lower().strip()):
    #     print('falsing')
    #     return 'false'
    
    try:
        response = requests.request("POST", circle_url, headers=circle_headers, data=payload)
    except Exception:
        time.sleep(10)
        response = requests.request("POST", circle_url, headers=circle_headers, data=payload)
        
    if response.status_code == 200:
        print("Post Created")
        data = response.json() 
        post_id = data['post']['id']     

        if random.randint(0, 100) <= 10:
            needed_likes = random.randint(0, 100)
        else:
            needed_likes = random.randint(400, 1050)

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
            
        split_likes = needed_likes // days
        split_comments = needed_comments // days
        likes_arr = []
        comments_arr = []
        for x in range(days):
            likes_arr.append(split_likes)
            comments_arr.append(split_comments)
        needed_likes = json.dumps(likes_arr)
        needed_comments = json.dumps(comments_arr)
        insert_post(email, original_title, original_description, title, description, post_id, space_id, url, needed_likes=needed_likes, needed_comments=needed_comments, post_category=post_category)
        try:
            like_with_no_api(email, post_id, remove=True)
        except Exception as e:
            print(f'error in mimick {e}')
            pass
        return "not false"