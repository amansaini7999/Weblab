from __future__ import annotations

from typing import Dict, List, Optional

from models import AuditEvent, PublishedConfig, Weblab
from .base import Repository


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self.weblabs: Dict[str, Weblab] = {}
        self.published: Dict[str, Dict[int, PublishedConfig]] = {}
        self.audit_events: List[AuditEvent] = []

    def create_weblab(self, weblab: Weblab) -> Weblab:
        self.weblabs[weblab.id] = weblab
        return weblab

    def list_weblabs(self) -> List[Weblab]:
        return list(self.weblabs.values())

    def get_weblab(self, weblab_id: str) -> Optional[Weblab]:
        return self.weblabs.get(weblab_id)

    def update_allocation(self, weblab_id: str, allocation_map: Dict[str, Dict[str, int]]) -> Optional[Weblab]:
        weblab = self.weblabs.get(weblab_id)
        if not weblab:
            return None
        weblab.allocation_map = allocation_map
        return weblab

    def publish(self, config: PublishedConfig) -> Optional[Weblab]:
        weblab = self.weblabs.get(config.weblab_id)
        if not weblab:
            return None
        versions = self.published.setdefault(config.weblab_id, {})
        versions[config.version] = config
        weblab.active_version = config.version
        return weblab

    def get_active_config(self, weblab_id: str, active_version: int) -> Optional[PublishedConfig]:
        return self.published.get(weblab_id, {}).get(active_version)

    def add_audit_event(self, event: AuditEvent) -> None:
        self.audit_events.append(event)
