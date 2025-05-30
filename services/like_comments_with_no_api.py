import tls_client
from services.seen_service import fresh_cookies


def like_with_no_api(email, post_id, remove=False):
    cookies = fresh_cookies(email)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://tubiit.circle.so/",
        "Origin": "https://tubiit.circle.so",
        "Content-Type": "application/json"
    }

    session = tls_client.Session(client_identifier="chrome_120")

    response = session.post(
        "https://tubiit.circle.so/user_likes?",
        headers=headers,
        cookies=cookies,
        json={
            "user_likeable_type": "Post",
            "user_likeable_id": post_id
        }
    )

    if remove:
        response = session.delete(
			"https://tubiit.circle.so/user_likes?",
			headers=headers,
			cookies=cookies,
			json={
				"user_likeable_type": "Post",
				"user_likeable_id": post_id
			}
		)
    if response.status_code == 200:
        return 'Post has been liked'
    else:
        raise Exception('post not liked')


def comment_with_no_api(email, post_id, comment):
    cookies = fresh_cookies(email)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://tubiit.circle.so/",
        "Origin": "https://tubiit.circle.so",
        "Content-Type": "application/json"
    }
    session = tls_client.Session(client_identifier="chrome_120")
    response = session.post(
        f"https://tubiit.circle.so/internal_api/posts/{post_id}/comments?",
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
        return 'ok'
    else:
        raise Exception('comment not posted')