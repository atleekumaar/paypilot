"""Commerce tool registry, schemas, and permission levels."""

from datetime import datetime, timezone
from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Optional, Type
import uuid
from pydantic import BaseModel, Field, ValidationError

from app.agents.state import AgentState
from app.db.session import get_db_context
from app.models.audit_log import ToolAuditLogModel

logger = logging.getLogger(__name__)


class ToolPermission(str, Enum):
    """Permission classification controlling tool execution privilege."""

    READ = "READ"
    WRITE = "WRITE"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    PAYMENT = "PAYMENT"


class ToolDefinition(BaseModel):
    """Metadata, signature, and permissions for an agent-callable commerce tool."""

    name: str
    description: str
    permission: ToolPermission
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON schema describing expected parameters")
    schema_model: Optional[Any] = Field(default=None, description="Pydantic validation model class")


class ToolExecutionResult(BaseModel):
    """Structured response from tool execution."""

    tool: str
    success: bool
    data: Any = None
    error: Optional[str] = None


def _sanitize_arguments(args: Dict[str, Any]) -> Dict[str, Any]:
    """Strip or mask potentially sensitive credentials from audit logs."""
    sensitive_keys = {"secret", "token", "password", "key", "authorization", "client_secret"}
    sanitized = {}
    for k, v in args.items():
        if any(sk in k.lower() for sk in sensitive_keys):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = _sanitize_arguments(v)
        else:
            sanitized[k] = v
    return sanitized


class ToolRegistry:
    """Registry maintaining available commerce tools and enforcing registration boundary."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}

    def register(
        self,
        name: str,
        description: str,
        permission: ToolPermission,
        handler: Callable[..., Any],
        parameters: Optional[Dict[str, Any]] = None,
        schema_model: Optional[Type[BaseModel]] = None,
    ) -> None:
        """Register a backend-governed commerce tool with strict validation schema."""
        defn = ToolDefinition(
            name=name,
            description=description,
            permission=permission,
            parameters=parameters or {},
            schema_model=schema_model,
        )
        self._tools[name] = defn
        self._handlers[name] = handler
        logger.debug(f"Registered commerce tool '{name}' with permission '{permission.value}'")

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Look up tool definition by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """Return list of all registered tool definitions."""
        return list(self._tools.values())

    def _record_audit_log(
        self,
        tool_name: str,
        state: AgentState,
        arguments: Dict[str, Any],
        status: str,
        summary: str,
        result_summary: Optional[str] = None,
    ) -> None:
        """Persist tool audit trail to the database."""
        try:
            with get_db_context() as db:
                log_entry = ToolAuditLogModel(
                    id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                    session_id=state.session_id,
                    user_id=state.user_id,
                    step=state.current_step,
                    tool_name=tool_name,
                    status=status,
                    summary=summary[:500],
                    arguments_sanitized=_sanitize_arguments(arguments),
                    result_summary=result_summary[:500] if result_summary else None,
                    created_at=datetime.now(timezone.utc),
                )
                db.merge(log_entry)
        except Exception as exc:
            logger.warning(f"Failed to record tool audit log: {exc}")

    def execute(self, tool_name: str, arguments: Dict[str, Any], state: AgentState) -> ToolExecutionResult:
        """Execute registered tool handler with strict Pydantic argument validation and audit logging."""
        defn = self.get_tool(tool_name)
        if not defn:
            logger.warning(f"Attempt to invoke unknown tool '{tool_name}' rejected.")
            self._record_audit_log(
                tool_name=tool_name,
                state=state,
                arguments=arguments,
                status="rejected",
                summary=f"Unknown tool '{tool_name}' rejected",
                result_summary="Tool not registered",
            )
            return ToolExecutionResult(
                tool=tool_name,
                success=False,
                error=f"Tool '{tool_name}' is not registered or permitted in PayPilot.",
            )

        # Strict Pydantic Argument Validation
        validated_args = arguments
        if defn.schema_model:
            try:
                model_inst = defn.schema_model.model_validate(arguments)
                validated_args = model_inst.model_dump()
            except ValidationError as val_err:
                err_msg = f"Validation failed for tool '{tool_name}': {val_err}"
                logger.warning(err_msg)
                self._record_audit_log(
                    tool_name=tool_name,
                    state=state,
                    arguments=arguments,
                    status="validation_error",
                    summary=err_msg,
                    result_summary=str(val_err),
                )
                return ToolExecutionResult(tool=tool_name, success=False, error=err_msg)

        handler = self._handlers.get(tool_name)
        if not handler:
            return ToolExecutionResult(
                tool=tool_name,
                success=False,
                error=f"No execution handler registered for '{tool_name}'.",
            )

        try:
            result = handler(arguments=validated_args, state=state)
            self._record_audit_log(
                tool_name=tool_name,
                state=state,
                arguments=validated_args,
                status="completed",
                summary=f"Successfully executed tool '{tool_name}'",
                result_summary=str(result)[:200] if result else None,
            )
            return ToolExecutionResult(tool=tool_name, success=True, data=result)
        except Exception as exc:
            logger.error(f"Error executing tool '{tool_name}': {exc}", exc_info=True)
            self._record_audit_log(
                tool_name=tool_name,
                state=state,
                arguments=validated_args,
                status="failed",
                summary=f"Tool '{tool_name}' execution threw exception",
                result_summary=str(exc),
            )
            return ToolExecutionResult(tool=tool_name, success=False, error=str(exc))
