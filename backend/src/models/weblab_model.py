from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .assignment_mode import AssignmentMode
from .treatment_set import TreatmentSet


@dataclass
class Weblab:
    id: str
    name: str
    assignment_mode: AssignmentMode
    treatment_set: TreatmentSet
    allocation_map: Optional[Dict[str, Dict[str, int]]] = None
    active_version: Optional[int] = None
