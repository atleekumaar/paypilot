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

    # Post-Purchase context
    user_id: str = Field(default="guest_user", description="Authenticated user ID")
    active_order_id: Optional[str] = None
    active_order: Optional[Dict[str, Any]] = None
    active_shipment: Optional[Dict[str, Any]] = None
    support_request_draft: Optional[Dict[str, Any]] = None
    support_request_approved: bool = False

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
    """Thread-safe persistent session repository for multi-turn agent conversations with user isolation."""

    def __init__(self):
        self._lock = threading.Lock()
        self._sessions: Dict[str, AgentState] = {}

    def get_or_create(
        self, session_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> AgentState:
        with self._lock:
            s_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
            if s_id in self._sessions:
                existing = self._sessions[s_id]
                if user_id and existing.user_id != user_id:
                    raise PermissionError(
                        f"Access denied: Session '{s_id}' belongs to another user."
                    )
                return existing

            from app.db.session import get_db_context
            from app.models.agent_session import AgentSessionModel

            with get_db_context() as db:
                record = db.query(AgentSessionModel).filter(AgentSessionModel.session_id == s_id).first()
                if record:
                    if user_id and record.user_id != user_id:
                        raise PermissionError(
                            f"Access denied: Session '{s_id}' belongs to another user."
                        )
                    state_data = record.state_data or {}
                    state = AgentState(**state_data) if state_data else AgentState(
                        session_id=record.session_id,
                        user_id=record.user_id,
                        status=AgentStatus(record.status),
                        user_query=record.user_query or "",
                        current_step=record.current_step,
                        max_steps=record.max_steps,
                        approval_status=record.approval_status,
                        approval_required=record.approval_required,
                        purchase_plan_id=record.purchase_plan_id,
                        paypal_order_id=record.paypal_order_id,
                        payment_status=record.payment_status,
                        active_order_id=record.active_order_id,
                        support_request_approved=record.support_request_approved,
                        created_at=record.created_at,
                        updated_at=record.updated_at,
                    )
                    self._sessions[s_id] = state
                    return state

                new_state = AgentState(
                    session_id=s_id,
                    user_id=user_id or "guest_user",
                )
                self._sessions[s_id] = new_state
                db_model = AgentSessionModel(
                    session_id=new_state.session_id,
                    user_id=new_state.user_id,
                    status=new_state.status.value if hasattr(new_state.status, "value") else str(new_state.status),
                    user_query=new_state.user_query,
                    current_step=new_state.current_step,
                    max_steps=new_state.max_steps,
                    approval_status=new_state.approval_status,
                    approval_required=new_state.approval_required,
                    purchase_plan_id=new_state.purchase_plan_id,
                    paypal_order_id=new_state.paypal_order_id,
                    payment_status=new_state.payment_status,
                    active_order_id=new_state.active_order_id,
                    support_request_approved=new_state.support_request_approved,
                    state_data=new_state.model_dump(mode="json"),
                    created_at=new_state.created_at,
                    updated_at=new_state.updated_at,
                )
                db.merge(db_model)
                return new_state

    def get(self, session_id: str, user_id: Optional[str] = None) -> Optional[AgentState]:
        with self._lock:
            state = self._sessions.get(session_id)
            if not state:
                from app.db.session import get_db_context
                from app.models.agent_session import AgentSessionModel
                with get_db_context() as db:
                    record = db.query(AgentSessionModel).filter(AgentSessionModel.session_id == session_id).first()
                    if record:
                        state_data = record.state_data or {}
                        state = AgentState(**state_data) if state_data else AgentState(
                            session_id=record.session_id,
                            user_id=record.user_id,
                            status=AgentStatus(record.status),
                            user_query=record.user_query or "",
                            current_step=record.current_step,
                            max_steps=record.max_steps,
                            approval_status=record.approval_status,
                            approval_required=record.approval_required,
                            purchase_plan_id=record.purchase_plan_id,
                            paypal_order_id=record.paypal_order_id,
                            payment_status=record.payment_status,
                            active_order_id=record.active_order_id,
                            support_request_approved=record.support_request_approved,
                            created_at=record.created_at,
                            updated_at=record.updated_at,
                        )
                        self._sessions[session_id] = state

            if state and user_id and state.user_id != user_id:
                raise PermissionError(
                    f"Access denied: Session '{session_id}' belongs to another user."
                )
            return state

    def save(self, state: AgentState, touch: bool = True) -> AgentState:
        with self._lock:
            if touch:
                state.updated_at = datetime.now(timezone.utc)
            self._sessions[state.session_id] = state
            from app.db.session import get_db_context
            from app.models.agent_session import AgentSessionModel
            with get_db_context() as db:
                db_model = AgentSessionModel(
                    session_id=state.session_id,
                    user_id=state.user_id,
                    status=state.status.value if hasattr(state.status, "value") else str(state.status),
                    user_query=state.user_query,
                    current_step=state.current_step,
                    max_steps=state.max_steps,
                    approval_status=state.approval_status,
                    approval_required=state.approval_required,
                    purchase_plan_id=state.purchase_plan_id,
                    paypal_order_id=state.paypal_order_id,
                    payment_status=state.payment_status,
                    active_order_id=state.active_order_id,
                    support_request_approved=state.support_request_approved,
                    state_data=state.model_dump(mode="json"),
                    created_at=state.created_at,
                    updated_at=state.updated_at,
                )
                db.merge(db_model)
            return state

    def clear(self) -> None:
        with self._lock:
            self._sessions.clear()
            from app.db.session import get_db_context
            from app.models.agent_session import AgentSessionModel
            with get_db_context() as db:
                db.query(AgentSessionModel).delete()


_session_store_instance: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Dependency provider returning singleton session store."""
    global _session_store_instance
    if _session_store_instance is None:
        _session_store_instance = SessionStore()
    return _session_store_instance
