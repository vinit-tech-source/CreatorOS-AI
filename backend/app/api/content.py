"""
app/api/content.py

API endpoints for generating content using AI workflows.
"""
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import StreamingResponse

from app.core.rate_limit import limiter

from app.api.deps import get_current_user_id, get_content_generation_service
from app.schemas.response import ApiResponse
from app.schemas.content import ContentGenerateRequest, ContentGenerateResponse
from app.services.content_generation_service import ContentGenerationService

router = APIRouter(
    prefix="/content",
    tags=["Content Generation"],
)


@router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ContentGenerateResponse],
    summary="Generate AI Content",
    description="Invokes the LangGraph workflow to generate content based on the project and workspace context.",
)
@limiter.limit("5/minute")
async def generate_content(
    request: Request,
    body: ContentGenerateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ContentGenerationService = Depends(get_content_generation_service),
) -> ApiResponse[ContentGenerateResponse]:
    result = await service.generate_content(
        request=body,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=result, message="Content generated successfully.")


async def _stream_content_events(
    request: ContentGenerateRequest,
    user_id: uuid.UUID,
    service: ContentGenerationService,
) -> AsyncGenerator[str, None]:
    """
    Async generator that yields Server-Sent Events during content generation.

    Events emitted:
      - data: {"event": "started",        "message": "..."}
      - data: {"event": "context_loaded", "message": "..."}
      - data: {"event": "draft_ready",    "message": "...", "preview": "first 100 chars..."}
      - data: {"event": "complete",       "data": { full ContentGenerateResponse }}
      - data: {"event": "error",          "message": "error details"}

    Each event is formatted as an SSE data line: "data: {json}\\n\\n"
    """

    def sse(payload: dict) -> str:
        return f"data: {json.dumps(payload)}\n\n"

    try:
        yield sse({"event": "started", "message": "Content generation started..."})

        # Phase 1: context loading (brand kit, RAG knowledge)
        # We emit this before the workflow runs so the client sees immediate progress
        yield sse({"event": "context_loading", "message": "Loading workspace context and knowledge base..."})

        # Phase 2: Run the actual generation workflow
        # The current service is blocking, so we emit a "thinking" event before awaiting
        yield sse({"event": "generating", "message": "AI is generating your content draft..."})

        result = await service.generate_content(
            request=request,
            requesting_user_id=user_id,
        )

        # Phase 3: Emit a preview of the draft
        preview = ""
        if result and result.generated_content:
            preview = result.generated_content[:120] + ("..." if len(result.generated_content) > 120 else "")
        yield sse({"event": "draft_ready", "message": "Draft generated successfully.", "preview": preview})

        # Phase 4: Emit the complete result
        yield sse({
            "event": "complete",
            "message": "Content generation complete.",
            "data": result.model_dump() if result else {},
        })

    except Exception as exc:
        yield sse({"event": "error", "message": str(exc)})


@router.post(
    "/generate/stream",
    summary="Generate AI Content (SSE Streaming)",
    description=(
        "Streams content generation progress as Server-Sent Events. "
        "Connect with EventSource or fetch with text/event-stream to receive "
        "real-time progress: context_loading → generating → draft_ready → complete."
    ),
    response_class=StreamingResponse,
)
@limiter.limit("5/minute")
async def generate_content_stream(
    request: Request,
    body: ContentGenerateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ContentGenerationService = Depends(get_content_generation_service),
) -> StreamingResponse:
    """
    SSE endpoint for streaming content generation progress to the frontend.
    Returns Content-Type: text/event-stream.
    """
    return StreamingResponse(
        _stream_content_events(request=body, user_id=user_id, service=service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for SSE
        },
    )
