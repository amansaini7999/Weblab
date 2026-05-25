from __future__ import annotations

import hashlib
from typing import Dict, Optional

from models import TreatmentSet
from validators import is_all_zero

_BUCKETS = 10_000


def _bucket_for_key(weblab_id: str, sticky_key: str) -> int:
    digest = hashlib.sha256(f"{weblab_id}:{sticky_key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % _BUCKETS


def resolve_treatment(
    weblab_id: str,
    sticky_key: str,
    treatment_set: TreatmentSet,
    splits: Dict[str, int],
) -> Optional[str]:
    if is_all_zero(splits):
        return None

    bucket = _bucket_for_key(weblab_id, sticky_key)

    t1_upper = splits.get("T1", 0) * 100

    if treatment_set == TreatmentSet.CT1:
        if bucket < t1_upper:
            return "T1"
        return "C"

    t2_upper_size = splits.get("T2", 0) * 100
    if bucket < t1_upper:
        return "T1"
    if bucket >= (_BUCKETS - t2_upper_size):
        return "T2"
    return "C"
