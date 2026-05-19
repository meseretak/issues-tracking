from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Enum, Float, Table, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    SUPER_ADMIN      = "super_admin"
    ADMIN            = "admin"
    PROJECT_MANAGER  = "project_manager"
    SCRUM_MASTER     = "scrum_master"
    BUSINESS_ANALYST = "business_analyst"
    DEVELOPER        = "developer"
    QA_ENGINEER      = "qa_engineer"
    DEVOPS_ENGINEER  = "devops_engineer"
    SECURITY_ENGINEER= "security_engineer"
    CLIENT           = "client"
    VIEWER           = "viewer"




class IssuePriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"


class IssueType(str, enum.Enum):
    BUG         = "bug"
    FEATURE     = "feature"
    TASK        = "task"
    EPIC        = "epic"
    STORY       = "story"
    IMPROVEMENT = "improvement"
    SECURITY    = "security"
    INCIDENT    = "incident"
    TEST_CASE   = "test_case"
    CHANGE      = "change"


class SprintStatus(str, enum.Enum):
    PLANNED   = "planned"
    ACTIVE    = "active"
    COMPLETED = "completed"


class IssueSeverity(str, enum.Enum):
    BLOCKER  = "blocker"
    CRITICAL = "critical"
    MAJOR    = "major"
    MINOR    = "minor"
    TRIVIAL  = "trivial"


# ─── Association Tables ────────────────────────────────────────────────────────

issue_watchers = Table(
    "issue_watchers", Base.metadata,
    Column("issue_id", Integer, ForeignKey("issues.id")),
    Column("user_id",  Integer, ForeignKey("users.id")),
)

issue_labels = Table(
    "issue_labels", Base.metadata,
    Column("issue_id", Integer, ForeignKey("issues.id")),
    Column("label_id", Integer, ForeignKey("labels.id")),
)

team_members = Table(
    "team_members", Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)


# ─── Models ───────────────────────────────────────────────────────────────────

class WorkflowStatus(Base):
    __tablename__ = "workflow_statuses"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), nullable=False)
    key         = Column(String(50), unique=True, index=True, nullable=False)
    color       = Column(String(20), default="#0052CC")
    category    = Column(String(50), default="todo") # todo, in_progress, done
    order_index = Column(Integer, default=0)

class WorkflowTransitionRule(Base):
    __tablename__ = "workflow_rules"
    id              = Column(Integer, primary_key=True, index=True)
    from_status_key = Column(String(50), nullable=False)
    to_status_key   = Column(String(50), nullable=False)
    allowed_role    = Column(String(50), nullable=False)


class Team(Base):
    __tablename__ = "teams"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text)
    team_type   = Column(String(50))   # qa, dev, devops, pm, ba, security
    color       = Column(String(7), default="#1B1F6B")
    lead_id     = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    lead    = relationship("User", foreign_keys=[lead_id])
    members = relationship("User", secondary=team_members, back_populates="teams")


class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    employee_id     = Column(String(20), unique=True, index=True)
    username        = Column(String(50), unique=True, index=True, nullable=False)
    email           = Column(String(100), unique=True, index=True, nullable=False)
    full_name       = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    department      = Column(String(100))
    branch          = Column(String(100), default="Head Office")
    avatar_color    = Column(String(7), default="#1B1F6B")
    phone           = Column(String(20))
    is_active       = Column(Boolean, default=True)
    is_verified     = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
    last_login      = Column(DateTime(timezone=True))

    reported_issues = relationship("Issue", foreign_keys="Issue.reporter_id", back_populates="reporter")
    assigned_issues = relationship("Issue", foreign_keys="Issue.assignee_id", back_populates="assignee")
    comments        = relationship("Comment", back_populates="author")
    activity_logs   = relationship("ActivityLog", back_populates="user")
    watching        = relationship("Issue", secondary=issue_watchers, back_populates="watchers")
    notifications   = relationship("Notification", back_populates="user")
    teams           = relationship("Team", secondary=team_members, back_populates="members")


class Project(Base):
    __tablename__ = "projects"
    id          = Column(Integer, primary_key=True, index=True)
    key         = Column(String(10), unique=True, index=True, nullable=False)
    name        = Column(String(200), nullable=False)
    description = Column(Text)
    department  = Column(String(100))
    lead_id     = Column(Integer, ForeignKey("users.id"))
    status      = Column(String(20), default="active")
    color       = Column(String(7), default="#1B1F6B")
    risk_level  = Column(String(20), default="medium")
    project_type = Column(String(50), default="scrum")
    category     = Column(String(100), default="Software")
    url          = Column(String(255))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    lead    = relationship("User", foreign_keys=[lead_id])
    issues  = relationship("Issue", back_populates="project")
    sprints = relationship("Sprint", back_populates="project")
    members = relationship("ProjectMember", back_populates="project")


