import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_automation_service
from app.schemas.automation import AutomationRuleCreate, AutomationRuleResponse
from app.schemas.response import ApiResponse
from app.services.automation_service import AutomationService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/automations",
    tags=["Automations"],
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[AutomationRuleResponse],
    summary="Create Automation Rule",
)
async def create_automation_rule(
    workspace_id: uuid.UUID,
    data: AutomationRuleCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    automation_service: AutomationService = Depends(get_automation_service),
) -> ApiResponse[AutomationRuleResponse]:
    rule = await automation_service.create_rule(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=rule, message="Automation rule created.")

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[List[AutomationRuleResponse]],
    summary="List Automation Rules",
)
async def list_automation_rules(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    automation_service: AutomationService = Depends(get_automation_service),
) -> ApiResponse[List[AutomationRuleResponse]]:
    rules = await automation_service.list_rules(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=rules)

@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete Automation Rule",
)
async def delete_automation_rule(
    workspace_id: uuid.UUID,
    rule_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    automation_service: AutomationService = Depends(get_automation_service),
) -> ApiResponse[None]:
    await automation_service.delete_rule(
        workspace_id=workspace_id,
        rule_id=rule_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Automation rule deleted.")
