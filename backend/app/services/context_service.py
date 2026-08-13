"""
app/services/context_service.py

Context builder service to assemble AI workflow context.
"""
from typing import Any, Dict

from app.models.brand_kit import BrandKit
from app.models.project import Project
from app.models.workspace import Workspace


class ContextService:
    """
    Builds the execution context for AI workflows,
    stripping sensitive information from models.
    """

    @staticmethod
    def build_workspace_context(workspace: Workspace) -> Dict[str, Any]:
        """Extract safe workspace attributes."""
        return {
            "id": str(workspace.id),
            "name": workspace.name,
            "description": workspace.description,
            "timezone": workspace.timezone,
        }

    @staticmethod
    def build_brand_kit_context(brand_kit: BrandKit | None) -> Dict[str, Any] | None:
        """Extract safe brand kit attributes."""
        if not brand_kit:
            return None
        return {
            "brand_name": brand_kit.brand_name,
            "description": brand_kit.description,
            "target_audience": brand_kit.target_audience,
            "brand_values": brand_kit.brand_values,
            "default_tone": brand_kit.default_tone,
            "preferred_language": brand_kit.preferred_language,
        }

    @staticmethod
    def build_project_context(project: Project) -> Dict[str, Any]:
        """Extract safe project attributes."""
        return {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "objective": project.objective,
            "target_audience": project.target_audience,
        }

    @classmethod
    def assemble_initial_state(
        cls,
        workspace: Workspace,
        project: Project,
        brand_kit: BrandKit | None,
        user_request: str,
        platform: str,
    ) -> Dict[str, Any]:
        """
        Assemble the initial dictionary for LangGraph state.
        """
        return {
            "workspace": cls.build_workspace_context(workspace),
            "project": cls.build_project_context(project),
            "brand_kit": cls.build_brand_kit_context(brand_kit),
            "user_request": user_request,
            "platform": platform,
            "strategy": None,
            "trends": [],
            "research": [],
            "outline": None,
            "draft": None,
            "optimized_content": None,
            "fact_check": None,
            "hashtags": [],
            "image_prompt": None,
            "schedule": None,
            "publishing": None,
            "analytics": None,
            "recommendations": [],
            "errors": [],
            "metadata": {},
        }
