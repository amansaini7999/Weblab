from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Optional

from models import AssignmentMode, AuditEvent, PublishedConfig, TreatmentSet, Weblab
from errors import NotFoundError, ValidationError
from repositories import Repository
from utils import resolve_treatment
from validators import normalize_splits, normalize_weblab_id, validate_splits, validate_weblab_id_format


class WeblabService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def create_weblab(self, payload: Dict) -> Dict:
        id_validation_result = self.validate_weblab_id({"weblabId": payload.get("weblabId")})
        if not id_validation_result.get("isValid", False):
            raise ValidationError(id_validation_result.get("errors", ["weblabId is invalid"]))

        weblab_id = id_validation_result.get("weblabId")
        if not isinstance(weblab_id, str) or not weblab_id:
            raise ValidationError(["weblabId is required and must be a non-empty string"])

        assignment_mode = AssignmentMode(payload["assignmentMode"])
        treatment_set = TreatmentSet(payload["treatmentSet"])

        weblab = Weblab(
            id=weblab_id,
            name=payload["name"],
            assignment_mode=assignment_mode,
            treatment_set=treatment_set,
            allocation_map=None,
        )
        self.repository.create_weblab(weblab)
        self._record_audit_event(AuditEvent(weblab_id=weblab.id, action="create", detail="weblab created"))
        return self._serialize_weblab(weblab)

    def validate_weblab_id(self, payload: Dict) -> Dict:
        weblab_id_value = payload.get("weblabId")
        format_validation = validate_weblab_id_format(weblab_id_value)
        normalized = normalize_weblab_id(weblab_id_value)

        if not format_validation.is_valid or normalized is None:
            return {
                "isValid": False,
                "isUnique": False,
                "errors": format_validation.errors,
            }

        is_unique = self.repository.get_weblab(normalized) is None
        errors = [] if is_unique else ["weblabId already exists"]
        return {
            "weblabId": normalized,
            "isValid": is_unique,
            "isUnique": is_unique,
            "errors": errors,
        }

    def list_weblabs(self):
        return [self._serialize_weblab(item) for item in self.repository.list_weblabs()]

    def get_weblab(self, weblab_id: str) -> Dict:
        weblab = self.repository.get_weblab(weblab_id)
        if not weblab:
            raise NotFoundError("weblab not found")
        return self._serialize_weblab(weblab)

    def update_allocation(self, weblab_id: str, payload: Dict) -> Dict:
        weblab = self.repository.get_weblab(weblab_id)
        if not weblab:
            raise NotFoundError("weblab not found")

        region_id = payload.get("regionId")
        stamp = payload.get("stamp")
        if not isinstance(region_id, str) or not region_id.strip():
            raise ValidationError(["regionId is required for allocation update"])
        if not isinstance(stamp, str) or not stamp.strip():
            raise ValidationError(["stamp is required for allocation update"])

        splits = normalize_splits(payload["splits"])
        validation = validate_splits(weblab.treatment_set, splits)
        if not validation.is_valid:
            raise ValidationError(validation.errors)

        allocation_key = f"{region_id.strip()}|{stamp.strip()}"
        allocation_map = dict(weblab.allocation_map or {})
        allocation_map[allocation_key] = splits

        updated = self.repository.update_allocation(weblab_id, allocation_map)
        if not updated:
            raise NotFoundError("weblab not found")

        self._record_audit_event(AuditEvent(weblab_id=weblab_id, action="update_allocation", detail=f"allocation updated for {allocation_key}"))
        return self._serialize_weblab(updated)

    def publish(self, weblab_id: str) -> Dict:
        weblab = self.repository.get_weblab(weblab_id)
        if not weblab:
            raise NotFoundError("weblab not found")

        if not weblab.allocation_map:
            raise ValidationError(["no allocation configured; call update allocation first"])

        for allocation_key, splits in weblab.allocation_map.items():
            validation = validate_splits(weblab.treatment_set, splits)
            if not validation.is_valid:
                raise ValidationError([f"invalid allocation for {allocation_key}: {', '.join(validation.errors)}"])

        next_version = (weblab.active_version or 0) + 1
        published = PublishedConfig(weblab_id=weblab_id, version=next_version, allocation_map=weblab.allocation_map)
        updated = self.repository.publish(published)
        if not updated:
            raise NotFoundError("weblab not found")

        self._record_audit_event(AuditEvent(weblab_id=weblab_id, action="publish", detail=f"version {next_version}"))
        return self._serialize_weblab(updated)

    def validate_config(self, weblab_id: str, payload: Optional[Dict] = None) -> Dict:
        weblab = self.repository.get_weblab(weblab_id)
        if not weblab:
            raise NotFoundError("weblab not found")

        if payload and payload.get("regionId") and payload.get("stamp") and payload.get("splits") is not None:
            normalized = normalize_splits(payload["splits"])
            validation = validate_splits(weblab.treatment_set, normalized)
            return {"isValid": validation.is_valid, "errors": validation.errors}

        allocation_map = weblab.allocation_map or {}
        errors = []
        for allocation_key, splits in allocation_map.items():
            validation = validate_splits(weblab.treatment_set, splits)
            if not validation.is_valid:
                errors.extend([f"{allocation_key}: {error}" for error in validation.errors])

        return {"isValid": len(errors) == 0, "errors": errors}

    def get_treatment(self, weblab_id: str, payload: Dict) -> Dict:
        weblab = self.repository.get_weblab(weblab_id)
        if not weblab:
            raise NotFoundError("weblab not found")

        region_id = payload.get("regionId")
        stamp = payload.get("stamp")
        if not isinstance(region_id, str) or not region_id.strip():
            raise ValidationError(["regionId is required for getTreatment"])
        if not isinstance(stamp, str) or not stamp.strip():
            raise ValidationError(["stamp is required for getTreatment"])

        allocation_key = f"{region_id.strip()}|{stamp.strip()}"
        allocation_map = weblab.allocation_map or {}
        splits = allocation_map.get(allocation_key)
        if not splits:
            return {
                "weblabId": weblab.id,
                "activeVersion": weblab.active_version,
                "treatment": None,
            }

        sticky_key = self._build_sticky_key(weblab.assignment_mode, payload)
        treatment = resolve_treatment(
            weblab_id=weblab.id,
            sticky_key=sticky_key,
            treatment_set=weblab.treatment_set,
            splits=splits,
        )

        return {
            "weblabId": weblab.id,
            "activeVersion": weblab.active_version,
            "treatment": treatment,
        }

    def _build_sticky_key(self, assignment_mode: AssignmentMode, payload: Dict) -> str:
        if assignment_mode == AssignmentMode.SESSION_BASED:
            session_id = payload.get("sessionId")
            if not session_id:
                raise ValidationError(["sessionId is required for session_based weblab"])
            region_id = payload.get("regionId")
            stamp = payload.get("stamp")
            return f"{session_id}|{region_id}|{stamp}"

        user_id = payload.get("userId")
        region_id = payload.get("regionId")
        stamp = payload.get("stamp")
        missing = [name for name, value in (("userId", user_id), ("regionId", region_id), ("stamp", stamp)) if not value]
        if missing:
            raise ValidationError([f"{', '.join(missing)} are required for user_based weblab"])
        return f"{user_id}|{region_id}|{stamp}"

    def _serialize_weblab(self, weblab: Weblab) -> Dict:
        result = asdict(weblab)
        result["assignmentMode"] = result.pop("assignment_mode")
        result["treatmentSet"] = result.pop("treatment_set")
        result["allocationMap"] = result.pop("allocation_map")
        result["activeVersion"] = result.pop("active_version")
        return result

    def _record_audit_event(self, event: AuditEvent) -> None:
        try:
            self.repository.add_audit_event(event)
        except Exception:
            return
