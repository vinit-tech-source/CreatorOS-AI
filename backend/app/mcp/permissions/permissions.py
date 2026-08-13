"""
app/mcp/permissions/permissions.py

MCP permissions system.
"""
from enum import Enum


class MCPPermission(str, Enum):
    RESEARCH_READ = "research:read"
    SOCIAL_READ = "social:read"
    SOCIAL_PUBLISH = "social:publish"
    ANALYTICS_READ = "analytics:read"
    MEDIA_READ = "media:read"
    MEDIA_WRITE = "media:write"
