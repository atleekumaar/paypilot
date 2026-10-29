"""SQLAlchemy model for Agent Conversational Sessions."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String
from app.db.session import Base


class AgentSessionModel(Base):
    """Persistent representation of multi-turn conversational agent sessions."""

    __tablename__ = "agent_sessions"

    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, default="IDLE", nullable=False)
    user_query = Column(String, nullable=True)
    current_step = Column(Integer, default=0, nullable=False)
    max_steps = Column(Integer, default=12, nullable=False)
    approval_status = Column(String, default="NONE", nullable=False)
    approval_required = Column(Boolean, default=False, nullable=False)
    purchase_plan_id = Column(String, nullable=True)
    paypal_order_id = Column(String, nullable=True)
    payment_status = Column(String, nullable=True)
    active_order_id = Column(String, nullable=True)
    support_request_approved = Column(Boolean, default=False, nullable=False)
    state_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

