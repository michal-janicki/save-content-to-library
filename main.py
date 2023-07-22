#!/usr/bin/env python3

import argparse
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Environment variables
MODEL = os.getenv('OPENAI_MODEL')
MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS'))
TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_URL = os.getenv('OPENAI_API_URL')
GET_CONTENT_API_URL = os.getenv('GET_CONTENT_API_URL')
GET_CONTENT_API_KEY = os.getenv('GET_CONTENT_API_KEY')
GET_CONTENT_API_KEY_HEADER = os.getenv('GET_CONTENT_API_KEY_HEADER')
SAVE_CONTENT_API_URL = os.getenv('SAVE_CONTENT_API_URL')
SAVE_CONTENT_API_KEY = os.getenv('SAVE_CONTENT_API_KEY')
SAVE_CONTENT_API_KEY_HEADER = os.getenv('SAVE_CONTENT_API_KEY_HEADER')
SYSTEM_PROMPT = os.getenv('OPENAI_SYSTEM_PROMPT')
INSTRUCTION = os.getenv('OPENAI_INSTRUCTION')


def get_ai_completion(data):
    """
    Returns a completion using OpenAI's GPT-4 model
    """
    text = data['text']
    print(f"system prompt:\n{SYSTEM_PROMPT}")
    print(f"user instruction:\n{INSTRUCTION}")

    user_message = {
        'role': 'user',
        'content': f'{INSTRUCTION}\n\n{text}'
    }
    system_message = {
        'role': 'system',
        'content': SYSTEM_PROMPT
    }

    messages = [system_message, user_message]
    options = {
        'model': MODEL,
        'max_tokens': MAX_TOKENS,
        'temperature': TEMPERATURE,
        'messages': messages,
        'stream': False,
        'stop': ["---"]
    }

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(options))
    response.raise_for_status()

    return response.text


def get_web_content(parameter):
    """
    Get content from the specified URL
    """
    url = f"{GET_CONTENT_API_URL}?url={parameter}"

    headers = {f"{GET_CONTENT_API_KEY_HEADER}": GET_CONTENT_API_KEY}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.text


def save_web_content(content):
    """
    Save content to a specified location
    """
    url = SAVE_CONTENT_API_URL

    headers = {f"{SAVE_CONTENT_API_KEY_HEADER}": SAVE_CONTENT_API_KEY}

    response = requests.post(url, headers=headers, json=content)
    response.raise_for_status()

    return response.text


def extract_data(api_response):
    """
    Extracts required data from the API response.
    """
    data = json.loads(api_response)['choices'][0]['message']['content']

    return json.loads(data)


def non_empty_string(s):
    """Ensures the input string is not empty"""
    if not s:
        raise argparse.ArgumentTypeError("The argument provided cannot be an empty string")
    return s


def main():
    parser = argparse.ArgumentParser(description="Send a GET request with a parameter")
    parser.add_argument("parameter", help="The parameter to send in the GET request", type=non_empty_string)

    args = parser.parse_args()
    url = args.parameter
    print(f"Received url: {url}")
    response = get_web_content(url)
    raw_data = json.loads(response)

    print(f"Parsed text with title: {raw_data['title']}")

    ai_result = get_ai_completion(raw_data)

    print(f"Received ai response:\n{ai_result}")

    ai_data = extract_data(ai_result)
    print(f"Extracted ai response:\n{ai_data}")
    content = {
        'url': url,
        'title': raw_data['title'],
        'text': raw_data['text'],
        'summary': ai_data['summary'],
        'categories': ai_data['categories'],
    }
    save_web_content(content)

    print("SUCCESS")


if __name__ == "__main__":
    main()
