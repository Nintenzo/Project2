import requests
import random
from bs4 import BeautifulSoup

def get_intro_template():
    try:
        link = f'https://www.writingforums.com/forums/introduce-yourself.12/page-{random.randint(1, 506)}'
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        thread_list = soup.find_all(class_='structItem-title')
        threads_link = []
        for x in thread_list[1:]:
            try:
                link = x.find('a')
                if link:
                    threads_link.append(f"https://www.writingforums.com{link['href']}")
            except Exception:
                pass
        link = random.choice(threads_link)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        intro_template = soup.find(class_='bbWrapper').text
        return intro_template
    except Exception:
        print('No Template')
        return "No Intro Template Please generate one Yourself"