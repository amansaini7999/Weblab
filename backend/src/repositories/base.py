from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from models import AuditEvent, PublishedConfig, Weblab


class Repository(ABC):
    @abstractmethod
    def create_weblab(self, weblab: Weblab) -> Weblab:
        raise NotImplementedError

    @abstractmethod
    def list_weblabs(self) -> List[Weblab]:
        raise NotImplementedError

    @abstractmethod
    def get_weblab(self, weblab_id: str) -> Optional[Weblab]:
        raise NotImplementedError

    @abstractmethod
    def update_allocation(self, weblab_id: str, allocation_map: Dict[str, Dict[str, int]]) -> Optional[Weblab]:
        raise NotImplementedError

    @abstractmethod
    def publish(self, config: PublishedConfig) -> Optional[Weblab]:
        raise NotImplementedError

    @abstractmethod
    def get_active_config(self, weblab_id: str, active_version: int) -> Optional[PublishedConfig]:
        raise NotImplementedError

    @abstractmethod
    def add_audit_event(self, event: AuditEvent) -> None:
        raise NotImplementedError
