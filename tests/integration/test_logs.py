from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services.audit import AuditStore, get_audit_store


async def test_logs_returns_audit_entries_for_calls() -> None:
    isolated_store = AuditStore()
    app.dependency_overrides[get_audit_store] = lambda: isolated_store

    with patch("src.services.detection.classify_all", new=AsyncMock(return_value=["finance"])):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/detect",
                json={
                    "prompt": "Best ETFs?",
                    "settings": {"health": False, "finance": True, "hr": False, "legal": False},
                },
            )
            response = await client.get("/logs")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    entries = response.json()
    assert len(entries) == 1
    assert entries[0]["endpoint"] == "detect"
    assert entries[0]["detected_topics"] == ["finance"]
