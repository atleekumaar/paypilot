"""SQLAlchemy model for Tool Execution Audit and Telemetry."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from app.db.session import Base


class ToolAuditLogModel(Base):
    """Audit log tracking tool invocations, security decisions, and outcomes."""

    __tablename__ = "tool_audit_logs"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    step = Column(Integer, nullable=False)
    tool_name = Column(String, nullable=False, index=True)
    status = Column(String, default="completed", nullable=False)
    summary = Column(Text, nullable=False)
    arguments_sanitized = Column(JSON, default=dict)
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

