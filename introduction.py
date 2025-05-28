from services.db_service import fetch_introduction, update_introduction
from services.intro_template_fetcher import get_intro_template
from services.circle_services import create_post
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import schedule

load_dotenv()
introduction_space_id = os.getenv('INTRODUCTION_SPACE_ID')
def main():
    print(datetime.now())
    data = fetch_introduction()
    if data:
        ready_members = set()
        for x in data:
            dt_object = datetime.strptime(x[4], "%Y-%m-%d")
            if dt_object <= datetime.now():
                ready_members.add(x) 
        del data
        if ready_members:
            total_time_seconds = 19 * 60 * 60
            avg_sleep_time = total_time_seconds // len(ready_members)
            
            for x in ready_members:
                email = x[0]
                name = x[1]
                job = x[2]
                location = x[3]
                template = get_intro_template()
                message = f"""
Name: {name}
Job: {job}
Location: {location}
Introduction Template: {template}
"""
                create_post(space_id=introduction_space_id, email=email, is_introduction=True, introduction_message=message)
                update_introduction(email)
                print(avg_sleep_time)
                time.sleep(avg_sleep_time)
            print(datetime.now())
            print('Completed waiting for the next day')
        else:
            print('No member turns today')

schedule.every().day.at("04:00").do(main)

while True:
    schedule.run_pending()
    time.sleep(60)