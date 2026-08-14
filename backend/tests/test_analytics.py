import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.schemas.analytics import AnalyticsSnapshot, AnalyticsSummary
from app.models.post_analytics import PostAnalytics
from app.services.analytics_service import AnalyticsService

@pytest.fixture
def mock_mcp_client():
    client = AsyncMock()
    return client

@pytest.fixture
def analytics_service(mock_mcp_client):
    session = AsyncMock()
    service = AnalyticsService(session=session, mcp_client=mock_mcp_client)
    # Mock repos
    service.analytics_repo = AsyncMock()
    service.post_repo = AsyncMock()
    return service

def test_calculate_engagement_rate_with_impressions(analytics_service):
    snapshot = AnalyticsSnapshot(
        impressions=1000,
        likes=50,
        comments=10,
        shares=5,
        saves=2,
        clicks=0
    )
    # total engagements = 50 + 10 + 5 + 2 = 67
    # 67 / 1000 = 0.067 -> 6.7%
    rate = analytics_service.calculate_engagement_rate(snapshot, None)
    assert rate == 6.7

def test_calculate_engagement_rate_with_views(analytics_service):
    snapshot = AnalyticsSnapshot(
        views=500,
        likes=10,
        comments=0,
        shares=0
    )
    # total engagements = 10
    # 10 / 500 = 0.02 -> 2.0%
    rate = analytics_service.calculate_engagement_rate(snapshot, None)
    assert rate == 2.0

def test_calculate_engagement_rate_with_followers(analytics_service):
    snapshot = AnalyticsSnapshot(
        likes=10,
        comments=10
    )
    # total = 20, followers = 200
    # 20 / 200 = 0.1 -> 10.0%
    rate = analytics_service.calculate_engagement_rate(snapshot, 200)
    assert rate == 10.0

def test_calculate_engagement_rate_no_denominator(analytics_service):
    snapshot = AnalyticsSnapshot(likes=100)
    rate = analytics_service.calculate_engagement_rate(snapshot, None)
    assert rate is None
