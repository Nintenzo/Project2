from settings.sgid import sgid
import requests
import random

def get_sgid(name):
    try:
        data = requests.get(f"https://www.tubiithubs.com/internal_api/search/advanced_search?query={name}&per_page=1")
        string = data.json()['records'][0]['sgid']
        return string
    except Exception:
        return random.choice(sgid)