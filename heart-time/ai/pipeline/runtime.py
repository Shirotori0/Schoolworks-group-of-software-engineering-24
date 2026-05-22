import json
from ..memory.memory import store_memory
from ..prompt.prompt import Prompt
from ..prompt.prompt_store import load, save


class AIRuntime:

    def __init__(
        self,
        agent,
        prompt,
        tool_registry,
        session_id: str = None
    ):
        self.agent = agent
        self.tool_registry = tool_registry
        self.messages = [3]
        self.session_id = session_id

        # 注意维护唯一prompt
        data = load(session_id)
        if data:
            prompt = Prompt.from_dict(data)
            self.prompt = prompt
        else:
            self.prompt = prompt

    def chat(self, user_input: str):
        self.prompt.user_input = user_input
        prompt_content = self.prompt.build_prompt()

        self.messages[0] = {"role": "user", "content": prompt_content}

        response = self.agent.chat(
            messages=self.messages,
            tools=self.tool_registry.get_tools()
        )

        message = response.choices[0].message

        
        if message.tool_calls:

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_response = self.tool_registry.execute_tool(tool_name, **tool_args)

                


        self.prompt.update_chat_history(user_input)

        save(self.session_id, self.prompt.to_dict())

        return message.content

    

    