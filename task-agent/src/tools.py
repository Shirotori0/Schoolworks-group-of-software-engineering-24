from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str


@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"
@tool
def create_task_list(user_input: str) -> str:
    """根据用户输入生成任务列表"""
    return f"任务列表：\n1. 分析需求\n2. 拆分任务\n3. 执行计划\n（基于：{user_input}）"

@tool
def save_to_file(content: str) -> str:
    """将内容保存到文件"""
    with open("./data/tasks.txt", "w", encoding="utf-8") as f:
        f.write(content)
    return "任务已保存到 tasks.txt"

tools = [
    get_weather_for_location,
    get_user_location,
    create_task_list,
    save_to_file,
]