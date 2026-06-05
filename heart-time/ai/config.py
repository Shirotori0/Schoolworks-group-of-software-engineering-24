"""
[优化] 集中管理数据目录路径。
优先将数据写入 backend/ai/data/，若不存在则回退到 ai/data/。
"""
from pathlib import Path

# AI 层根目录（ai/）
AI_ROOT = Path(__file__).resolve().parent

# 优先使用 backend/ai/data/ 作为数据根目录
BACKEND_DATA_DIR = AI_ROOT.parent / "backend" / "ai" / "data"
if BACKEND_DATA_DIR.exists():
    DATA_DIR = BACKEND_DATA_DIR
else:
    DATA_DIR = AI_ROOT / "data"

PROMPTS_DIR = DATA_DIR / "prompts"
VECTORS_DIR = DATA_DIR / "vectors"
CHARACTER_SCRIPTS_DIR = DATA_DIR / "character_scripts"
RAW_DIR = DATA_DIR / "raw"

# 确保所有目录存在
for d in [PROMPTS_DIR, VECTORS_DIR, CHARACTER_SCRIPTS_DIR, RAW_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def vector_path_for_source(source_path: str) -> Path:
    """根据原始文本路径生成对应的向量文件路径。"""
    filename = Path(source_path.replace("\\", "/")).name
    return VECTORS_DIR / f"{filename}.jsonl"