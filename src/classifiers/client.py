import json

from openai import AsyncOpenAI

from src.core.config import settings

_VALID_TOPICS = frozenset({"health", "finance", "legal", "hr"})

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    return _client


_SYSTEM_ALL = (
    "You are a topic classifier for a content security system.\n"
    "Given a user prompt and a list of active topic categories, identify ALL topics present.\n\n"
    "Active topics: {topics}\n\n"
    'Respond ONLY with valid JSON: {{"topics": ["<topic>", ...]}}\n'
    "Use only the exact keys listed. Include a topic only if the prompt clearly relates to it.\n"
    "Return an empty list if no topics match."
)

_SYSTEM_FAST = (
    "You are a topic classifier for a content security system.\n"
    "Given a user prompt and a list of active topic categories, "
    "identify the FIRST topic you find.\n"
    "Stop as soon as you find one match — do not look for more.\n\n"
    "Active topics: {topics}\n\n"
    'Respond ONLY with valid JSON: {{"topics": ["<topic>"]}}\n'
    "Use only the exact keys listed. Return an empty list if no topics match."
)


def _parse(response_text: str, enabled_topics: list[str]) -> list[str]:
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Classifier returned unparseable response: {response_text!r}") from exc
    raw = data.get("topics", []) if isinstance(data, dict) else []
    allowed = _VALID_TOPICS & set(enabled_topics)
    return [t.lower() for t in raw if isinstance(t, str) and t.lower() in allowed]


async def _call(system: str, prompt: str, enabled_topics: list[str]) -> list[str]:
    response = await get_client().chat.completions.create(
        model="gpt-4.1",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return _parse(response.choices[0].message.content or "", enabled_topics)


async def classify_all(prompt: str, enabled_topics: list[str]) -> list[str]:
    """Return all topics from enabled_topics that are present in prompt."""
    return await _call(_SYSTEM_ALL.format(topics=", ".join(enabled_topics)), prompt, enabled_topics)


async def classify_fast(prompt: str, enabled_topics: list[str]) -> list[str]:
    """Return the first matching topic from enabled_topics found in prompt."""
    return (
        await _call(_SYSTEM_FAST.format(topics=", ".join(enabled_topics)), prompt, enabled_topics)
    )[:1]
