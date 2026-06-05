from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import text as db_text
from config import get_db
from api_schemas import (
    CreateMemoryRequest, MemoryResponse, DeleteMemoryResponse,
    UpdateMemoryRequest, UpdateMemoryResponse
)
from utils.exceptions import AppException
import uuid
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/memories", response_model=MemoryResponse)
async def create_memory(request: CreateMemoryRequest, db: Session = Depends(get_db)):
    """创建新记忆体"""
    try:
        if not request.name.strip():
            raise AppException(status_code=400, detail="记忆体名称不能为空")

        memory_id = str(uuid.uuid4())

        sql = db_text("""
            INSERT INTO memory (memory_id, user_id, name, summary)
            VALUES (:memory_id, :user_id, :name, :summary)
        """)
        db.execute(sql, {
            "memory_id": memory_id,
            "user_id": request.user_id,
            "name": request.name,
            "summary": request.summary
        })
        db.commit()

        logger.info(f"用户 {request.user_id} 创建记忆体 {memory_id}")

        return MemoryResponse(
            memory_id=memory_id,
            user_id=request.user_id,
            name=request.name,
            summary=request.summary,
            source_file_path="",
            vector_file_path="",
            import_status="not_imported",
            created_at="",
            updated_at=""
        )

    except AppException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建记忆体失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="创建记忆体失败")


@router.get("/memories", response_model=list[MemoryResponse])
async def get_memories(
    user_id: str,
    db: Session = Depends(get_db)
):
    """获取用户的记忆体列表"""
    try:
        sql = db_text("""
            SELECT memory_id, user_id, name, summary, 
                   source_file_path, vector_file_path, import_status,
                   created_at, updated_at
            FROM memory
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)
        rows = db.execute(sql, {"user_id": user_id}).fetchall()

        return [
            MemoryResponse(
                memory_id=row[0],
                user_id=row[1],
                name=row[2],
                summary=row[3] or "",
                source_file_path=row[4] or "",
                vector_file_path=row[5] or "",
                import_status=row[6],
                created_at=str(row[7]) if row[7] else "",
                updated_at=str(row[8]) if row[8] else ""
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"查询记忆体列表失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="查询记忆体列表失败")


@router.delete("/memories/{memory_id}", response_model=DeleteMemoryResponse)
async def delete_memory(
    memory_id: str,
    db: Session = Depends(get_db)
):
    """删除记忆体"""
    try:
        check_sql = db_text("SELECT memory_id, source_file_path, vector_file_path FROM memory WHERE memory_id = :memory_id")
        result = db.execute(check_sql, {"memory_id": memory_id}).fetchone()

        if not result:
            raise AppException(status_code=404, detail="记忆体不存在")

        source_file = result[1]
        vector_file = result[2]

        if source_file and os.path.exists(source_file):
            os.remove(source_file)
            logger.info(f"已删除源文件: {source_file}")

        if vector_file and os.path.exists(vector_file):
            os.remove(vector_file)
            logger.info(f"已删除向量文件: {vector_file}")

        delete_sql = db_text("DELETE FROM memory WHERE memory_id = :memory_id")
        db.execute(delete_sql, {"memory_id": memory_id})
        db.commit()

        logger.info(f"记忆体 {memory_id} 已删除")

        return DeleteMemoryResponse(status="deleted")

    except AppException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除记忆体失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="删除记忆体失败")


@router.post("/memories/{memory_id}/upload")
async def upload_memory_data(
    memory_id: str,
    user_id: str = Form(...),
    file: UploadFile = File(None),
    text: str = Form(None),
    db: Session = Depends(get_db)
):
    """上传文本或文件，并导入到记忆体"""
    try:
        if not file and not text:
            raise AppException(status_code=400, detail="必须提供 file 或 text")

        check_sql = db_text("SELECT memory_id, name FROM memory WHERE memory_id = :memory_id")
        memory = db.execute(check_sql, {"memory_id": memory_id}).fetchone()
        if not memory:
            raise AppException(status_code=404, detail="记忆体不存在")

        raw_dir = "ai/data/raw"
        os.makedirs(raw_dir, exist_ok=True)

        file_path = os.path.join(raw_dir, f"{memory_id}.txt")

        content = ""
        if text:
            content = text
        elif file:
            content = (await file.read()).decode("utf-8")

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n===== {datetime.now().strftime('%Y-%m-%d %H:%M')} 上传 =====\n")
            f.write(content)
            f.write("\n")

        logger.info(f"记忆体 {memory_id} 文本已保存到 {file_path}")

        try:
            from ai.pipeline.embedding_runtime import EmbeddingRuntime
            runtime = EmbeddingRuntime(file_path)
            runtime.process_file()
            import_status = "imported"
            message = "导入成功"
        except Exception as e:
            logger.error(f"向量化失败: {str(e)}")
            import_status = "failed"
            message = f"向量化失败: {str(e)[:100]}"

        vector_path = file_path.replace(".txt", ".txt.jsonl").replace("raw", "vectors")

        update_sql = db_text("""
            UPDATE memory 
            SET source_file_path = :source_path,
                vector_file_path = :vector_path,
                import_status = :status,
                updated_at = CURRENT_TIMESTAMP
            WHERE memory_id = :memory_id
        """)
        db.execute(update_sql, {
            "source_path": file_path,
            "vector_path": vector_path,
            "status": import_status,
            "memory_id": memory_id
        })
        db.commit()

        return {
            "memory_id": memory_id,
            "file_path": file_path,
            "vector_path": vector_path,
            "import_status": import_status,
            "message": message
        }

    except AppException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"上传记忆体数据失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="上传记忆体数据失败")


@router.patch("/memories/{memory_id}", response_model=UpdateMemoryResponse)
async def update_memory(
    memory_id: str,
    request: UpdateMemoryRequest,
    db: Session = Depends(get_db)
):
    """更新记忆体信息（名称、简介）"""
    try:
        if request.name is not None and not request.name.strip():
            raise AppException(status_code=400, detail="记忆体名称不能为空")
        
        check_sql = db_text("SELECT memory_id, name, summary FROM memory WHERE memory_id = :memory_id")
        result = db.execute(check_sql, {"memory_id": memory_id}).fetchone()

        if not result:
            raise AppException(status_code=404, detail="记忆体不存在")

        old_name = result[1]
        old_summary = result[2]

        new_name = request.name.strip() if request.name is not None else old_name
        new_summary = request.summary.strip() if request.summary is not None else old_summary

        update_sql = db_text("""
            UPDATE memory 
            SET name = :name, summary = :summary, updated_at = CURRENT_TIMESTAMP
            WHERE memory_id = :memory_id
        """)
        db.execute(update_sql, {
            "name": new_name,
            "summary": new_summary,
            "memory_id": memory_id
        })
        db.commit()

        logger.info(f"记忆体 {memory_id} 已更新")

        return UpdateMemoryResponse(
            memory_id=memory_id,
            name=new_name,
            summary=new_summary,
            updated_at=""
        )

    except AppException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新记忆体失败: {str(e)}", exc_info=True)
        raise AppException(status_code=500, detail="更新记忆体失败")