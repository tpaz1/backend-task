from src.classifiers.client import classify_all, classify_fast
from src.models.detection import AuditEntry, DetectionResult, PromptRequest
from src.services.audit import AuditStore


def _enabled_topics(request: PromptRequest) -> list[str]:
    s = request.settings
    return [
        t
        for t, active in [
            ("health", s.health),
            ("finance", s.finance),
            ("legal", s.legal),
            ("hr", s.hr),
        ]
        if active
    ]


async def detect(request: PromptRequest, store: AuditStore) -> DetectionResult:
    """Classify all topics present in prompt and record the call."""
    enabled = _enabled_topics(request)
    topics = await classify_all(request.prompt, enabled) if enabled else []
    store.append(AuditEntry(endpoint="detect", prompt=request.prompt, detected_topics=topics))
    return DetectionResult(detected_topics=topics)


async def protect(request: PromptRequest, store: AuditStore) -> DetectionResult:
    """Return the first matching topic as fast as possible and record the call."""
    enabled = _enabled_topics(request)
    topics = await classify_fast(request.prompt, enabled) if enabled else []
    store.append(AuditEntry(endpoint="protect", prompt=request.prompt, detected_topics=topics))
    return DetectionResult(detected_topics=topics)
