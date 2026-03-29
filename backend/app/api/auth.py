"""认证API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.models.database import get_db
from app.models.models import User
from app.models.schemas import (
    UserCreate, UserLogin, UserResponse, UserListResponse,
    TokenResponse, PasswordChange, AdminInit, AdminUserCreate,
    AdminUserUpdate, AdminPasswordReset, UserDetailResponse, UserStatsResponse
)
from app.services.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    verify_token, get_current_user, require_user, require_admin
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建用户
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="user",
        status="pending"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.status != "approved":
        raise HTTPException(status_code=403, detail="账号尚未通过审核")

    # 生成令牌
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """刷新令牌"""
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or user.status != "approved":
        raise HTTPException(status_code=401, detail="用户不存在或已被禁用")

    # 生成新令牌
    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(require_user)):
    """获取当前用户信息"""
    return user


@router.put("/change-password")
def change_password(
    data: PasswordChange,
    user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")

    user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "密码修改成功"}


@router.get("/users", response_model=UserListResponse)
def list_users(
    status: str = None,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅管理员）"""
    query = db.query(User)

    if status:
        query = query.filter(User.status == status)

    users = query.order_by(User.created_at.desc()).all()

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=len(users)
    )


@router.put("/users/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """审核通过用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.status == "approved":
        raise HTTPException(status_code=400, detail="用户已通过审核")

    user.status = "approved"
    user.approved_at = datetime.utcnow()
    user.approved_by = admin.id
    db.commit()
    db.refresh(user)

    return user


@router.put("/users/{user_id}/reject", response_model=UserResponse)
def reject_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """拒绝用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.status = "rejected"
    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账号")

    db.delete(user)
    db.commit()

    return {"message": "用户已删除"}


@router.get("/check-init")
def check_init(db: Session = Depends(get_db)):
    """检查是否需要初始化admin"""
    admin_count = db.query(User).filter(User.role == "admin").count()
    return {"needs_init": admin_count == 0}


@router.post("/init-admin", response_model=TokenResponse)
def init_admin(data: AdminInit, db: Session = Depends(get_db)):
    """初始化管理员账号"""
    # 检查是否已存在admin
    if db.query(User).filter(User.role == "admin").first():
        raise HTTPException(status_code=400, detail="管理员账号已存在")

    # 检查用户名和邮箱
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建管理员
    admin = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="admin",
        status="approved",
        approved_at=datetime.utcnow()
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    # 生成令牌
    access_token = create_access_token({"sub": str(admin.id)})
    refresh_token = create_refresh_token({"sub": str(admin.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(admin)
    )


# ============ 管理员用户管理接口 ============

@router.post("/users", response_model=UserResponse)
def create_user(
    data: AdminUserCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员创建用户"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 验证角色和状态
    if data.role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="无效的角色")
    if data.status not in ["pending", "approved", "rejected"]:
        raise HTTPException(status_code=400, detail="无效的状态")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        status=data.status,
        approved_at=datetime.utcnow() if data.status == "approved" else None,
        approved_by=admin.id if data.status == "approved" else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/users/{user_id}", response_model=UserDetailResponse)
def get_user_detail(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户详情（包含统计信息）"""
    from app.models.models import KnowledgeBase, Document, Chunk

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 统计用户的资源
    kb_count = db.query(KnowledgeBase).filter(KnowledgeBase.user_id == user_id).count()

    kb_ids = [kb.id for kb in db.query(KnowledgeBase).filter(KnowledgeBase.user_id == user_id).all()]
    doc_count = db.query(Document).filter(Document.kb_id.in_(kb_ids)).count() if kb_ids else 0
    chunk_count = 0
    if kb_ids:
        doc_ids = [doc.id for doc in db.query(Document).filter(Document.kb_id.in_(kb_ids)).all()]
        chunk_count = db.query(Chunk).filter(Chunk.doc_id.in_(doc_ids)).count() if doc_ids else 0

    return UserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        approved_at=user.approved_at,
        stats=UserStatsResponse(
            kb_count=kb_count,
            doc_count=doc_count,
            chunk_count=chunk_count
        )
    )


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能修改自己的角色
    if user_id == admin.id and data.role:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    # 更新字段
    if data.username:
        # 检查用户名是否已被使用
        existing = db.query(User).filter(
            User.username == data.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = data.username

    if data.email:
        # 检查邮箱是否已被使用
        existing = db.query(User).filter(
            User.email == data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        user.email = data.email

    if data.role:
        if data.role not in ["admin", "user"]:
            raise HTTPException(status_code=400, detail="无效的角色")
        user.role = data.role

    if data.status:
        if data.status not in ["pending", "approved", "rejected"]:
            raise HTTPException(status_code=400, detail="无效的状态")
        user.status = data.status
        if data.status == "approved" and not user.approved_at:
            user.approved_at = datetime.utcnow()
            user.approved_by = admin.id

    db.commit()
    db.refresh(user)

    return user


@router.put("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    data: AdminPasswordReset,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员重置用户密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "密码重置成功"}
