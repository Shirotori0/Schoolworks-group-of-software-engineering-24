from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

from langchain.tools import ToolRuntime, tool


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: str


def _get_project_root() -> Path:
    current_dir = Path(__file__).resolve().parent
    for candidate in (current_dir, current_dir.parent):
        if (candidate / "data").exists():
            return candidate
    return current_dir


PROJECT_ROOT = _get_project_root()
DATA_DIR = PROJECT_ROOT / "data"
TASKS_FILE = DATA_DIR / "tasks.txt"
LOG_FILE = DATA_DIR / "log.txt"

USER_LOCATIONS = {
    "1": "Florida",
    "2": "San Francisco",
    "3": "Shanghai",
}

SIMULATED_WEATHER = [
    ("晴", "26°C", "微风"),
    ("多云", "22°C", "东北风 2 级"),
    ("小雨", "19°C", "空气较湿润"),
    ("阴", "24°C", "体感偏闷"),
]


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _strip_request_prefix(text: str) -> str:
    prefixes = (
        "请帮我",
        "帮我",
        "请",
        "麻烦你",
        "麻烦",
        "我想",
        "我需要",
        "想要",
    )
    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix) :].strip()
    return text


def _split_task_parts(user_input: str) -> list[str]:
    cleaned = _strip_request_prefix(_clean_text(user_input))
    if not cleaned:
        return []

    parts = [
        part.strip("：:，。；;、 ")
        for part in re.split(r"[，。；;、\n]+|然后|并且|以及", cleaned)
        if part.strip("：:，。；;、 ")
    ]

    deduped_parts: list[str] = []
    for part in parts:
        if part not in deduped_parts:
            deduped_parts.append(part)
    return deduped_parts


def _build_task_steps(user_input: str) -> list[str]:
    parts = _split_task_parts(user_input)
    summary = _strip_request_prefix(_clean_text(user_input))

    if not summary:
        return ["补充更具体的目标、对象和期望结果。"]

    steps = [f"明确目标和交付结果：{summary}"]

    if len(parts) > 1:
        for part in parts[:3]:
            steps.append(f"执行子任务：{part}")
    elif any(keyword in summary for keyword in ("学习", "复习", "作业", "考试")):
        steps.extend(
            [
                "整理需要学习的主题，先标出最难或最紧急的部分。",
                "按时间块完成学习与练习，并记录卡住的问题。",
                "结束前做一次复盘，整理错题和下一步计划。",
            ]
        )
    elif any(keyword in summary for keyword in ("会议", "汇报", "演示", "答辩")):
        steps.extend(
            [
                "整理议题、目标和关键信息，确认参与人和时间。",
                "提前准备材料或提纲，并标记需要重点说明的部分。",
                "会后整理结论、待办事项和责任人。",
            ]
        )
    else:
        steps.extend(
            [
                "拆分出 2 到 3 个可立即执行的小步骤。",
                "按优先级依次处理，并在过程中记录关键结果。",
            ]
        )

    steps.append("检查完成情况，并决定是否需要保存或继续补充。")
    return steps


def _append_log(message: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


@tool
def get_weather_for_location(city: str) -> str:
    """Get simulated weather for a given city."""
    normalized_city = _clean_text(city)
    if not normalized_city:
        return "未提供城市，无法查询天气。"

    index = sum(ord(char) for char in normalized_city) % len(SIMULATED_WEATHER)
    weather, temperature, note = SIMULATED_WEATHER[index]
    return f"{normalized_city}的模拟天气：{weather}，{temperature}，{note}。"


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user location based on user ID."""
    user_id = runtime.context.user_id
    return USER_LOCATIONS.get(user_id, "Shanghai")


@tool
def create_task_list(user_input: str) -> str:
    """根据用户输入生成任务列表。"""
    steps = _build_task_steps(user_input)
    lines = [f"{index}. {step}" for index, step in enumerate(steps, start=1)]
    return "任务列表：\n" + "\n".join(lines)


@tool
def save_to_file(content: str) -> str:
    """将内容保存到项目 data 目录中的 tasks.txt。"""
    normalized_content = content.strip()
    if not normalized_content:
        return "内容为空，未执行保存。"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_FILE.write_text(normalized_content + "\n", encoding="utf-8")
    _append_log(f"saved tasks.txt ({len(normalized_content)} chars)")
    return f"任务已保存到 {TASKS_FILE}"


tools = [
    get_weather_for_location,
    get_user_location,
    create_task_list,
    save_to_file,
]
