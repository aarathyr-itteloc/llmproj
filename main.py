import argparse
import os
import json

from call_function import available_functions, call_function
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt


def generate_content(client, messages):
    return client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
    )

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    for _ in range(20):
        response = generate_content(client,messages)
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            if response.usage.prompt_tokens != None and response.usage.completion_tokens != None:
                print(f"Prompt tokens: {response.usage.prompt_tokens}")
                print(f"Response tokens: {response.usage.completion_tokens}")
        message = response.choices[0].message
        messages.append(message)
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_args = json.loads(tool_call.function.arguments or "{}")
                result_message =call_function( tool_call , function_args)
                if not result_message.get("content"):
                    raise Exception(f"Empty content returned by {tool_call.function.name}")
                if args.verbose:
                    print(f"-> {result_message['content']}")
                messages.append(result_message)
        else:
            print(response.choices[0].message.content)
            return
    exit(1)
main()
