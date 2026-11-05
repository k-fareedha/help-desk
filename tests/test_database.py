import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL is not configured")


def test_configured_database_connectivity():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
            assert connection.execute(text("SELECT to_regclass('public.tickets')")).scalar_one()
    finally:
        engine.dispose()


def test_multi_product_schema_and_seed_data_are_present():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            tables = {
                name: connection.execute(text("SELECT to_regclass(:table_name)"), {"table_name": f"public.{name}"}).scalar_one()
                for name in ("products", "product_modules")
            }
            assert all(tables.values()), f"Expected products schema tables, found {tables}"
            assert connection.execute(text("SELECT count(*) FROM products")).scalar_one() == 3
            assert connection.execute(text("SELECT count(*) FROM product_modules")).scalar_one() == 17
    finally:
        engine.dispose()


def test_postgresql_transaction_rolls_back_temporary_work():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    try:
        with Session(engine) as session:
            with pytest.raises(RuntimeError, match="force rollback"):
                with session.begin():
                    session.execute(text("CREATE TEMP TABLE rollback_probe (value INTEGER)"))
                    session.execute(text("INSERT INTO rollback_probe VALUES (1)"))
                    raise RuntimeError("force rollback")
            assert session.execute(
                text("SELECT to_regclass('pg_temp.rollback_probe')")
            ).scalar_one() is None
    finally:
        engine.dispose()
