import sqlite3

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.migrate_sqlite import migrate_sqlite
from backend.models import Base, TicketRecord


def make_sqlite_source(path):
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open')"
        )
        connection.executemany(
            "INSERT INTO tickets(id, title, description, status) VALUES (?, ?, ?, ?)",
            [(7, "Login", "Cannot sign in", "open"), (21, "Export", "CSV fails", "closed")],
        )


@pytest.fixture
def target_engine():
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_sqlite_migration_preserves_data_and_is_repeatable(tmp_path, target_engine):
    source_path = tmp_path / "legacy.db"
    make_sqlite_source(source_path)
    original_bytes = source_path.read_bytes()

    first = migrate_sqlite(source_path, target_engine)
    second = migrate_sqlite(source_path, target_engine)

    assert first == {"source": 2, "inserted": 2, "already_present": 0, "verified": 2}
    assert second == {"source": 2, "inserted": 0, "already_present": 2, "verified": 2}
    assert source_path.read_bytes() == original_bytes
    with Session(target_engine) as session:
        tickets = session.scalars(select(TicketRecord).order_by(TicketRecord.id)).all()
        assert [(t.id, t.title, t.description, t.status, t.ticket_no) for t in tickets] == [
            (7, "Login", "Cannot sign in", "Open", "TEX-000007"),
            (21, "Export", "CSV fails", "Closed", "TEX-000021"),
        ]
        assert all((t.category, t.priority, t.product_id, t.customer_id) == ("General", "Medium", None, None) for t in tickets)


def test_sqlite_migration_detects_id_conflict_and_rolls_back(tmp_path, target_engine):
    source_path = tmp_path / "legacy.db"
    make_sqlite_source(source_path)
    with Session(target_engine) as session, session.begin():
        session.add(
            TicketRecord(
                id=7,
                ticket_no="TEX-000007",
                title="Different",
                description="Conflict",
                status="Open",
                category="General",
                priority="Medium",
            )
        )

    with pytest.raises(ValueError, match="conflicts"):
        migrate_sqlite(source_path, target_engine)
    with Session(target_engine) as session:
        ids = session.scalars(select(TicketRecord.id).order_by(TicketRecord.id)).all()
        assert ids == [7]


def test_sqlite_migration_supports_legacy_schema_without_status(tmp_path, target_engine):
    source_path = tmp_path / "older.db"
    with sqlite3.connect(source_path) as connection:
        connection.execute(
            "CREATE TABLE tickets (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL)"
        )
        connection.execute("INSERT INTO tickets VALUES (4, 'Older', 'Legacy ticket')")

    result = migrate_sqlite(source_path, target_engine)
    assert result["verified"] == 1
    with Session(target_engine) as session:
        ticket = session.get(TicketRecord, 4)
        assert ticket is not None
        assert ticket.status == "Open"


def test_sqlite_migration_rejects_null_status_without_partial_import(tmp_path, target_engine):
    source_path = tmp_path / "null-status.db"
    with sqlite3.connect(source_path) as connection:
        connection.execute(
            "CREATE TABLE tickets (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
            "description TEXT NOT NULL, status TEXT)"
        )
        connection.execute("INSERT INTO tickets VALUES (9, 'Malformed', 'Null state', NULL)")

    with pytest.raises(ValueError, match="ID 9 has a NULL status"):
        migrate_sqlite(source_path, target_engine)
    with Session(target_engine) as session:
        assert session.scalars(select(TicketRecord)).all() == []
