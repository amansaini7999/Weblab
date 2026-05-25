from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PublishedConfig:
    weblab_id: str
    version: int
    allocation_map: Dict[str, Dict[str, int]]
