from fastapi import APIRouter, Depends

from src.models.detection import DetectionResult, PromptRequest
from src.services import detection as svc
from src.services.audit import AuditStore, get_audit_store

router = APIRouter(tags=["detection"])


@router.post("/detect")
async def detect(
    request: PromptRequest, store: AuditStore = Depends(get_audit_store)
) -> DetectionResult:
    return await svc.detect(request, store)


@router.post("/protect")
async def protect(
    request: PromptRequest, store: AuditStore = Depends(get_audit_store)
) -> DetectionResult:
    return await svc.protect(request, store)
