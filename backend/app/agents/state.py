"""Agent state models, action tracking, and session memory structures."""

from datetime import datetime, timezone
from enum import Enum
import threading
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.product import Product
from app.schemas.purchase_plan import PurchasePlan


class AgentStatus(str, Enum):
    """Operational lifecycle statuses for the autonomous commerce agent."""

    IDLE = "IDLE"
    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    SEARCHING = "SEARCHING"
    COMPARING = "COMPARING"
    RECOMMENDING = "RECOMMENDING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentAction(BaseModel):
    """Operational action logged during agent workflow execution."""

    id: str = Field(default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8].upper()}")
    session_id: str
    step: int
    tool: str
    status: str = Field(default="completed", description="completed | waiting | failed")
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRunSummary(BaseModel):
    """Observability run summary for developer telemetry and demo auditing."""

    session_id: str
    step_count: int
    tools_used: List[str]
    status: str
    total_actions: int
    created_at: datetime


class AgentPlan(BaseModel):
    """Structured action plan formulated by the agent."""

    goal: str
    steps: List[str] = Field(default_factory=list)


class ConversationMessage(BaseModel):
    """A conversational turn in multi-turn commerce."""

    role: str = Field(..., description="user | assistant | system")
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentState(BaseModel):
    """Operational state of the commerce agent for a given user session."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: str
    user_query: str = ""
    current_step: int = 0
    max_steps: int = 12
    status: AgentStatus = AgentStatus.IDLE

    # Contextual artifacts
    plan: Optional[AgentPlan] = None
    candidate_products: List[Product] = Field(default_factory=list)
    compared_products: List[Dict[str, Any]] = Field(default_factory=list)
    selected_product: Optional[Product] = None
    recommendation_summary: Optional[str] = None

    # Purchase & Payment boundaries
    purchase_plan_id: Optional[str] = None
    purchase_plan: Optional[PurchasePlan] = None
    approval_required: bool = False
    approval_status: str = Field(default="NONE", description="NONE | PENDING | APPROVED | DENIED")
    paypal_order_id: Optional[str] = None
    payment_status: Optional[str] = None

    # Observability & multi-turn memory
    actions: List[AgentAction] = Field(default_factory=list)
    messages: List[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def log_action(self, tool: str, summary: str, status: str = "completed") -> AgentAction:
        """Record an operational tool action into the activity log."""
        self.current_step += 1
        action = AgentAction(
            session_id=self.session_id,
            step=self.current_step,
            tool=tool,
            status=status,
            summary=summary,
        )
        self.actions.append(action)
        self.updated_at = datetime.now(timezone.utc)
        return action


class SessionStore:
    """Thread-safe in-memory session repository for multi-turn agent conversations."""

    def __init__(self):
        self._lock = threading.Lock()
        self._sessions: Dict[str, AgentState] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> AgentState:
        with self._lock:
            s_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
            if s_id not in self._sessions:
                self._sessions[s_id] = AgentState(session_id=s_id)
            return self._sessions[s_id]

    def get(self, session_id: str) -> Optional[AgentState]:
        with self._lock:
            return self._sessions.get(session_id)

    def save(self, state: AgentState) -> AgentState:
        with self._lock:
            state.updated_at = datetime.now(timezone.utc)
            self._sessions[state.session_id] = state
            return state

    def clear(self) -> None:
        with self._lock:
            self._sessions.clear()


_session_store_instance: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Dependency provider returning singleton session store."""
    global _session_store_instance
    if _session_store_instance is None:
        _session_store_instance = SessionStore()
    return _session_store_instance
