import json
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import os

GPT_MODEL = "gpt-3.5-turbo-0613"
openai.api_key = os.environ['OPENAI_API_KEY']

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_workout",
            "description": "Add a new workout to a players schedule",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "string",
                        "description": "The start date and time of the workout, e.g. 2023-11-19T22:12:49-05:00",
                    },
                    "end": {
                        "type": "string",
                        "description": "The end date and time of the workout, e.g. 2023-11-19T22:12:49-05:00",
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the workout",
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the workout",
                    },
                    "intensity": {
                        "type": "string",
                        "enum": ["recovery", "low", "maintenance", "high", "extreme"],
                        "description": "The intensity of the workout",
                    },
                },
                "required": ["start", "end", "name", "intensity"],
            },
        }
    }
]


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "Please create a new workout, start date will be 2023-11-19T22:12:49-05:00, the end date will be 2023-11-19T22:12:49-05:00, the intensity will be high, call it Long Run"})
chat_response = chat_completion_request(
    messages, tools=tools
)
assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)
pretty_print_conversation(messages)
print(chat_response.json()["choices"][0])

