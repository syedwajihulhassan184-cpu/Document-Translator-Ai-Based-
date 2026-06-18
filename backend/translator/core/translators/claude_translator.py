import time
import anthropic
API_KEY='api-key'
def translate_chunk(chunk_text, source_lang, target_lang):
    client = anthropic.Anthropic(API_KEY)

import requests
import time

def fetch_with_retry(url, max_tries=3):
        for attempt in range(max_tries):
            try:
                response = requests.get(url)
                return response
            except requests.exceptions.ConnectionError as e:
                if attempt == max_tries - 1:
                     raise
                time.sleep(2 ** attempt)


