"""
app/api/social_accounts.py

Social Account API endpoints for CreatorOS AI.

Social Accounts are nested under their parent Workspace resource.
Tokens are NEVER exposed in any response payload.
"""
import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_social_account_service
from app.schemas.response import ApiResponse
from app.schemas.social_account import (
    SocialAccountCreate,
    SocialAccountResponse,
    SocialAccountUpdate,
)
from app.services.social_account_service import SocialAccountService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/social-accounts",
    tags=["Social Accounts"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[SocialAccountResponse],
    summary="Connect Social Account",
    description="Connect a new social media account. Tokens are encrypted securely.",
)
async def create_social_account(
    workspace_id: uuid.UUID,
    data: SocialAccountCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SocialAccountService = Depends(get_social_account_service),
) -> ApiResponse[SocialAccountResponse]:
    account = await service.create_social_account(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=account, message="Social account connected successfully.")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[SocialAccountResponse]],
    summary="List Social Accounts",
    description="List all social accounts connected to this workspace.",
)
async def list_social_accounts(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SocialAccountService = Depends(get_social_account_service),
) -> ApiResponse[list[SocialAccountResponse]]:
    accounts = await service.list_social_accounts(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=accounts)


@router.get(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[SocialAccountResponse],
    summary="Get Social Account",
    description="Retrieve details of a specific social account. Tokens are NOT returned.",
)
async def get_social_account(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SocialAccountService = Depends(get_social_account_service),
) -> ApiResponse[SocialAccountResponse]:
    account = await service.get_social_account(
        workspace_id=workspace_id,
        account_id=account_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=account)


@router.patch(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[SocialAccountResponse],
    summary="Update Social Account",
    description="Apply partial updates to a social account's metadata.",
)
async def update_social_account(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    data: SocialAccountUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SocialAccountService = Depends(get_social_account_service),
) -> ApiResponse[SocialAccountResponse]:
    account = await service.update_social_account(
        workspace_id=workspace_id,
        account_id=account_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=account, message="Social account updated successfully.")


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete Social Account",
    description="Disconnect and permanently delete a social account.",
)
async def delete_social_account(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SocialAccountService = Depends(get_social_account_service),
) -> ApiResponse[None]:
    await service.delete_social_account(
        workspace_id=workspace_id,
        account_id=account_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Social account disconnected successfully.")
