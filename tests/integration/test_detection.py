from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services.audit import AuditStore, get_audit_store


def _override_store() -> AuditStore:
    return AuditStore()


async def test_detect_returns_matched_topics() -> None:
    with patch("src.services.detection.classify_all", new=AsyncMock(return_value=["health"])):
        app.dependency_overrides[get_audit_store] = _override_store
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/detect",
                json={"prompt": "How do I treat depression?", "settings": {"health": True, "finance": False, "hr": False, "legal": False}},
            )
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"detected_topics": ["health"]}


async def test_protect_returns_at_most_one_topic() -> None:
    with patch("src.services.detection.classify_fast", new=AsyncMock(return_value=["hr"])):
        app.dependency_overrides[get_audit_store] = _override_store
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/protect",
                json={"prompt": "Hiring a new engineer", "settings": {"health": False, "finance": False, "hr": True, "legal": False}},
            )
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"detected_topics": ["hr"]}