class ProjectMember(Base):
    __tablename__ = "project_members"
    id         = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    role       = Column(Enum(UserRole), default=UserRole.VIEWER)
    joined_at  = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="members")
    user    = relationship("User")


class Sprint(Base):
    __tablename__ = "sprints"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    goal       = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status     = Column(Enum(SprintStatus), default=SprintStatus.PLANNED)
    start_date = Column(DateTime(timezone=True))
    end_date   = Column(DateTime(timezone=True))
    velocity   = Column(Float, default=0)
    capacity   = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="sprints")
    issues  = relationship("Issue", back_populates="sprint")


class Label(Base):
    __tablename__ = "labels"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#F5A623")
    issues = relationship("Issue", secondary=issue_labels, back_populates="labels")


class Issue(Base):
    __tablename__ = "issues"
    id              = Column(Integer, primary_key=True, index=True)
    key             = Column(String(20), unique=True, index=True)
    title           = Column(String(500), nullable=False)
    description     = Column(Text)
    issue_type      = Column(Enum(IssueType), default=IssueType.TASK, nullable=False)
    status          = Column(String(50), default="todo", nullable=False)
    priority        = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False)
    severity        = Column(Enum(IssueSeverity), default=IssueSeverity.MINOR)
    story_points    = Column(Integer, default=0)
    estimated_hours = Column(Float, default=0)
    logged_hours    = Column(Float, default=0)
    environment     = Column(String(100))
    version         = Column(String(50))
    component       = Column(String(100))
    root_cause      = Column(Text)
    resolution      = Column(Text)

    project_id  = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    sprint_id   = Column(Integer, ForeignKey("sprints.id"))
    parent_id   = Column(Integer, ForeignKey("issues.id"))

    due_date    = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    project      = relationship("Project", back_populates="issues")
    reporter     = relationship("User", foreign_keys=[reporter_id], back_populates="reported_issues")
    assignee     = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_issues")
    sprint       = relationship("Sprint", back_populates="issues")
    comments     = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
    attachments  = relationship("Attachment", back_populates="issue", cascade="all, delete-orphan")
    activity_logs= relationship("ActivityLog", back_populates="issue")
    watchers     = relationship("User", secondary=issue_watchers, back_populates="watching")
    labels       = relationship("Label", secondary=issue_labels, back_populates="issues")
    time_logs    = relationship("TimeLog", back_populates="issue", cascade="all, delete-orphan")
    notifications= relationship("Notification", back_populates="issue")
    sub_issues   = relationship("Issue", foreign_keys=[parent_id], back_populates="parent")
    parent       = relationship("Issue", foreign_keys=[parent_id], remote_side=[id],
                                back_populates="sub_issues", overlaps="sub_issues")


class Comment(Base):
    __tablename__ = "comments"
    id          = Column(Integer, primary_key=True, index=True)
    content     = Column(Text, nullable=False)
    issue_id    = Column(Integer, ForeignKey("issues.id"), nullable=False)
    author_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_internal = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    issue  = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")


class Attachment(Base):
    __tablename__ = "attachments"
    id          = Column(Integer, primary_key=True, index=True)
    filename    = Column(String(255), nullable=False)
    file_path   = Column(String(500), nullable=False)
    file_size   = Column(Integer)
    mime_type   = Column(String(100))
    issue_id    = Column(Integer, ForeignKey("issues.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    issue    = relationship("Issue", back_populates="attachments")
    uploader = relationship("User")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id            = Column(Integer, primary_key=True, index=True)
    action        = Column(String(100), nullable=False)
    field_changed = Column(String(100))
    old_value     = Column(Text)
    new_value     = Column(Text)
    issue_id      = Column(Integer, ForeignKey("issues.id"))
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address    = Column(String(45))
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    issue = relationship("Issue", back_populates="activity_logs")
    user  = relationship("User", back_populates="activity_logs")


class Notification(Base):
    __tablename__ = "notifications"
    id         = Column(Integer, primary_key=True, index=True)
    message    = Column(Text, nullable=False)
    type       = Column(String(50), default="info")
    is_read    = Column(Boolean, default=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_id   = Column(Integer, ForeignKey("issues.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user  = relationship("User", back_populates="notifications")
    issue = relationship("Issue", back_populates="notifications")


class TimeLog(Base):
    __tablename__ = "time_logs"
    id         = Column(Integer, primary_key=True, index=True)
    issue_id   = Column(Integer, ForeignKey("issues.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    hours      = Column(Float, nullable=False)
    description= Column(Text)
    logged_at  = Column(DateTime(timezone=True), server_default=func.now())
    work_date  = Column(DateTime(timezone=True), nullable=False)

    issue = relationship("Issue", back_populates="time_logs")
    user  = relationship("User")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id    = Column(Integer, ForeignKey("teams.id"), nullable=True)
    message    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user  = relationship("User")
    team  = relationship("Team")


