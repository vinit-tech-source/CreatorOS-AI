"""
app/services/content_generation_service.py

Bridging service for LangGraph workflow orchestration.
Handles authorization boundaries and context injection.
"""
import uuid
import logging
from typing import Any, Dict

from langgraph.graph.state import CompiledStateGraph

from app.core.exceptions import ProjectNotFoundError, PermissionDeniedError
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.repositories.project_repository_interface import AbstractProjectRepository
from app.repositories.brand_kit_repository_interface import AbstractBrandKitRepository
from app.schemas.content import ContentGenerateRequest, ContentGenerateResponse
from app.services.context_service import ContextService

logger = logging.getLogger(__name__)


class ContentGenerationService:
    def __init__(
        self,
        workspace_repo: AbstractWorkspaceRepository,
        project_repo: AbstractProjectRepository,
        brand_kit_repo: AbstractBrandKitRepository,
        workflow: CompiledStateGraph,
    ):
        self._ws_repo = workspace_repo
        self._proj_repo = project_repo
        self._bk_repo = brand_kit_repo
        self._workflow = workflow

    async def generate_content(
        self,
        request: ContentGenerateRequest,
        requesting_user_id: uuid.UUID,
    ) -> ContentGenerateResponse:
        """
        Authorize the user, build context, execute the graph, and map the output.
        """
        # 1. Authorize Workspace
        workspace = await self._ws_repo.get_by_id(request.workspace_id)
        if workspace is None or workspace.owner_id != requesting_user_id:
            logger.warning(
                f"Generation denied: User {requesting_user_id} cannot access workspace {request.workspace_id}"
            )
            raise PermissionDeniedError("Access to this workspace is denied.")

        # 2. Authorize Project
        project = await self._proj_repo.get_by_id(request.project_id)
        if project is None or project.workspace_id != workspace.id:
            logger.warning(
                f"Generation denied: Project {request.project_id} not found in workspace {request.workspace_id}"
            )
            raise ProjectNotFoundError()

        # 3. Retrieve Brand Kit
        brand_kit = await self._bk_repo.get_by_workspace(workspace.id)

        # 4. Build State Context
        initial_state = ContextService.assemble_initial_state(
            workspace=workspace,
            project=project,
            brand_kit=brand_kit,
            user_request=request.user_request,
            platform=request.platform,
        )
        
        # Merge extra request info if necessary
        # e.g., tone and target_audience overriding project defaults could go into a specific state key
        
        # 5. Invoke LangGraph
        logger.info(f"Invoking content graph for Project {project.id}")
        final_state = await self._workflow.ainvoke(initial_state)

        # 6. Check for graph errors
        errors = final_state.get("errors", [])
        if errors:
            logger.error(f"LangGraph execution encountered errors: {errors}")
            # Depending on business logic, we might still return partial data or raise an exception.
            # We'll continue and try to map whatever we got.

        # 7. Map to Response Schema
        # We need to construct a robust mapping since LangGraph agents may fail to produce data
        draft = final_state.get("draft") or {}
        optimized = final_state.get("optimized_content") or draft.get("content", "")
        
        # The schema requires specific structure
        fact_check_state = final_state.get("fact_check") or {}
        brand_voice_state = final_state.get("brand_voice") or {}
        seo_state = final_state.get("seo") or {}
        
        return ContentGenerateResponse(
            title=draft.get("title", f"Draft for {request.platform}"),
            content=optimized,
            platform=request.platform,
            contentType=request.content_type,
            hashtags=[
                {"tag": tag, "isNiche": False, "relevanceScore": 80}
                for tag in final_state.get("hashtags", [])
            ],
            cta="Let us know what you think in the comments!",
            imagePrompt={
                "visualStyle": final_state.get("image_prompt", {}).get("visual_style", "Standard"),
                "composition": final_state.get("image_prompt", {}).get("composition", "Standard"),
                "aspectRatio": final_state.get("image_prompt", {}).get("aspect_ratio", "1:1"),
                "lighting": final_state.get("image_prompt", {}).get("lighting", "Natural"),
                "colorPalette": final_state.get("image_prompt", {}).get("color_palette", "Vibrant"),
                "altText": final_state.get("image_prompt", {}).get("alt_text", ""),
                "prompt": final_state.get("image_prompt", {}).get("prompt", ""),
            },
            brandVoice={
                "score": brand_voice_state.get("score", 100),
                "isCompliant": brand_voice_state.get("is_compliant", True),
                "issues": brand_voice_state.get("issues", []),
                "changesMade": brand_voice_state.get("changes_made", []),
            },
            factCheck={
                "status": fact_check_state.get("overall_status", "PASSED"),
                "issues": fact_check_state.get("issues", []),
            },
            seo={
                "score": seo_state.get("score", 100),
                "primaryKeywords": seo_state.get("primary_keywords", []),
                "secondaryKeywords": seo_state.get("secondary_keywords", []),
                "recommendations": seo_state.get("recommendations", []),
            }
        )
