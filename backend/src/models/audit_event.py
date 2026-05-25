from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class AuditEvent:
    weblab_id: str
    action: str
    detail: str
    id: str = field(default_factory=lambda: str(uuid4()))
