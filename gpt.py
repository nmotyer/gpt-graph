import openai
import orjson
import os
from enum import Enum

class ModeEnum(Enum):
    DATA = 1
    GRAPH = 2

class gpt:
    def __init__(self, mode: ModeEnum):
        self.model = 'gpt-3.5-turbo'
        self.mode = mode
        self.messages = get_starting_prompts(self.mode)
        self.get_api_secret()

    def prompt(self, prompt:str, use_chat_history: bool = True) -> str:
        self.messages.append([{'role': 'user', 'content': prompt}])
        response = self._query(self.messages if use_chat_history else self.messages[-1])
        self.messages.append({'role': 'assistant', 'content': response.choices[0].message['content']})
        return response.choices[0].message['content']

    def _query(self, messages: list[dict]) -> dict:
        return openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    # stream
                )

    def _set_mode(self):
        return

    def get_api_secret(self):
        try:
            with open('credentials.json', 'r') as cbytes:
                creds = orjson.loads(cbytes.read())['key']
        except IOError:
            pass
        openai.api_key = os.environ.get("OPENAI_API_KEY", creds)
        return

def get_starting_prompts(mode: ModeEnum) -> list[dict]:
    if mode.DATA:
        return [{
            'role': 'system', 
            'content': 'you are an assistant that helps generate sql to retrieve data. you return code only. do not provide notes'
                }]
    elif mode.GRAPH:
        return [{
            'role': 'system', 
            'content': 'you are an assistant that helps generate code to retrieve and display data. you return all code in <script> tags'
                }]
    return [{}]
