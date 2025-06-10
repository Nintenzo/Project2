import os
from dotenv import load_dotenv
import openai
import openai.error
load_dotenv()

def send_prompt(system_prompt, message, model):
    openai.api_key = os.getenv("GPT_KEY")
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                    },
                {"role": "user", "content": message}
            ]
        )
    except openai.error.RateLimitError:
        print("Quota exceeded. Check your usage and billing.")
        return "quota"
    
    return response["choices"][0]["message"]["content"]