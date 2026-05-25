from __future__ import annotations

import os

from .base import Repository
from .in_memory import InMemoryRepository
from .postgres import PostgresRepository


def build_repository() -> Repository:
    database_url = os.getenv("WEBLAB_DATABASE_URL")
    if database_url:
        return PostgresRepository(database_url)
    return InMemoryRepository()
