"""
app/services/token_refresh_service.py

Automatic OAuth token refresh service for social accounts.

Responsibilities:
  - Find social accounts with tokens expiring within TOKEN_REFRESH_BEFORE_EXPIRY_MINUTES
  - Decrypt the current refresh_token for each account
  - Call the appropriate OAuth provider's refresh_token() method
  - Re-encrypt the new access_token (and refresh_token if rotated)
  - Update token_expires_at in the database
  - Mark accounts as inactive if refresh fails (expired/revoked tokens)
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.encryption import decrypt_secret, encrypt_secret
from app.models.social_account import SocialAccount, SocialPlatform

logger = logging.getLogger(__name__)


class TokenRefreshService:
    """
    Service that finds and refreshes expiring OAuth tokens for social accounts.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_expiring_accounts(self) -> List[SocialAccount]:
        """
        Return active social accounts whose tokens expire within the configured window.
        Only accounts that have a refresh_token_encrypted are returned (can be refreshed).
        """
        threshold = datetime.now(timezone.utc) + timedelta(
            minutes=settings.TOKEN_REFRESH_BEFORE_EXPIRY_MINUTES
        )
        stmt = (
            select(SocialAccount)
            .where(
                and_(
                    SocialAccount.is_active == True,
                    SocialAccount.token_expires_at <= threshold,
                    SocialAccount.refresh_token_encrypted.is_not(None),
                )
            )
            .limit(50)  # Process at most 50 per cycle to avoid blocking
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def _get_provider(self, platform: SocialPlatform):
        """
        Return the appropriate OAuth provider for a given platform.
        Returns None if the platform has no configured provider.
        """
        from app.core.config import settings as cfg

        platform_str = platform.value if hasattr(platform, "value") else str(platform)

        if platform_str == "BLUESKY" and cfg.BLUESKY_ENABLED:
            from app.integrations.oauth.bluesky_provider import BlueskyOAuthProvider
            return BlueskyOAuthProvider()

        if platform_str == "X" and cfg.TWITTER_ENABLED:
            from app.integrations.oauth.twitter_provider import TwitterOAuthProvider
            return TwitterOAuthProvider()

        if platform_str == "LINKEDIN" and cfg.LINKEDIN_ENABLED:
            from app.integrations.oauth.linkedin_provider import LinkedInOAuthProvider
            return LinkedInOAuthProvider()

        if platform_str == "INSTAGRAM" and cfg.INSTAGRAM_ENABLED:
            from app.integrations.oauth.instagram_provider import InstagramOAuthProvider
            return InstagramOAuthProvider()

        return None

    async def refresh_account_token(self, account: SocialAccount) -> bool:
        """
        Refresh the access token for a single social account.

        Returns:
            True  — token refreshed successfully
            False — refresh failed (token revoked/expired, will mark account inactive)
        """
        provider = self._get_provider(account.platform)
        if not provider:
            logger.info(
                f"TokenRefreshService: no provider configured for {account.platform.value} "
                f"account {account.id}. Skipping."
            )
            return False

        try:
            # Decrypt the current refresh token
            refresh_token_plain = decrypt_secret(account.refresh_token_encrypted)
        except Exception as exc:
            logger.error(
                f"TokenRefreshService: failed to decrypt refresh token for account {account.id}: {exc}"
            )
            return False

        try:
            result = await provider.refresh_token(refresh_token_plain)
        except Exception as exc:
            logger.warning(
                f"TokenRefreshService: token refresh failed for account {account.id} "
                f"({account.platform.value}): {exc}. Marking account inactive."
            )
            account.is_active = False
            self.session.add(account)
            await self.session.commit()
            return False

        # Re-encrypt and store the new access token
        account.access_token_encrypted = encrypt_secret(result.access_token)

        # If the provider rotated the refresh token, store the new one
        if result.refresh_token:
            account.refresh_token_encrypted = encrypt_secret(result.refresh_token)

        # Update expiry
        if result.expires_in:
            account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=result.expires_in)
        else:
            # No expiry provided — clear the field (token has unknown lifetime)
            account.token_expires_at = None

        account.updated_at = datetime.now(timezone.utc)
        self.session.add(account)
        await self.session.commit()

        logger.info(
            f"TokenRefreshService: successfully refreshed token for account {account.id} "
            f"({account.platform.value}). New expiry: {account.token_expires_at}"
        )
        return True

    async def refresh_all_expiring(self) -> dict:
        """
        Find and refresh all accounts with soon-to-expire tokens.

        Returns a summary dict: {"refreshed": N, "failed": N, "skipped": N}
        """
        accounts = await self.get_expiring_accounts()
        logger.info(f"TokenRefreshService: found {len(accounts)} accounts needing refresh.")

        refreshed, failed, skipped = 0, 0, 0
        for account in accounts:
            success = await self.refresh_account_token(account)
            if success:
                refreshed += 1
            else:
                if account.is_active:
                    skipped += 1
                else:
                    failed += 1

        summary = {"refreshed": refreshed, "failed": failed, "skipped": skipped}
        logger.info(f"TokenRefreshService: cycle complete. {summary}")
        return summary
