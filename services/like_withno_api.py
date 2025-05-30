import tls_client
from services.db_service import get_user_password
from services.seen_service import last_seen
import cloudscraper

def fresh_cookies(email):
	pw = get_user_password(email)[0]
	payload = {
		"user": {
			"email": email,
			"password": pw,
			"community_id": ''
		},
		"source": None,
		"chat_bot_session_id": ""
	}
	login_url = "https://login.circle.so/sign_in?"

	scraper = cloudscraper.create_scraper()
	scraper.headers.update({
		"accept": "application/json"
	})
	resp = scraper.post(login_url, json=payload)
	if resp.status_code != 200 or 'redirect_url' not in resp.json():
		print("Login failed or bad response")
		print(resp.text)
		return {}
	redirect_url = resp.json()['redirect_url']
	scraper.get(redirect_url)
	return scraper.cookies.get_dict()


def like_withno_api(email, post_id):
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
    if response.status_code == 200:
        last_seen(email=email)
        return 'Post has been liked'
    else:
        return Exception('post not liked')
