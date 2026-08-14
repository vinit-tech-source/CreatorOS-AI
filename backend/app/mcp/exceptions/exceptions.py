"""
app/mcp/exceptions/exceptions.py

Exceptions for the MCP architecture.
"""
from app.core.exceptions import AppException


class MCPConnectionError(AppException):
    """Raised when an MCP client cannot connect to a server or external provider."""
    def __init__(self, message: str = "MCP connection failed"):
        super().__init__(message)


class MCPToolNotFoundError(AppException):
    """Raised when a requested MCP tool is not found."""
    def __init__(self, message: str = "MCP tool not found"):
        super().__init__(message)


class MCPToolValidationError(AppException):
    """Raised when an MCP tool fails input or output validation."""
    def __init__(self, message: str = "MCP tool validation failed"):
        super().__init__(message)


class MCPToolPermissionError(AppException):
    """Raised when an MCP tool call lacks the required permissions."""
    def __init__(self, message: str = "MCP tool permission denied"):
        super().__init__(message)


class MCPToolTimeoutError(AppException):
    """Raised when an MCP tool execution exceeds the allowed timeout."""
    def __init__(self, message: str = "MCP tool execution timed out"):
        super().__init__(message)


class MCPToolExecutionError(AppException):
    """Raised when an MCP tool execution fails internally."""
    def __init__(self, message: str = "MCP tool execution failed"):
        super().__init__(message)


class MCPProviderError(AppException):
    """Raised when an underlying MCP provider (e.g., YouTube, Reddit) returns an error."""
    def __init__(self, message: str = "MCP provider returned an error"):
        super().__init__(message)


class MCPAuthenticationError(MCPProviderError):
    """Raised when an underlying MCP provider returns an authentication or authorization error."""
    def __init__(self, message: str = "MCP provider authentication failed"):
        super().__init__(message)
