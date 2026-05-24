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

        messages = [{"role": "user", "content": self.prompt.build_prompt()}]

        response = self.agent.chat(
            messages=messages,
            tools=self.tool_registry.get_tools()
        )

        message = response.choices[0].message

        
        if message.tool_calls:

            tool_responses = []

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_responses.append({tool_name: self.tool_registry.execute_tool(tool_name, **tool_args)})

            for tool_response in tool_responses:
                if tool_response.get("Retrieve_Context"):
                    self.prompt.rag_retrievals.extend(tool_response["Retrieve_Context"])

                    messages = [{"role": "user", "content": self.prompt.build_prompt()}]
                    response = self.agent.chat(
                        messages=messages,
                        tools=self.tool_registry.get_tools()
                    )
                    message = response.choices[0].message

                    if message.tool_calls:
                        tool_responses = []
                        for tool_call in message.tool_calls:
                            if tool_call.function.name != "Retrieve_Context":
                                tool_name = tool_call.function.name
                                tool_args = json.loads(tool_call.function.arguments)

                                self.tool_registry.execute_tool(tool_name, **tool_args)
                                

        self.prompt.update_chat_history(user_input)

        save(self.session_id, self.prompt.to_dict())

        return message.content

    

    