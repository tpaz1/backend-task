from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.classifiers.client import classify_all, classify_fast


def _completion(content: str) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    result = MagicMock()
    result.choices = [choice]
    return result


@pytest.mark.parametrize(
    "prompt, enabled, llm_json, expected",
    [
        (
            "How do I treat depression?",
            ["health", "finance"],
            '{"topics": ["health"]}',
            ["health"],
        ),
        (
            "Salary negotiation advice for a nurse",
            ["health", "hr", "finance"],
            '{"topics": ["health", "hr"]}',
            ["health", "hr"],
        ),
        (
            "Best stocks to buy this week",
            ["health"],
            '{"topics": ["finance"]}',  # LLM returns a disabled topic
            [],
        ),
        (
            "What is the weather in Tel Aviv?",
            ["health", "finance"],
            '{"topics": []}',
            [],
        ),
    ],
)
async def test_classify_all_decision_boundary(
    prompt: str, enabled: list[str], llm_json: str, expected: list[str]
) -> None:
    mock_create = AsyncMock(return_value=_completion(llm_json))
    with patch("src.classifiers.client.get_client") as mock_get_client:
        mock_get_client.return_value.chat.completions.create = mock_create
        result = await classify_all(prompt, enabled)
    assert result == expected


async def test_classify_all_raises_on_malformed_llm_response() -> None:
    mock_create = AsyncMock(return_value=_completion("not valid json {{{"))
    with patch("src.classifiers.client.get_client") as mock_get_client:
        mock_get_client.return_value.chat.completions.create = mock_create
        with pytest.raises(ValueError):
            await classify_all("test prompt", ["health"])


@pytest.mark.parametrize(
    "llm_json, enabled, expected",
    [
        ('{"topics": ["hr"]}', ["health", "hr"], ["hr"]),
        ('{"topics": ["health", "hr"]}', ["health", "hr"], ["health"]),  # LLM returns 2, must get 1
    ],
)
async def test_classify_fast_returns_at_most_one_topic(
    llm_json: str, enabled: list[str], expected: list[str]
) -> None:
    mock_create = AsyncMock(return_value=_completion(llm_json))
    with patch("src.classifiers.client.get_client") as mock_get_client:
        mock_get_client.return_value.chat.completions.create = mock_create
        result = await classify_fast("Hiring a new nurse", enabled)
    assert result == expected
