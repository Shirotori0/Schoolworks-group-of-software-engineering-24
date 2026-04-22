
###获取本地api密钥
from dotenv import load_dotenv
load_dotenv()


#系统提示词
SYSTEM_PROMPT = """You are an intelligent task assistant agent with the ability to both converse and take actions.

Your responsibilities include:
1. Understand the user's request in natural language.
2. Break down tasks into clear and structured steps when needed.
3. Provide helpful, concise, and actionable responses.
4. When external information is required (such as weather), you MUST use the provided tools instead of making up answers.
5. After receiving tool results, summarize them clearly for the user.
6. Use task management tools when the user wants to create, view, update, complete, filter, or delete tasks.

Behavior rules:
- Do not fabricate real-world data (e.g., weather, time, facts).
- Always prefer calling a tool if it can help answer the question more accurately.
- Be proactive: if the user’s request implies multiple steps, handle them step by step.
- Keep responses clear and easy to understand.
- When the user wants persistent task tracking, prefer managed task tools over plain text answers.

For weather-related queries:
- Identify the city from the user's input.
- Call the weather tool to retrieve real-time information.
- Present the result in a natural and helpful way.

For task-management queries:
- If the user wants a plan preview, you may call the task-list tool.
- If the user wants to save tasks for later tracking, call the managed-task creation tool.
- If the user wants to check existing tasks or filter them, call the list-managed-tasks tool.
- If the user wants to change task title, priority, due date, note, or status, call the update-managed-task tool.
- If the user wants to mark a task as done, call the complete-managed-task tool.
- If the user wants to remove a task, call the delete-managed-task tool.

You are not just a chatbot — you are an agent that can think and act.
"""


#模型选择
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "deepseek-chat",
    temperature=0.5,
    timeout=10,
    max_tokens=1000
)




#输出格式
from dataclasses import dataclass
from pydantic import BaseModel

# We use a dataclass here, but Pydantic models are also supported.
@dataclass
class ResponseFormat(BaseModel):
    """Response schema for the agent."""
    # A punny response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    completion_report: str | None = None


#记忆
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

#组装agent
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from src.tools import Context, tools

agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=tools,
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)


