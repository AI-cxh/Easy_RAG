"""用户长期记忆 API。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from app.models.models import User
from app.services.auth import require_user
from app.services.user_memory import user_memory_service

router = APIRouter()


class UserMemoryResponse(BaseModel):
    id: str
    memory: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    score: Optional[float] = None


@router.get("/user-memories", response_model=List[UserMemoryResponse])
async def list_user_memories(
    user: User = Depends(require_user)
):
    """获取当前用户的 mem0 长期记忆。"""
    try:
        return await user_memory_service.list_user_memories(user.id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"获取长期记忆失败: {str(exc)}")


@router.delete("/user-memories/{memory_id}")
async def delete_user_memory(
    memory_id: str,
    user: User = Depends(require_user)
):
    """删除当前用户的一条 mem0 长期记忆。"""
    try:
        deleted = await user_memory_service.delete_user_memory(user.id, memory_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"删除长期记忆失败: {str(exc)}")

    if not deleted:
        raise HTTPException(status_code=404, detail="长期记忆不存在")

    return {"message": "长期记忆已删除"}
