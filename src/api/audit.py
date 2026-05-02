from fastapi import APIRouter, Depends

from src.models.detection import AuditEntry
from src.services.audit import AuditStore, get_audit_store

router = APIRouter(tags=["audit"])


@router.get("/logs")
async def logs(store: AuditStore = Depends(get_audit_store)) -> list[AuditEntry]:
    return store.all()
