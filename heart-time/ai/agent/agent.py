import os
from openai import OpenAI

class Agent:
    def __init__(self):
        self.client = OpenAI(
            api_key="",#这里写自己的api key，获取方法有问题，待修复  
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-v4-pro"

    def chat(self, messages, stream=False, reasoning_effort="high"):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            reasoning_effort=reasoning_effort,
            extra_body={"thinking": {"type": "enabled"}}
        )
        return response


