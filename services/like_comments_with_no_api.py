import tls_client
import random
from services.seen_service import fresh_cookies
from services.sgid_service import get_sgid
from services.db_service import get_random_user_email
import os
from dotenv import load_dotenv

load_dotenv()
base_link = os.getenv("COMMUNITY_LINK")
def like_with_no_api(email, post_id, remove=False):
    cookies = fresh_cookies(email)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": base_link,
        "Origin": base_link,
        "Content-Type": "application/json"
    }

    session = tls_client.Session(client_identifier="chrome_120")

    response = session.post(
        f"{base_link}/user_likes?",
        headers=headers,
        cookies=cookies,
        json={
            "user_likeable_type": "Post",
            "user_likeable_id": post_id
        }
    )

    if remove:
        response = session.delete(
			f"{base_link}/user_likes?",
			headers=headers,
			cookies=cookies,
			json={
				"user_likeable_type": "Post",
				"user_likeable_id": post_id
			}
		)
    if response.status_code == 200:
        session.close()
        return 'Post has been liked'
    else:
        session.close()
        raise Exception('post not liked')


def comment_with_no_api(email, post_id, comment, mention=False):
    cookies = fresh_cookies(email)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": f"{base_link}/",
        "Origin": base_link,
        "Content-Type": "application/json"
    }
    session = tls_client.Session(client_identifier="chrome_120")
    if mention:
        name = get_random_user_email(column_name="name")
        sgid = get_sgid(name)
        comment = f" {comment}"
    else:
        sgid = ""
    response = session.post(
        f"{base_link}/internal_api/posts/{post_id}/comments?",
        headers=headers,
        cookies=cookies,
        json={
            "comment": {
                "tiptap_body": {
                    "body": {
                        "type": "doc",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "mention",
                                        "attrs": {
                                            "sgid": sgid
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": comment
                                    }
                                ]
                            }
                        ]
                    }
                    }
                }
            }
        
    )
    if response.status_code == 201:
        session.close()
        return 'ok'
    else:
        session.close()
        raise Exception('comment not posted')