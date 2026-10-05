"""Commerce tool registry, schemas, and permission levels."""

from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from app.agents.state import AgentState

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


class ToolExecutionResult(BaseModel):
    """Structured response from tool execution."""

    tool: str
    success: bool
    data: Any = None
    error: Optional[str] = None


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
    ) -> None:
        """Register a backend-governed commerce tool."""
        defn = ToolDefinition(
            name=name,
            description=description,
            permission=permission,
            parameters=parameters or {},
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

    def execute(self, tool_name: str, arguments: Dict[str, Any], state: AgentState) -> ToolExecutionResult:
        """Execute registered tool handler with argument validation."""
        defn = self.get_tool(tool_name)
        if not defn:
            logger.warning(f"Attempt to invoke unknown tool '{tool_name}' rejected.")
            return ToolExecutionResult(
                tool=tool_name,
                success=False,
                error=f"Tool '{tool_name}' is not registered or permitted in PayPilot.",
            )

        handler = self._handlers.get(tool_name)
        if not handler:
            return ToolExecutionResult(
                tool=tool_name,
                success=False,
                error=f"No execution handler registered for '{tool_name}'.",
            )

        try:
            # Execute handler passing arguments and state
            result = handler(arguments=arguments, state=state)
            return ToolExecutionResult(tool=tool_name, success=True, data=result)
        except Exception as exc:
            logger.error(f"Error executing tool '{tool_name}': {exc}", exc_info=True)
            return ToolExecutionResult(tool=tool_name, success=False, error=str(exc))
