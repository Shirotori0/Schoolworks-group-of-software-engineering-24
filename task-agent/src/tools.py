from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import re
from typing import Any

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
TASKS_DB_FILE = DATA_DIR / "tasks.json"
LOG_FILE = DATA_DIR / "log.txt"

USER_LOCATIONS = {
    "1": "GuangZhou",
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


def _get_default_city() -> str:
    return _clean_text(os.getenv("TASK_AGENT_DEFAULT_CITY", "Shanghai")) or "Shanghai"


def _get_user_location_from_config(user_id: str) -> str:
    env_key = f"TASK_AGENT_USER_{user_id}_LOCATION"
    configured_city = _clean_text(os.getenv(env_key, ""))
    if configured_city:
        return configured_city
    return USER_LOCATIONS.get(user_id, _get_default_city())


def _load_task_store() -> dict[str, list[dict[str, Any]]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not TASKS_DB_FILE.exists():
        return {"tasks": []}

    try:
        data = json.loads(TASKS_DB_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _append_log("tasks.json is invalid, reset to empty store")
        return {"tasks": []}

    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        return {"tasks": []}
    return {"tasks": tasks}


def _save_task_store(store: dict[str, list[dict[str, Any]]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DB_FILE.write_text(
        json.dumps(store, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _normalize_task_id(task_id: str) -> str:
    cleaned = _clean_text(task_id).upper()
    digits = re.sub(r"\D", "", cleaned)
    if digits:
        return f"T{int(digits):03d}"
    return cleaned


def _next_task_id(tasks: list[dict[str, Any]]) -> str:
    max_task_number = 0
    for task in tasks:
        digits = re.sub(r"\D", "", str(task.get("id", "")))
        if digits:
            max_task_number = max(max_task_number, int(digits))
    return f"T{max_task_number + 1:03d}"


def _find_task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any] | None:
    normalized_task_id = _normalize_task_id(task_id)
    for task in tasks:
        if _normalize_task_id(str(task.get("id", ""))) == normalized_task_id:
            return task
    return None


def _format_task(task: dict[str, Any]) -> str:
    status = "已完成" if task.get("status") == "completed" else "待办"
    completed_at = task.get("completed_at")
    completed_suffix = f" | 完成于：{completed_at}" if completed_at else ""
    return f"{task['id']} [{status}] {task['title']}{completed_suffix}"


def _build_managed_tasks(user_input: str) -> list[str]:
    steps = _build_task_steps(user_input)
    actionable_steps = [
        step
        for step in steps
        if not step.startswith("检查完成情况")
    ]
    return actionable_steps or ["补充更具体的任务描述。"]


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
    return _get_user_location_from_config(user_id)


@tool
def create_task_list(user_input: str) -> str:
    """根据用户输入生成任务列表。"""
    steps = _build_task_steps(user_input)
    lines = [f"{index}. {step}" for index, step in enumerate(steps, start=1)]
    return "任务列表：\n" + "\n".join(lines)


@tool
def create_managed_tasks(user_input: str) -> str:
    """根据用户输入创建可管理的结构化任务，并写入 tasks.json。"""
    summary = _strip_request_prefix(_clean_text(user_input))
    if not summary:
        return "任务描述为空，未创建任务。"

    store = _load_task_store()
    tasks = store["tasks"]
    task_titles = _build_managed_tasks(summary)

    created_tasks: list[dict[str, Any]] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for title in task_titles:
        task = {
            "id": _next_task_id(tasks),
            "title": title,
            "status": "pending",
            "created_at": timestamp,
            "completed_at": None,
            "source": summary,
        }
        tasks.append(task)
        created_tasks.append(task)

    _save_task_store(store)
    _append_log(f"created {len(created_tasks)} managed tasks from: {summary}")

    lines = [f"- {_format_task(task)}" for task in created_tasks]
    return f"已创建 {len(created_tasks)} 个任务：\n" + "\n".join(lines)


@tool
def list_managed_tasks(status: str = "all") -> str:
    """查看结构化任务。status 可选 all、pending、completed。"""
    normalized_status = _clean_text(status).lower() or "all"
    status_alias = {
        "all": "all",
        "全部": "all",
        "pending": "pending",
        "待办": "pending",
        "todo": "pending",
        "completed": "completed",
        "done": "completed",
        "已完成": "completed",
    }
    normalized_status = status_alias.get(normalized_status, "all")

    store = _load_task_store()
    tasks = store["tasks"]
    if normalized_status != "all":
        tasks = [task for task in tasks if task.get("status") == normalized_status]

    if not tasks:
        return "当前没有符合条件的结构化任务。"

    header = {
        "all": "当前全部任务：",
        "pending": "当前待办任务：",
        "completed": "当前已完成任务：",
    }[normalized_status]
    lines = [f"- {_format_task(task)}" for task in tasks]
    return header + "\n" + "\n".join(lines)


@tool
def complete_managed_task(task_id: str) -> str:
    """将指定结构化任务标记为已完成。"""
    store = _load_task_store()
    tasks = store["tasks"]
    task = _find_task(tasks, task_id)
    if task is None:
        return f"未找到任务 {task_id}。"

    if task.get("status") == "completed":
        return f"任务 {task['id']} 已经是完成状态。"

    task["status"] = "completed"
    task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _save_task_store(store)
    _append_log(f"completed managed task {task['id']}")
    return f"已完成任务：{_format_task(task)}"


@tool
def delete_managed_task(task_id: str) -> str:
    """删除指定结构化任务。"""
    store = _load_task_store()
    tasks = store["tasks"]
    task = _find_task(tasks, task_id)
    if task is None:
        return f"未找到任务 {task_id}。"

    tasks.remove(task)
    _save_task_store(store)
    _append_log(f"deleted managed task {task['id']}")
    return f"已删除任务：{task['id']} {task['title']}"


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
    create_managed_tasks,
    list_managed_tasks,
    complete_managed_task,
    delete_managed_task,
    save_to_file,
]
