from dotenv import load_dotenv
import requests
import time
import os
import logging
from openai import OpenAI
import openai

load_dotenv()
AI_API_KEY = os.getenv("AI_API_KEY")

logger = logging.getLogger(__name__)


def translate_chunk(chunk_text, source_lang, target_lang):
    if not target_lang and not chunk_text:
        raise ValueError('Target language aand chunk text is required!')

    client = OpenAI(
        api_key=AI_API_KEY,
        base_url="https://api.deepseek.com"
    )
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role":"system", "content": f"""Translate this from {source_lang} to {target_lang} just return the
                        translated text i dont want any extra text exact translated text now translate this"""},
    
                    {"role": "user","content": chunk_text}
                ],
                max_tokens=1024,
            )

            logger.info(f"Input token: {response.usage.prompt_tokens}")
            logger.info(f"Output Tokens: {response.usage.completion_tokens}")
            return response.choices[0].message.content
    
        except openai.RateLimitError as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)