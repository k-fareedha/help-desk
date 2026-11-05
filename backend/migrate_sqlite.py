"""Copy the starter SQLite tickets into the configured database, safely repeatably."""

import argparse
import sqlite3
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.main import get_engine
from backend.models import TicketRecord

STATUS_ALIASES = {"open": "Open", "closed": "Closed"}


def _normalize_status(value: str) -> str:
    return STATUS_ALIASES.get(value.lower(), value)


def migrate_sqlite(sqlite_path: Path, target_engine: Engine) -> dict[str, int]:
    """Import tickets without modifying the source or overwriting target rows."""
    if not sqlite_path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    source_uri = f"file:{sqlite_path.resolve()}?mode=ro"
    source = sqlite3.connect(source_uri, uri=True)
    source.row_factory = sqlite3.Row
    try:
        tables = {
            row[0]
            for row in source.execute("SELECT name FROM sqlite_master WHERE type = ?", ("table",))
        }
        if "tickets" not in tables:
            raise ValueError("SQLite source does not contain a tickets table")
        columns = {row[1] for row in source.execute("PRAGMA table_info(tickets)")}
        required = {"id", "title", "description"}
        if not required.issubset(columns):
            raise ValueError(f"SQLite tickets table is missing columns: {sorted(required - columns)}")
        status_expr = "status" if "status" in columns else "'open' AS status"
        source_tickets = source.execute(
            f"SELECT id, title, description, {status_expr} FROM tickets ORDER BY id"
        ).fetchall()
    finally:
        source.close()

    inserted = 0
    existing = 0
    factory = sessionmaker(bind=target_engine, expire_on_commit=False)
    with factory() as session, session.begin():
        for row in source_tickets:
            if row["status"] is None:
                raise ValueError(f"SQLite ticket ID {row['id']} has a NULL status")
            record = session.get(TicketRecord, row["id"])
            values = {
                "title": row["title"],
                "description": row["description"],
                "status": _normalize_status(row["status"]),
            }
            if record is not None:
                if any(getattr(record, field) != value for field, value in values.items()):
                    raise ValueError(f"Target ticket ID {row['id']} conflicts with the SQLite source")
                existing += 1
                continue
            session.add(
                TicketRecord(
                    id=row["id"],
                    ticket_no=f"TEX-{row['id']:06d}",
                    category="General",
                    priority="Medium",
                    **values,
                )
            )
            inserted += 1
        session.flush()

        if target_engine.dialect.name == "postgresql" and source_tickets:
            session.execute(
                text(
                    "SELECT setval(pg_get_serial_sequence('tickets', 'id'), "
                    "GREATEST((SELECT COALESCE(MAX(id), 1) FROM tickets), 1), "
                    "(SELECT COUNT(*) > 0 FROM tickets))"
                )
            )

    with factory() as verify_session:
        verified = 0
        for row in source_tickets:
            record = verify_session.get(TicketRecord, row["id"])
            if record is not None and (
                record.title == row["title"]
                and record.description == row["description"]
                and record.status == _normalize_status(row["status"])
            ):
                verified += 1
        if verified != len(source_tickets):
            raise RuntimeError(
                f"Migration verification failed: {verified}/{len(source_tickets)} source tickets match"
            )

    return {"source": len(source_tickets), "inserted": inserted, "already_present": existing, "verified": verified}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=Path(__file__).with_name("helpdesk.db"),
        help="Read-only path to the existing SQLite database (default: backend/helpdesk.db)",
    )
    args = parser.parse_args()
    result = migrate_sqlite(args.sqlite_path, get_engine())
    print(
        "SQLite import complete: "
        f"source={result['source']}, inserted={result['inserted']}, "
        f"already_present={result['already_present']}, verified={result['verified']}"
    )


if __name__ == "__main__":
    main()
