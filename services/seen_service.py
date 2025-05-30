from services.db_service import get_user_password
import cloudscraper

# def last_seen(email):  el seen keda keda bit3ml automatic m3 el likes w comments f di useless bardo
#     try:
#         remember_user_token, user_session_identifier = fresh_cookies(email)
#         url = "https://tubiit.circle.so/feed"
#         cookies = {
#             "remember_user_token": remember_user_token,
#             "user_session_identifier": user_session_identifier,
#         }
#         try:
#             requests.get(url, cookies=cookies)
#         except Exception:
#             time.sleep(10)
#             requests.get(url, cookies=cookies)
#         time.sleep(2)
#         print("last seen mimicked")
#         return
#     except Exception:
#         pass


def fresh_cookies(email):
    pw = get_user_password(email)[0]
    payload = {
        "user": {
            "email": email,
            "password": pw,
            "community_id": ""
        },
        "source": None,
        "chat_bot_session_id": ""
    }
    login_url = "https://login.circle.so/sign_in?"

    scraper = cloudscraper.create_scraper()
    try:
        scraper.headers.update({
            "accept": "application/json"
        })
        resp = scraper.post(login_url, json=payload)
        try:
            if resp.status_code != 200 or 'redirect_url' not in resp.json():
                print("Login failed or bad response")
                print(resp.text)
                return {}
            redirect_url = resp.json()['redirect_url']
            redirect_resp = scraper.get(redirect_url)
            cookies = scraper.cookies.get_dict()
            return cookies
        finally:
            resp.close()
            if 'redirect_resp' in locals():
                redirect_resp.close()
    finally:
        scraper.close()
