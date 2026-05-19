import os
import re

backend_dir = r"c:\Users\meseretak\Desktop\devops execrices\issues tracking\backend"

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    if "models.py" in filepath:
        # Remove IssueStatus Enum definition
        content = re.sub(r'class IssueStatus\(str, enum\.Enum\):.*?(?=\n\nclass |\n\n# ───)', '', content, flags=re.DOTALL)
        
        # Replace Issue.status column definition
        content = content.replace('status          = Column(Enum(IssueStatus), default="backlog", nullable=False)', 
                                  'status          = Column(String(50), default="todo", nullable=False)')
        
        # Add new tables
        new_tables = """
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
"""
        content = content.replace('# ─── Models ───────────────────────────────────────────────────────────────────',
                                  '# ─── Models ───────────────────────────────────────────────────────────────────\n' + new_tables)

    elif "schemas.py" in filepath:
        content = content.replace('', '')
        content = content.replace('', '')
        content = content.replace('from app.models import UserRole, IssuePriority', 'from app.models import UserRole, IssuePriority')
        content = re.sub(r'status: Optional\[IssueStatus\] = None', 'status: Optional[str] = None', content)
        content = re.sub(r'status: IssueStatus = "backlog"', 'status: str = "todo"', content)
        content = re.sub(r'status: IssueStatus', 'status: str', content)

    else:
        # For routers and seed.py
        content = content.replace('', '')
        content = content.replace('', '')
        
        # Replace IssueStatus.<VALUE> with "<value>"
        def replace_enum(match):
            return f'"{match.group(1).lower()}"'
        
        content = re.sub(r'IssueStatus\.([A-Z_]+)', replace_enum, content)

        if "issues.py" in filepath:
            content = content.replace('status: Optional[IssueStatus] = None,', 'status: Optional[str] = None,')

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk(backend_dir):
    for f in files:
        if f.endswith(".py"):
            process_file(os.path.join(root, f))
