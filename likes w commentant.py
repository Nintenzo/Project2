from services.db_service import fetch_posts, get_random_user_email, decrement_likes_comments
from services.until4am import sleep_until_4am
from services.circle_services import like_post, comment_on_post
from services.like_comments_with_no_api import like_with_no_api
import random
import time
from pympler.asizeof import asizeof
from datetime import datetime
import gc

def extract_opening(text, num_words=10):
    if not text:
        return ""
    sentence = text.split('.')
    if sentence:
        opening = sentence[0].strip()
        if len(opening.split()) > num_words:
            return ' '.join(opening.split()[:num_words])
        return opening
    return ' '.join(text.split()[:num_words])


def like_comment_sum(posts):
    total_likes = 0
    total_comments = 0
    for post in posts:
        total_likes += post[2]
        total_comments += post[3]
    total_interactions = total_likes + total_comments
    hour = (sleep_until_4am() / 60 / 60 )
    total_time_seconds = hour * 60 * 60
    average_sleep_time = total_time_seconds // total_interactions
    percentage = random.uniform(-0.3, 0.3)
    average_sleep_time = int(average_sleep_time * (1 + percentage))
    return average_sleep_time

previous_openings = {}
CAP = 128_000_000
while True:
    try:
        posts = fetch_posts()
        if len(posts) >= 1:
            average_sleep_time = like_comment_sum(posts)
            for x in random.sample(posts, len(posts)):
                if asizeof(previous_openings) > CAP:
                    previous_openings = {}
                print(average_sleep_time)
                email = get_random_user_email()
                print('emailed changed')
                post_id = x[0]
                space_id = x[1]
                needed_likes = x[2]
                needed_comments = x[3]
                try:
                    response = like_with_no_api(email, post_id)
                    if response == 'Post has been liked':
                        print('post has been liked with no api call')
                        time.sleep(1)
                        pass
                except Exception as e:
                    print(e)
                    response = like_post(post_id, email)
                    if response['message'] == "Oops! couldn't find the post you requested.":
                        continue
                    while response['message'] != "Post has been liked":
                        email = get_random_user_email()
                        response = like_post(post_id, email)
                        time.sleep(1)
                decrement_likes_comments(post_id, "needed_likes")
                needed_likes -= 1
                if needed_comments >= 1:
                    if random.randint(0, 100) <= 30:
                        email = get_random_user_email()
                    if random.randint(0, 100) <= 20:
                        continue
                    comment_body = comment_on_post(space_id, post_id, email, previous_openings=previous_openings)
                    if comment_body:
                        opening = extract_opening(comment_body)
                        if post_id not in previous_openings:
                            previous_openings[post_id] = []
                        previous_openings[post_id].append(opening)
                    decrement_likes_comments(post_id, "needed_comments")
                    time.sleep(average_sleep_time)
                    continue
                decrement = 0
                while needed_comments <= 0 and needed_likes >= 1:
                    print(f"Likes left: {needed_likes}")
                    email = get_random_user_email()
                    try:
                        response = like_with_no_api(email, post_id)
                        if response == 'Post has been liked':
                            print('post has been liked with no api call')
                            time.sleep(1)
                            pass
                    except Exception as e:
                        response = like_post(post_id, email)
                        if response['message'] == "Oops! couldn't find the post you requested.":
                            break
                        while response['message'] != "Post has been liked":
                            email = get_random_user_email()
                            response = like_post(post_id, email)
                            gc.collect()
                            time.sleep(1)
                    decrement += 1
                    needed_likes -= 1
                    gc.collect()
                    if decrement >= 50:
                        decrement_likes_comments(post_id, "needed_likes", decrement=decrement)
                        decrement = 0
                if decrement > 0:
                    decrement_likes_comments(post_id, "needed_likes", decrement=decrement)
                    #needed_likes = fetch_post_byID(post_id)[0] bn3ml track lel likes localy f di useless nek
            gc.collect()
                
        else:
            previous_openings = {}
            print(datetime.now())
            time.sleep(3600)
    except Exception as e:
        print(e)
        time.sleep(10)
        