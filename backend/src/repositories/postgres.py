from __future__ import annotations

import json
from typing import Dict, List, Optional

from models import AssignmentMode, AuditEvent, PublishedConfig, TreatmentSet, Weblab
from .base import Repository

try:
    import psycopg
except ImportError:  # pragma: no cover
    psycopg = None


class PostgresRepository(Repository):
    def __init__(self, database_url: str) -> None:
        if not psycopg:
            raise RuntimeError("psycopg is required for PostgresRepository")
        self.database_url = database_url

    def _connect(self):
        return psycopg.connect(self.database_url)

    def _row_to_weblab(self, row) -> Weblab:
        return Weblab(
            id=row["id"],
            name=row["name"],
            assignment_mode=AssignmentMode(row["assignment_mode"]),
            treatment_set=TreatmentSet(row["treatment_set"]),
            allocation_map=row.get("allocation_map"),
            active_version=row.get("active_version"),
        )

    def create_weblab(self, weblab: Weblab) -> Weblab:
        with self._connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            try:
                cur.execute(
                    """
                    insert into weblabs (id, name, assignment_mode, treatment_set, allocation_map, active_version)
                    values (%s, %s, %s, %s, %s::jsonb, %s)
                    """,
                    (
                        weblab.id,
                        weblab.name,
                        weblab.assignment_mode.value,
                        weblab.treatment_set.value,
                        json.dumps(weblab.allocation_map),
                        weblab.active_version,
                    ),
                )
            except Exception:
                cur.execute(
                    """
                    insert into weblabs (id, name, assignment_mode, treatment_set)
                    values (%s, %s, %s, %s)
                    """,
                    (
                        weblab.id,
                        weblab.name,
                        weblab.assignment_mode.value,
                        weblab.treatment_set.value,
                    ),
                )
        return weblab

    def list_weblabs(self) -> List[Weblab]:
        with self._connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("select * from weblabs order by created_at desc")
            rows = cur.fetchall()
        return [self._row_to_weblab(row) for row in rows]

    def get_weblab(self, weblab_id: str) -> Optional[Weblab]:
        with self._connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("select * from weblabs where id = %s", (weblab_id,))
            row = cur.fetchone()
        if not row:
            return None
        return self._row_to_weblab(row)

    def update_allocation(self, weblab_id: str, allocation_map: Dict[str, Dict[str, int]]) -> Optional[Weblab]:
        with self._connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(
                """
                update weblabs
                set allocation_map = %s::jsonb, updated_at = now()
                where id = %s
                returning *
                """,
                (json.dumps(allocation_map), weblab_id),
            )
            row = cur.fetchone()
        if not row:
            return None
        return self._row_to_weblab(row)

    def publish(self, config: PublishedConfig) -> Optional[Weblab]:
        with self._connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(
                """
                insert into weblab_versions (weblab_id, version, splits)
                values (%s, %s, %s::jsonb)
                """,
                (config.weblab_id, config.version, json.dumps(config.allocation_map)),
            )
            cur.execute(
                """
                update weblabs
                set active_version = %s, updated_at = now()
                where id = %s
                returning *
                """,
                (config.version, config.weblab_id),
            )
            row = cur.fetchone()
        if not row:
            return None
        return self._row_to_weblab(row)

    def get_active_config(self, weblab_id: str, active_version: int) -> Optional[PublishedConfig]:
        with self._connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(
                """
                select weblab_id, version, splits
                from weblab_versions
                where weblab_id = %s and version = %s
                """,
                (weblab_id, active_version),
            )
            row = cur.fetchone()
        if not row:
            return None
        return PublishedConfig(weblab_id=row["weblab_id"], version=row["version"], allocation_map=row["splits"])

    def add_audit_event(self, event: AuditEvent) -> None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                insert into weblab_audit (id, weblab_id, action, detail)
                values (%s, %s, %s, %s)
                """,
                (event.id, event.weblab_id, event.action, event.detail),
            )
