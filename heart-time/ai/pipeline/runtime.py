import json
from ..prompt.prompt import Prompt
from ..prompt.prompt_store import load, save
from ..prompt.script import load_script, save_script

from ..utils.load_file import textLoader

class AIRuntime:

    def __init__(
        self,
        agent,
        prompt,
        tool_registry,
        session_id: str,
        script_path: str = None
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

        if script_path:
            self.prompt.script = load_script(script_path)    

        

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

            ## 处理工具调用，执行工具并保存结果
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_responses.append({tool_name: self.tool_registry.execute_tool(tool_name, **tool_args)})

            ## 处理工具调用结果，如果有检索结果，更新prompt并重新生成回复
            for tool_response in tool_responses:
                if tool_response.get("Retrieve_Context"):
                    self.prompt.update_retrieval_history(tool_response["Retrieve_Context"])

                    messages = [{"role": "user", "content": self.prompt.build_prompt()}]
                    response = self.agent.chat(
                        messages=messages,
                        tools=self.tool_registry.get_tools()
                    )
                    message = response.choices[0].message

                    ## 注意：如果工具调用后重新生成回复，可能会再次调用工具，形成循环。这里简单处理为只允许一次工具调用后的回复生成，实际应用中需要更复杂的状态管理来避免无限循环。
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


    def make_script(self, file_path: str, user_input: str):
        text = textLoader.load(file_path)

        self.prompt.user_input = user_input
        prompt_to_script = self.prompt.build_script(text)

        response = self.agent.chat(
            messages=[{"role": "user", "content": prompt_to_script}],
            tools=self.tool_registry.get_tools()
        )
        message = response.choices[0].message

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                self.tool_registry.execute_tool(tool_name, **tool_args)

    def chat_cosplay(self, user_input: str):
        self.prompt.user_input = user_input

        messages = [{"role": "user", "content": self.prompt.build_prompt_cosplay()}]

        response = self.agent.chat(
            messages=messages,
            tools=self.tool_registry.get_tools()
        )
        message = response.choices[0].message

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                self.tool_registry.execute_tool(tool_name, **tool_args)

        self.prompt.update_chat_history(user_input)

        save(self.session_id, self.prompt.to_dict())

        return message.content

    