from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, IssuePriority, IssueType, SprintStatus


# ─── Auth ─────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserOut"


class TokenData(BaseModel):
    username: Optional[str] = None


# ─── User ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    employee_id: Optional[str] = None
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.VIEWER
    department: Optional[str] = None
    branch: Optional[str] = "Head Office"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    branch: Optional[str] = None
    is_active: Optional[bool] = None
    avatar_color: Optional[str] = None


class UserOut(BaseModel):
    id: int
    employee_id: Optional[str]
    username: str
    email: str
    full_name: str
    role: UserRole
    department: Optional[str]
    branch: Optional[str]
    avatar_color: str
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    login_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    department: Optional[str]
    avatar_color: str

    model_config = {"from_attributes": True}


# ─── Project ──────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    department: Optional[str] = None
    lead_id: Optional[int] = None
    color: Optional[str] = "#1B1F6B"
    project_type: Optional[str] = "scrum"
    category: Optional[str] = "Software"
    url: Optional[str] = None

    @field_validator("key")
    @classmethod
    def key_upper(cls, v):
        return v.upper().strip()


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    lead_id: Optional[int] = None
    status: Optional[str] = None
    color: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    key: str
    name: str
    description: Optional[str]
    department: Optional[str]
    lead: Optional[UserSummary]
    status: str
    color: str
    project_type: Optional[str] = "scrum"
    category: Optional[str] = "Software"
    url: Optional[str] = None
    created_at: datetime
    issue_count: Optional[int] = 0
    member_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# ─── Sprint ───────────────────────────────────────────────────────────────────

class SprintCreate(BaseModel):
    name: str
    goal: Optional[str] = None
    project_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    status: Optional[SprintStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SprintOut(BaseModel):
    id: int
    name: str
    goal: Optional[str]
    project_id: int
    status: SprintStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    velocity: float
    created_at: datetime
    issue_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# ─── Label ────────────────────────────────────────────────────────────────────

class LabelOut(BaseModel):
    id: int
    name: str
    color: str

    model_config = {"from_attributes": True}


# ─── Issue ────────────────────────────────────────────────────────────────────

class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    issue_type: IssueType = IssueType.TASK
    status: str = "todo"
    priority: IssuePriority = IssuePriority.MEDIUM
    story_points: Optional[int] = 0
    estimated_hours: Optional[float] = 0
    project_id: int
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None
    parent_id: Optional[int] = None
    due_date: Optional[datetime] = None
    label_ids: Optional[List[int]] = []


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[IssueType] = None
    status: Optional[str] = None
    priority: Optional[IssuePriority] = None
    story_points: Optional[int] = None
    estimated_hours: Optional[float] = None
    logged_hours: Optional[float] = None
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None
    parent_id: Optional[int] = None
    due_date: Optional[datetime] = None
    label_ids: Optional[List[int]] = None


class IssueOut(BaseModel):
    id: int
    key: str
    title: str
    description: Optional[str]
    issue_type: IssueType
    status: str
    priority: IssuePriority
    story_points: int
    estimated_hours: float
    logged_hours: float
    project_id: int
    project_key: Optional[str] = None
    reporter: Optional[UserSummary]
    assignee: Optional[UserSummary]
    sprint: Optional[SprintOut]
    parent_id: Optional[int]
    due_date: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    comment_count: Optional[int] = 0
    labels: Optional[List[LabelOut]] = []

    model_config = {"from_attributes": True}


class IssueSummary(BaseModel):
    id: int
    key: str
    title: str
    issue_type: IssueType
    status: str
    priority: IssuePriority
    assignee: Optional[UserSummary]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Comment ──────────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    content: str
    is_internal: bool = False


class CommentOut(BaseModel):
    id: int
    content: str
    issue_id: int
    author: UserSummary
    is_internal: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ─── Activity ─────────────────────────────────────────────────────────────────

class ActivityOut(BaseModel):
    id: int
    action: str
    field_changed: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    issue_id: Optional[int]
    user: UserSummary
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Notification ─────────────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: int
    message: str
    type: str
    is_read: bool
    issue_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard / Analytics ────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_issues: int
    open_issues: int
    in_progress: int
    resolved_today: int
    overdue: int
    by_status: dict
    by_priority: dict
    by_type: dict
    by_assignee: List[dict]
    recent_activity: List[ActivityOut]
    sprint_progress: Optional[dict] = None
    velocity_trend: Optional[List[dict]] = None
    burndown: Optional[List[dict]] = None
