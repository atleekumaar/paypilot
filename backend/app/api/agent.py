"""Agent API endpoints for conversational commerce and human-in-the-loop approvals."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.agents.orchestrator import AgentOrchestrator
from app.agents.state import AgentAction, AgentState, get_session_store

router = APIRouter(prefix="/api/agent", tags=["Agent"])


class AgentChatRequest(BaseModel):
    """Payload to interact with the PayPilot autonomous commerce agent."""

    message: str = Field(
        ...,
        description="User natural-language request (e.g. 'Find me a laptop under $1200 and buy the best one.')",
        json_schema_extra={"example": "Find me a laptop under $1200 for AI development and buy the best one."},
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Conversational session ID for multi-turn context",
        json_schema_extra={"example": "sess-alpha-1"},
    )


class AgentChatResponse(BaseModel):
    """Agent response envelope."""

    session_id: str
    status: str
    message: str
    purchase_plan_id: Optional[str] = None
    purchase_plan: Optional[Dict[str, Any]] = None
    candidate_products: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)


@router.post(
    "/chat",
    response_model=AgentChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with Autonomous Commerce Agent",
    description="Processes user intent, plans workflow, executes registered tools, enforces policy rules, and returns conversational response with activity tracking.",
)
async def agent_chat(request: AgentChatRequest) -> AgentChatResponse:
    """Send a message to the PayPilot agent."""
    orchestrator = AgentOrchestrator()
    result = orchestrator.process_message(request.message, request.session_id)
    return AgentChatResponse(**result)


@router.post(
    "/{session_id}/approve",
    response_model=Dict[str, Any],
    summary="Approve Purchase Plan within Agent Session",
    description="Resumes paused agent execution upon explicit human approval, creating a PayPal Sandbox order.",
)
async def agent_approve_purchase(session_id: str) -> Dict[str, Any]:
    """Approve a purchase plan in the active agent session."""
    orchestrator = AgentOrchestrator()
    try:
        return orchestrator.approve_purchase(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{session_id}/deny",
    response_model=Dict[str, Any],
    summary="Deny Purchase Plan within Agent Session",
    description="Halts purchasing workflow when user denies purchase approval.",
)
async def agent_deny_purchase(session_id: str) -> Dict[str, Any]:
    """Deny a purchase plan in the active agent session."""
    orchestrator = AgentOrchestrator()
    try:
        return orchestrator.deny_purchase(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{session_id}/state",
    response_model=AgentState,
    summary="Get Agent Session State",
)
async def get_agent_state(session_id: str) -> AgentState:
    """Retrieve operational state for an agent session."""
    store = get_session_store()
    state = store.get(session_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")
    return state


@router.get(
    "/{session_id}/actions",
    response_model=List[AgentAction],
    summary="Get Agent Operational Activity Log",
)
async def get_agent_actions(session_id: str) -> List[AgentAction]:
    """Retrieve logged tool actions and execution steps for an agent session."""
    store = get_session_store()
    state = store.get(session_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")
    return state.actions


@router.get(
    "/{session_id}/summary",
    summary="Get Agent Run Summary & Observability Metrics",
)
async def get_agent_summary(session_id: str) -> Dict[str, Any]:
    """Retrieve run summary and tools telemetry for a session."""
    store = get_session_store()
    state = store.get(session_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")

    tools_used = list(dict.fromkeys(a.tool for a in state.actions))
    return {
        "session_id": state.session_id,
        "step_count": state.current_step,
        "tools_used": tools_used,
        "status": state.status.value,
        "total_actions": len(state.actions),
        "created_at": state.created_at,
    }
