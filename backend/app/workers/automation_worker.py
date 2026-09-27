"""
app/workers/automation_worker.py

Background worker that evaluates active automation rules and executes their actions.

Supported trigger_type values:
  - SCHEDULED_TIME  — fires at a cron-like time (condition: {"hour": 9, "minute": 0})
  - POST_PUBLISHED  — fires when a post is published (checked via recent DB state)
  - ALWAYS          — fires every cycle (useful for recurring drafts)

Supported action_type values:
  - GENERATE_DRAFT       — calls ContentGenerationService to create a new draft post
  - SEND_NOTIFICATION    — logs a notification (placeholder for webhook/email)

condition field: JSON string with trigger-specific configuration.
  Example: {"hour": 9, "minute": 0, "project_id": "uuid", "platform": "X"}
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.repositories.automation_repository import AutomationRepository
from app.models.automation_rule import AutomationRule

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _parse_condition(rule: AutomationRule) -> dict:
    """Safely parse the condition JSON field. Returns empty dict on failure."""
    if not rule.condition:
        return {}
    try:
        return json.loads(rule.condition)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"AutomationWorker: rule {rule.id} has invalid condition JSON: {rule.condition!r}")
        return {}


def _should_trigger(rule: AutomationRule, now: datetime) -> bool:
    """
    Evaluate whether a rule should fire in the current cycle.

    ALWAYS        — always returns True
    SCHEDULED_TIME — checks if current UTC hour/minute matches condition
    POST_PUBLISHED — placeholder; would query DB for recent publish events
    """
    condition = _parse_condition(rule)
    trigger = rule.trigger_type.upper()

    if trigger == "ALWAYS":
        return True

    if trigger == "SCHEDULED_TIME":
        target_hour = condition.get("hour")
        target_minute = condition.get("minute", 0)
        if target_hour is None:
            return False
        # Fire if we're within the same minute window
        return now.hour == target_hour and now.minute == target_minute

    if trigger == "POST_PUBLISHED":
        # In a full implementation: query PublishingLog for recent publishes
        # filtered by workspace_id and time window. For now, always False to prevent
        # accidental spam — this requires event-driven architecture to be truly correct.
        logger.info(f"AutomationWorker: POST_PUBLISHED trigger for rule {rule.id} — skipped (needs event bus).")
        return False

    if trigger == "RSS_FEED_UPDATE":
        # Placeholder — would require an RSS fetcher integration
        logger.info(f"AutomationWorker: RSS_FEED_UPDATE trigger for rule {rule.id} — skipped (not implemented).")
        return False

    if trigger == "MENTION":
        # Placeholder — would require polling social APIs for mentions
        logger.info(f"AutomationWorker: MENTION trigger for rule {rule.id} — skipped (not implemented).")
        return False

    logger.warning(f"AutomationWorker: unknown trigger_type '{rule.trigger_type}' for rule {rule.id}. Skipping.")
    return False


async def _execute_action(rule: AutomationRule, session) -> None:
    """
    Execute the action for a triggered rule.
    """
    condition = _parse_condition(rule)
    action = rule.action_type.upper()

    if action == "GENERATE_DRAFT":
        await _action_generate_draft(rule, condition, session)

    elif action == "SEND_NOTIFICATION":
        await _action_send_notification(rule, condition)

    else:
        logger.warning(f"AutomationWorker: unknown action_type '{rule.action_type}' for rule {rule.id}. Skipping.")


async def _action_generate_draft(rule: AutomationRule, condition: dict, session) -> None:
    """
    Execute GENERATE_DRAFT: create a new DRAFT post in the specified project.

    Condition fields:
        project_id (required) — UUID of the project to create the draft in
        platform   (required) — social platform (X, LINKEDIN, INSTAGRAM, etc.)
        topic      (optional) — topic or brief for the AI content generator
    """
    from app.models.post import Post, PostStatus, ContentType
    from app.models.social_account import SocialPlatform
    import uuid

    project_id_str = condition.get("project_id")
    platform_str = condition.get("platform", "X").upper()

    if not project_id_str:
        logger.error(f"AutomationWorker: GENERATE_DRAFT rule {rule.id} missing 'project_id' in condition.")
        return

    try:
        project_id = uuid.UUID(project_id_str)
        platform = SocialPlatform(platform_str)
    except (ValueError, KeyError) as exc:
        logger.error(f"AutomationWorker: GENERATE_DRAFT rule {rule.id} invalid condition: {exc}")
        return

    topic = condition.get("topic", "Create an engaging social media post for our audience.")

    # Create a placeholder draft post — in a full implementation this would
    # call ContentGenerationService to AI-generate the content.
    draft = Post(
        project_id=project_id,
        content=f"[Auto-generated draft] Topic: {topic}",
        title=f"Auto-draft — {rule.name}",
        content_type=ContentType.TEXT,
        status=PostStatus.DRAFT,
        platform=platform,
    )
    session.add(draft)
    await session.commit()
    logger.info(
        f"AutomationWorker: GENERATE_DRAFT created post {draft.id} "
        f"in project {project_id} for rule {rule.id}"
    )


async def _action_send_notification(rule: AutomationRule, condition: dict) -> None:
    """
    Execute SEND_NOTIFICATION: log a notification message.
    In production, this would send an email/webhook/Slack message.

    Condition fields:
        message (optional) — custom message text
        webhook_url (optional) — URL to POST the notification to
    """
    import httpx

    message = condition.get("message", f"Automation rule '{rule.name}' triggered.")
    webhook_url = condition.get("webhook_url")

    logger.info(f"AutomationWorker: SEND_NOTIFICATION for rule {rule.id} — message: {message}")

    if webhook_url:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(webhook_url, json={"message": message, "rule_id": str(rule.id)})
            logger.info(f"AutomationWorker: webhook notification sent to {webhook_url}")
        except Exception as exc:
            logger.warning(f"AutomationWorker: webhook to {webhook_url} failed: {exc}")


async def process_automations():
    """Fetch active rules and execute those whose triggers are satisfied."""
    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as session:
        automation_repo = AutomationRepository(session)

        try:
            rules = await automation_repo.get_all_active()
        except Exception as exc:
            logger.error(f"AutomationWorker: error fetching rules: {exc}")
            return

        logger.info(f"AutomationWorker: evaluating {len(rules)} active rules.")

        for rule in rules:
            try:
                if _should_trigger(rule, now):
                    logger.info(f"AutomationWorker: rule {rule.id} ({rule.name}) triggered. Executing {rule.action_type}.")
                    await _execute_action(rule, session)
            except Exception as exc:
                logger.error(f"AutomationWorker: error executing rule {rule.id}: {exc}", exc_info=True)


shutdown_event = asyncio.Event()


def handle_shutdown(sig, frame):
    logger.info(f"Received signal {sig}. Shutting down gracefully...")
    shutdown_event.set()


async def worker_loop(interval_seconds: int = 60):
    """Main loop for the automation worker. Runs every 60 seconds."""
    logger.info("Automation worker started.")

    import signal
    try:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: shutdown_event.set())
    except (NotImplementedError, AttributeError):
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    while not shutdown_event.is_set():
        try:
            await process_automations()
        except Exception as exc:
            logger.error(f"Worker loop error: {exc}")

        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass

    logger.info("Automation worker stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Automation worker stopped.")
