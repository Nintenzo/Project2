from dotenv import load_dotenv
import os
import openai
load_dotenv()

def get_seo(title ,description):
    message = f"""
    Title: {title}
    Description: {description}
    """

    system_prompt = """You are an SEO assistant. Given a post title and description, generate the following 5 fields in this exact order:

1. slug — lowercase, hyphenated, URL-friendly
2. meta_title — max 60 characters
3. opengraph_title — suitable for social sharing
4. opengraph_description — engaging, social-media-friendly summary
5. meta_description — search-optimized summary (max 155 characters; may wrap to second line if needed)

Output each field on its own line. No labels, no extra text — only the 5 lines.
"""
    openai.api_key = os.getenv("GPT_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": message}
        ]
    )
    rewrite = response["choices"][0]["message"]["content"]
    slug = rewrite.split('\n')[0]
    meta_title = rewrite.split('\n')[1]
    opengraph_title = rewrite.split('\n')[2]
    opengraph_description = rewrite.split('\n')[3]
    meta_description = rewrite.split('\n')[4:]
    seo = {
        'slug': slug,
        'meta_title': meta_title,
        'opengraph_title': opengraph_title,
        'opengraph_description': opengraph_description,
        'meta_description': meta_description
        }
    return seo
