from src.models.detection import AuditEntry


class AuditStore:
    """Append-only in-memory audit log for the lifetime of the process."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def append(self, entry: AuditEntry) -> None:
        self._entries.append(entry)

    def all(self) -> list[AuditEntry]:
        return list(self._entries)


_store = AuditStore()


def get_audit_store() -> AuditStore:
    return _store
