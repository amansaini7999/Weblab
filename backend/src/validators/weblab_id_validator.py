from __future__ import annotations

import re
from typing import Any, Optional

from models import ValidationResult

_WEBLAB_ID_PATTERN = re.compile(r"^[A-Z0-9_-]+$")


def normalize_weblab_id(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if normalized else None


def validate_weblab_id_format(value: Any) -> ValidationResult:
    normalized = normalize_weblab_id(value)
    errors = []

    if not normalized:
        errors.append("weblabId is required and must be a non-empty string")
        return ValidationResult(is_valid=False, errors=errors)

    if " " in normalized:
        errors.append("weblabId must not contain spaces")

    if len(normalized) > 64:
        errors.append("weblabId must be at most 64 characters")

    if not _WEBLAB_ID_PATTERN.fullmatch(normalized):
        errors.append("weblabId must be uppercase and may contain only A-Z, 0-9, '_' and '-'")

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)
