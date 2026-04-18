"""项目 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.models import Project, ProjectMember, ProjectMemory, User
from app.models.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectMemoryCreate, ProjectMemoryResponse, ProjectMemoryUpdate
)
from app.services.auth import require_user, resolve_project_for_user
from app.services.project import ensure_default_project, get_project_membership

router = APIRouter()


def build_project_response(project: Project, role: str | None = None) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        visibility=project.visibility,
        created_at=project.created_at,
        updated_at=project.updated_at,
        role=role
    )


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    ensure_default_project(db, user)

    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == user.id).all()
    project_ids = [membership.project_id for membership in memberships]
    projects = db.query(Project).filter(Project.id.in_(project_ids)).order_by(Project.created_at.desc()).all() if project_ids else []
    role_map = {membership.project_id: membership.role for membership in memberships}

    return ProjectListResponse(
        items=[build_project_response(project, role_map.get(project.id)) for project in projects],
        total=len(projects)
    )


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    project = Project(
        name=request.name,
        description=request.description,
        owner_id=user.id,
        visibility="private"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    db.add(ProjectMember(project_id=project.id, user_id=user.id, role="owner"))
    db.commit()

    return build_project_response(project, "owner")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    project = resolve_project_for_user(db, user, project_id, "viewer")
    membership = get_project_membership(db, project.id, user.id)
    return build_project_response(project, membership.role if membership else None)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    request: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    project = resolve_project_for_user(db, user, project_id, "owner")

    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.visibility is not None:
        project.visibility = request.visibility

    db.commit()
    db.refresh(project)

    membership = get_project_membership(db, project.id, user.id)
    return build_project_response(project, membership.role if membership else None)


@router.get("/projects/{project_id}/memories", response_model=list[ProjectMemoryResponse])
async def list_project_memories(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    resolve_project_for_user(db, user, project_id, "viewer")
    memories = db.query(ProjectMemory).filter(
        ProjectMemory.project_id == project_id
    ).order_by(ProjectMemory.pinned.desc(), ProjectMemory.created_at.asc()).all()
    return memories


@router.post("/projects/{project_id}/memories", response_model=ProjectMemoryResponse)
async def create_project_memory(
    project_id: int,
    request: ProjectMemoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    resolve_project_for_user(db, user, project_id, "editor")

    memory = ProjectMemory(
        project_id=project_id,
        content=request.content,
        memory_type=request.memory_type,
        enabled=request.enabled,
        pinned=request.pinned,
        created_by=user.id
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


@router.put("/projects/{project_id}/memories/{memory_id}", response_model=ProjectMemoryResponse)
async def update_project_memory(
    project_id: int,
    memory_id: int,
    request: ProjectMemoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    resolve_project_for_user(db, user, project_id, "editor")

    memory = db.query(ProjectMemory).filter(
        ProjectMemory.id == memory_id,
        ProjectMemory.project_id == project_id
    ).first()
    if not memory:
        raise HTTPException(status_code=404, detail="项目记忆不存在")

    if request.content is not None:
        memory.content = request.content
    if request.memory_type is not None:
        memory.memory_type = request.memory_type
    if request.enabled is not None:
        memory.enabled = request.enabled
    if request.pinned is not None:
        memory.pinned = request.pinned

    db.commit()
    db.refresh(memory)
    return memory


@router.delete("/projects/{project_id}/memories/{memory_id}")
async def delete_project_memory(
    project_id: int,
    memory_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    resolve_project_for_user(db, user, project_id, "editor")

    memory = db.query(ProjectMemory).filter(
        ProjectMemory.id == memory_id,
        ProjectMemory.project_id == project_id
    ).first()
    if not memory:
        raise HTTPException(status_code=404, detail="项目记忆不存在")

    db.delete(memory)
    db.commit()
    return {"message": "项目记忆已删除"}


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    project = resolve_project_for_user(db, user, project_id, "owner")

    member_count = db.query(ProjectMember).filter(ProjectMember.user_id == user.id).count()
    if member_count <= 1:
        raise HTTPException(status_code=400, detail="至少保留一个项目，无法删除最后一个项目")

    db.delete(project)
    db.commit()
    return {"message": "项目已删除"}


@router.post("/projects/{project_id}/members/{user_id}")
async def add_project_member(
    project_id: int,
    user_id: int,
    role: str = "viewer",
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    resolve_project_for_user(db, user, project_id, "owner")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    membership = get_project_membership(db, project_id, user_id)
    if membership:
        membership.role = role
    else:
        membership = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        db.add(membership)

    db.commit()
    return {"message": "项目成员已更新"}
