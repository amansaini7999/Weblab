from __future__ import annotations

from typing import Dict, List, Tuple

from models import TreatmentSet, ValidationResult

_ALLOWED_KEYS = {
    TreatmentSet.CT1: {"C", "T1"},
    TreatmentSet.CT1T2: {"C", "T1", "T2"},
}


def validate_splits(treatment_set: TreatmentSet, splits: Dict[str, int]) -> ValidationResult:
    expected_keys = _ALLOWED_KEYS[treatment_set]
    errors: List[str] = []

    if set(splits.keys()) != expected_keys:
        errors.append(f"splits must contain keys: {sorted(expected_keys)}")
        return ValidationResult(is_valid=False, errors=errors)

    for key, value in splits.items():
        if not isinstance(value, int):
            errors.append(f"{key} must be an integer")
            continue
        if value < 0 or value > 100:
            errors.append(f"{key} must be between 0 and 100")

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    values = list(splits.values())
    all_zero = all(value == 0 for value in values)
    total = sum(values)

    if not all_zero and total != 100:
        errors.append("sum of non-zero split configuration must be exactly 100")

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def is_all_zero(splits: Dict[str, int]) -> bool:
    return all(value == 0 for value in splits.values())


def normalize_splits(splits: Dict[str, int]) -> Dict[str, int]:
    return {key: int(value) for key, value in splits.items()}


def treatment_order(treatment_set: TreatmentSet) -> Tuple[str, ...]:
    if treatment_set == TreatmentSet.CT1:
        return ("C", "T1")
    return ("C", "T1", "T2")
