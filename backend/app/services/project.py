"""项目服务"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import Project, ProjectMember, User


PROJECT_ROLE_LEVELS = {
    "viewer": 1,
    "editor": 2,
    "owner": 3,
}


def ensure_default_project(db: Session, user: User) -> Project:
    """确保用户存在默认项目。"""
    project = db.query(Project).filter(Project.owner_id == user.id).order_by(Project.id.asc()).first()
    if project:
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id
        ).first()
        if not membership:
            db.add(ProjectMember(project_id=project.id, user_id=user.id, role="owner"))
            db.commit()
        return project

    project = Project(
        name=f"{user.username} 的默认项目",
        description="系统自动创建的默认项目",
        owner_id=user.id,
        visibility="private"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    db.add(ProjectMember(project_id=project.id, user_id=user.id, role="owner"))
    db.commit()
    return project


def get_project_membership(db: Session, project_id: int, user_id: int) -> Optional[ProjectMember]:
    return db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()


def user_has_project_role(db: Session, project_id: int, user: User, minimum_role: str = "viewer") -> bool:
    if user.role == "admin":
        return True

    membership = get_project_membership(db, project_id, user.id)
    if not membership:
        return False

    current_level = PROJECT_ROLE_LEVELS.get(membership.role, 0)
    required_level = PROJECT_ROLE_LEVELS.get(minimum_role, 0)
    return current_level >= required_level
