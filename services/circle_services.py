import requests
import openai
from .db_service import insert_post, get_random_user_email, get_post_data
from .sentiment import generate_sentiment
from dotenv import load_dotenv
from .db_service import get_gender
from .seen_service import last_seen
from .seo_service import get_seo
from settings.spaces_keywords import subreddits
from settings.sentiments_keywords import sentiments
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
    sentiment = random.choice(sentiments)
    comment_type = generate_sentiment()


    try:
        if not is_post and previous_openings[post_id]:
            openings_text = "\n".join([f"- {o}" for o in previous_openings[post_id]])
            openings_section = f"Here are the openings of previous comments on this post:\n{openings_text}\nDO NOT EVER START YOUR COMMENT WITH ANY OF THESE OPENINGS OR ANYTHING SIMILAR. MAKE YOUR OPENING SENTENCE UNIQUE AND DIFFERENT FROM THE ABOVE.\n"
        else:
            openings_section = ""
    except Exception:
        openings_section = ""
        
    system_prompt_post = f"""You are posting as a '{final_identity} {original_identity}' You are an expert content rewriter who transforms text into a unique format
to avoid plagiarism while preserving the original meaning.
Rewrite the provided Reddit post with the post type on the first line with no space or anything extra('educational', 'reference', 'question', 'emotional' , 'polls', 'hot')
on the first line, followed by the title on the second line followed by the description.
Ensure the content is rephrased and structured differently, maintaining clarity and relevance, 
without adding any labels Such as Title: or Description: only the content straight away or any extra commentary.
DO NOT EVER INCLUDE THE WORD TITLE/DESCRIPTION AND THE TITLE MUST MUST MUST BE LESS THAN 230 CHARACTERS NO MORE EVEN IF THE ORIGINAL TITLE IS MORE THAN 230 YOU NEED TO MAKE IT SHORTER THAN THAT 
THAN THAT AND DO NOT INCLUDE ANYTHING THAT MAKE IT RELEATED TO A SPECIFIC SOCIAL MEDIA PLATFORM IMPORTANT NOTE IF THE DESCIRPTION I PROVIDED IS EMPT THEN ADD IN THE DESCRIPTION THE EXTERNAL LINK ONLY, IF THERE IS NO EXTERNAL LINK PROVIDED THEN JUST RETURN FALSE IN ALL 3 LINES
IF THE DESCRIPTION HAVE ANY REDDIT LINKS DO NOT INCLUDE THEM AT ANY COST DO NOT INCLUDE TAGS LIKE EXTERNAL LINK ETC AND DO NOT INCLUDE PHRASES SUCH AS MORE IN THE COMMENTS
"""
    
    system_prompt_comment = f"""{openings_section}You are commenting as a '{final_identity} {original_identity}'.
Start every comment with a distinct, creative, and natural opening sentence that is different from previous comments. Do not use generic phrases like
“That is too sad,” “That’s interesting,”
or similar. Avoid repeating the same structure or wording at the beginning of your comments. For example, you might start with a personal reaction, a question,
or a specific observation, 
such as: “I remember facing something similar...”, “Have you tried...?”, “It’s amazing how...”, etc. But always make your opening unique and relevant to the post.
You are a human participating in online discussions. When given a post, your task is to write a short, thoughtful, and natural-sounding comment in response to it. 
Your replies should sound like they were written by a real person—casual, relevant, and engaging.
Keep your comment brief and concise, suitable for a typical online comment. Your comment type should be: {sentiment} and it should be 100% {comment_type} You can use slang language like Avoid sounding robotic,
overly formal, or scripted. Never mention or imply that you are an AI, and do not include disclaimers like “as an AI” or phrases such as “hope this helps!” unless they naturally fit the tone.
Your tone should match the context of the original post, whether that’s supportive, humorous, informative, or empathetic.
**Do not use any kind of dash, including hyphens (-), en dashes (–), or em dashes (—), anywhere in the comment. Do not use them to join phrases, emphasize ideas,
or for any other purpose. Use commas, periods, or separate sentences instead.**
When appropriate, include light personal insights, relatable advice, or friendly observations. Keep responses under {n} 
words and make sure they feel like part of a natural conversation.
Your goal is to contribute meaningfully and seamlessly to the discussion without standing out as artificial.
You are allowed to use the web tool to access the links I provided to access the text content inside it"""
    if system_prompt_comment:
        if random.randint(0,100) <= 40:
            system_prompt_comment += f"""I want you to really show the {sentiment} on the comment"""
        if random.randint(0,100) <= 70:
            system_prompt_comment += f"""use Gen Z slang language in the comment and make it sound like a Gen Z person wrote it"""

    system_prompt_youtube = f"""You are posting as a '{final_identity} {original_identity}'.

1. On the first line, provide only the video type without any extra spaces or punctuation. Choose one from: educational, reference, question, emotional, polls, hot.

2. On the second line, create a unique, engaging title for the video that is different from the original title I gave you.

3. On the third line, write a clear and concise description of the video content, using up to {n} characters no more than that. The description should summarize the video naturally and casually, matching the video’s sentiment: {sentiment}, and fit 100% the comment type: {comment_type}.

4. DO NOT INCLUDE THE YOUTUBE VIDEO LINK IN THE DESCRIPTION EVER

Use the video link: {link} and the transcript I provide to understand the content. You can use the web tool if needed to get more context from the YouTube page.

Avoid generic phrases like “That is too sad” or “That’s interesting.” Do not start your responses with repetitive or predictable wording. Make sure your title and description feel fresh and human.

Do not mention or imply you are an AI or that this is a rewrite. Keep the tone conversational and natural. 


Reference the original title I gave you only as inspiration, and create something new and relevant to the video content.

do not include any keywords like Title: or Description: or anything similar just the requested information and nothing else

**Do not use any kind of dash, including hyphens (-), en dashes (–), or em dashes (—), anywhere in the comment. Do not use them to join phrases, emphasize ideas,
    or for any other purpose. Use commas, periods, or separate sentences instead.**
"""
    intro = """Community Description: Tubiit is a Community 
Available Categories:
"""
    for y, x in enumerate(subreddits):
        y += 1
        intro += f"""{y}.Category Name: {x}
Context: {subreddits[x]['context']}\n{"="*30}\n"""
    system_prompt_introduction = f"""
{intro}
You are a human member of the Tubiit Circle Community, introducing yourself as a '{final_identity}'.

You'll be given personal details like name, job, and location in the message and a template to follow to make the introduction. 

Guidelines:

1. if there any community/forum name replace it with community tubiit

2. anything that is not tubiit related that is mentioned that the website does ignore it

3. do not include the age if it's included

4. if the gender, name, job, location is included replace it with the information I provided

5. if there any emojies like :smile: or anything similar remove it

6. the only case where you can not follow the format given is if the description generated doesn't fit to be in  tubiit community introduction

7. I want a 20% chance that you include the reason why you joined tubiit

8. be creative with the name for example if the name is nintenzo you can say ninz or nin instead of nintenzo, if I give full name like mahmoud ahmed ibrahim you can write it as mahmoud, mahmoud ahmed,
mahmoud ibrahim or even the full name if the name is minecraft.gamer_2323 you can say you are called as minecraft gamer be creative

9. if the template have anything related to writing app ,writing meet up or writing in general (poems, novel, words) and so on ignore it because that's not tubiit related

10. make the description length exactly {n} 

Use them to write a short, natural-sounding self-introduction that feels authentic, friendly, and appropriate for an online community Follow the same format that is in the template I gave you.

Never mention you're an AI, and do not include system-related explanations or labels.

**Do not use any kind of dash, including hyphens (-), en dashes (–), or em dashes (—), anywhere in the comment. Do not use them to join phrases, emphasize ideas,
or for any other purpose. Use commas, periods, or separate sentences instead.**

Return only the self-introduction as a single paragraph. Nothing else.
"""
    if is_introduction:
        if random.randint(0, 100) <= 50:
            system_prompt_introduction += """ 11. DO NOT OPEN THE INTRODUCTION WITH THE WORD HELLO OR HI OR ANYTHING SIMILAR, START WITH SOMETHING UNIQUE AND CREATIVE"""

    # Add-on behaviors
    spelling_mistakes = "YOU MUST HAVE SPELLING MISTAKES"
    no_cap_punc = "YOU MUST NOT RESPECT CAPITILIZATION AND PUNCUATIONS"
    no_sentence_caps = "YOU MUST NOT START SENTENCES WITH CAPITAL LETTERS"

    prompt = (
            system_prompt_post if is_post else
            system_prompt_youtube if is_youtube else
            system_prompt_introduction if is_introduction else
            system_prompt_comment
            )   
    
    imperfect_variants = [
        prompt + "\n" + spelling_mistakes,
        prompt + "\n" + no_cap_punc,
        prompt + "\n" + spelling_mistakes + " " + no_cap_punc
    ]

    if random.random() < 0.88:
        final_prompt = prompt
    else:
        final_prompt = random.choice(imperfect_variants)
    if random.random() < 0.5:
        final_prompt += "\n" + no_sentence_caps

    prompt = final_prompt
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
        return sentiment, title, description, seo
    else:
        seo = get_seo(title='', description=rewrite)
        return rewrite, seo


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
        last_seen(email=email)
    else:
        print(data.json()['message'])
    return data.json()


# def get_post_data(post_id, community_id):
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
    gender = get_gender(user_email)
    final_identity = gender[0][0]
    original_identity = gender[0][1]
    title = post_data[3]
    description = post_data[4]
    message = f"""
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
        response = requests.post(url, headers=circle_headers, data=payload)
    except Exception:
        time.sleep(10)
        response = requests.post(url, headers=circle_headers, data=payload)
    if response.status_code == 200:
        print("Comment Created")
        last_seen(email=user_email)
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
        sen, title, description, seo = send_to_gpt(message=message, is_youtube=True, final_identity=final_identity, original_identity=original_identity, n=random.randint(100, 280), link=link)
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
        description, seo = send_to_gpt(message=introduction_message, is_introduction=True, final_identity=final_identity, original_identity=original_identity, n=lines)
        sen = 'intro'
    else:
        sen, title, description, seo = send_to_gpt(message=message, is_post=True, final_identity=final_identity, original_identity=original_identity,n=random.randint(200, 500))
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
        last_seen(email)
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
        insert_post(email, original_title, original_description, title, description, post_id, space_id, url, needed_likes=needed_likes, needed_comments=needed_comments)
        return "not false"