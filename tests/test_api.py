import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.main import app, get_db
from backend.models import Base, CustomerProduct, TicketHistory, TicketRecord


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    app.state.test_engine = engine

    def override_get_db():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def create_product(client, name="Vanforces", code="VF"):
    response = client.post("/api/v1/products", json={"name": name, "code": code})
    assert response.status_code == 201, response.text
    return response.json()


def create_module(client, product_id, name="Mobile Sales", code="MOBILE_SALES"):
    response = client.post(
        f"/api/v1/products/{product_id}/modules",
        json={"name": name, "code": code},
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_ticket(client, product_id, **overrides):
    payload = {
        "product_id": product_id,
        "title": "Cannot sign in",
        "description": "Login returns an error",
        "category": "Bug",
        "priority": "High",
    }
    payload.update(overrides)
    return client.post("/api/v1/tickets", json=payload)


def test_product_uniqueness_and_module_code_scope(client):
    product = create_product(client)
    duplicate = client.post("/api/v1/products", json={"name": "Other", "code": "VF"})
    assert duplicate.status_code == 409

    module = create_module(client, product["id"])
    conflict = client.post(
        f"/api/v1/products/{product['id']}/modules",
        json={"name": "Mobile Sales Clone", "code": "MOBILE_SALES"},
    )
    assert conflict.status_code == 409
    assert client.get(f"/api/v1/products/{product['id']}/modules").json()[0]["id"] == module["id"]


def test_customer_membership_and_product_validation(client):
    first = create_product(client)
    create_product(client, "Taskforce", "TF")
    second = create_product(client, "Speak Order", "SO")
    customer_response = client.post(
        "/api/v1/customers",
        json={"name": "Example customer", "code": "EXAMPLE", "product_ids": [first["id"]]},
    )
    assert customer_response.status_code == 201
    customer = customer_response.json()
    assert customer["product_ids"] == [first["id"]]

    replaced = client.put(
        f"/api/v1/customers/{customer['id']}/products",
        json={"product_ids": [first["id"]]},
    )
    assert replaced.status_code == 200
    assert replaced.json()["product_ids"] == [first["id"]]
    duplicate_ids = client.put(
        f"/api/v1/customers/{customer['id']}/products",
        json={"product_ids": [first["id"], first["id"]]},
    )
    assert duplicate_ids.status_code == 422

    ticket = create_ticket(client, first["id"], customer_id=customer["id"])
    assert ticket.status_code == 201
    wrong_product = create_ticket(client, second["id"], customer_id=customer["id"])
    assert wrong_product.status_code == 422


def test_customer_patch_membership_and_profile_are_atomic_with_ticket_fk(client):
    first = create_product(client)
    second = create_product(client, "Taskforce", "TF")
    customer = client.post(
        "/api/v1/customers",
        json={"name": "Original name", "code": "EXAMPLE", "product_ids": [first["id"], second["id"]]},
    ).json()
    ticket = create_ticket(client, first["id"], customer_id=customer["id"])
    assert ticket.status_code == 201

    rejected = client.patch(
        f"/api/v1/customers/{customer['id']}",
        json={"name": "Changed name", "product_ids": [second["id"]]},
    )
    assert rejected.status_code == 409
    unchanged = client.get(f"/api/v1/customers/{customer['id']}").json()
    assert unchanged["name"] == "Original name"
    assert unchanged["product_ids"] == [first["id"], second["id"]]


def test_customer_patch_rejects_invalid_or_duplicate_product_ids(client):
    product = create_product(client)
    customer = client.post(
        "/api/v1/customers",
        json={"name": "Example", "code": "EXAMPLE", "product_ids": [product["id"]]},
    ).json()

    duplicate_ids = client.patch(
        f"/api/v1/customers/{customer['id']}",
        json={"name": "Changed", "product_ids": [product["id"], product["id"]]},
    )
    assert duplicate_ids.status_code == 422
    unknown_id = client.patch(
        f"/api/v1/customers/{customer['id']}",
        json={"name": "Changed", "product_ids": [product["id"] + 999]},
    )
    assert unknown_id.status_code == 422
    unchanged = client.get(f"/api/v1/customers/{customer['id']}").json()
    assert unchanged["name"] == "Example"
    assert unchanged["product_ids"] == [product["id"]]


def test_ticket_creation_module_validation_and_detail(client):
    product = create_product(client)
    module = create_module(client, product["id"])
    created = create_ticket(client, product["id"], module_id=module["id"])
    assert created.status_code == 201, created.text
    ticket = created.json()
    assert ticket["ticket_no"] == "TEX-000001"
    assert ticket["module_name"] == "Mobile Sales"
    assert ticket["status"] == "Open"
    assert ticket["resolved_at"] is None

    second_product = create_product(client, "Speak Order", "SO")
    wrong_module = create_ticket(client, second_product["id"], module_id=module["id"])
    assert wrong_module.status_code == 422
    assert client.get(f"/api/v1/tickets/{ticket['id']}").json()["title"] == "Cannot sign in"


def test_ticket_assignee_filters_pagination_and_dashboard(client):
    first = create_product(client)
    second = create_product(client, "Taskforce", "TF")
    assignee_response = client.post("/api/v1/assignees", json={"name": "Demo Engineer"})
    assert assignee_response.status_code == 201
    assignee = assignee_response.json()
    assert client.patch(f"/api/v1/assignees/{assignee['id']}", json={"email": "not-an-email"}).status_code == 422
    assert client.patch(
        f"/api/v1/assignees/{assignee['id']}", json={"email": "demo@example.test"}
    ).status_code == 200
    assert client.get("/api/v1/assignees").json()[0]["id"] == assignee["id"]

    assert create_ticket(client, first["id"], assigned_to=assignee["id"], priority="Critical").status_code == 201
    assert create_ticket(client, first["id"], title="Password reset", category="Technical Support").status_code == 201
    assert create_ticket(client, second["id"], title="Task assigned").status_code == 201

    page = client.get("/api/v1/tickets", params={"product_id": first["id"], "page": 1, "page_size": 1})
    assert page.status_code == 200
    assert page.json()["total"] == 2
    assert len(page.json()["items"]) == 1
    assert page.json()["page_size"] == 1
    search = client.get("/api/v1/tickets", params={"q": "Password"}).json()
    assert search["total"] == 1

    summary = client.get("/api/v1/dashboard/summary", params={"product_id": first["id"]}).json()
    assert summary["total_tickets"] == 2
    assert summary["open_tickets"] == 2
    assert summary["critical_tickets"] == 1
    assert sum(entry["count"] for entry in summary["by_product"]) == 2


def test_update_history_resolution_cycle_and_comment(client):
    product = create_product(client)
    ticket = create_ticket(client, product["id"]).json()

    resolved = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "Resolved", "priority": "Critical"})
    assert resolved.status_code == 200
    resolved_at = resolved.json()["resolved_at"]
    assert resolved_at

    closed = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "Closed"}).json()
    assert closed["resolved_at"] == resolved_at
    reopened = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "Open"}).json()
    assert reopened["resolved_at"] is None

    history = client.get(f"/api/v1/tickets/{ticket['id']}/history").json()
    fields = {row["changed_field"] for row in history}
    assert {"created", "status", "priority"}.issubset(fields)
    assert all(row["actor_label"] == "Local demo operator" for row in history)

    comment = client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"comment": "Please provide a browser console log."},
    )
    assert comment.status_code == 201
    assert comment.json()["author_label"] == "Local demo operator"
    assert client.get(f"/api/v1/tickets/{ticket['id']}/comments").json()[0]["comment"].startswith("Please")


def test_closed_without_resolved_and_reopening_status_edges(client):
    product = create_product(client)
    ticket = create_ticket(client, product["id"]).json()

    closed = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "Closed"})
    assert closed.status_code == 200
    assert closed.json()["resolved_at"] is not None
    summary = client.get("/api/v1/dashboard/summary", params={"product_id": product["id"]}).json()
    assert summary["resolved_tickets"] == 1

    reopened = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "Triaged"})
    assert reopened.status_code == 200
    assert reopened.json()["resolved_at"] is None
    summary = client.get("/api/v1/dashboard/summary", params={"product_id": product["id"]}).json()
    assert summary["resolved_tickets"] == 0


def test_validation_errors_and_ticket_not_found(client):
    product = create_product(client)
    missing_fields = client.post("/api/v1/tickets", json={"product_id": product["id"], "title": "Only title"})
    assert missing_fields.status_code == 422
    empty_update = client.patch("/api/v1/tickets/123", json={})
    assert empty_update.status_code == 422
    missing = client.get("/api/v1/tickets/123")
    assert missing.status_code == 404
    missing_comment = client.post("/api/v1/tickets/123/comments", json={"comment": "Hello"})
    assert missing_comment.status_code == 404


def test_legacy_routes_keep_shape_and_unassigned_create(client):
    created = client.post("/tickets", json={"title": "Legacy client", "description": "Existing payload"})
    assert created.status_code == 200
    assert set(created.json()) == {"id", "title", "description", "status"}
    assert created.json()["status"] == "Open"

    listed = client.get("/tickets").json()
    assert len(listed) == 1
    assert set(listed[0]) == {"id", "title", "description", "status"}
    updated = client.patch(f"/tickets/{created.json()['id']}", json={"status": "in_progress"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "In Progress"

    detail = client.get(f"/api/v1/tickets/{created.json()['id']}").json()
    assert detail["product_id"] is None
    assert detail["category"] == "General"
    assert detail["priority"] == "Medium"


def test_customer_membership_database_constraint(client):
    product = create_product(client)
    customer = client.post("/api/v1/customers", json={"name": "Example", "code": "C1"}).json()
    engine = client.app.state.test_engine
    with Session(engine) as session:
        with pytest.raises(IntegrityError):
            with session.begin():
                session.add(CustomerProduct(customer_id=customer["id"], product_id=product["id"] + 999))
                session.flush()


def test_ticket_transaction_rollback_isolation(client):
    engine = client.app.state.test_engine
    with Session(engine) as session:
        with pytest.raises(RuntimeError, match="force rollback"):
            with session.begin():
                session.add(
                    TicketRecord(
                        id=98765,
                        ticket_no="TEX-098765",
                        title="Transient",
                        description="Must roll back",
                        category="General",
                        priority="Medium",
                    )
                )
                session.flush()
                raise RuntimeError("force rollback")
    with Session(engine) as session:
        assert session.scalar(select(TicketRecord).where(TicketRecord.id == 98765)) is None
        assert session.scalar(select(TicketHistory).where(TicketHistory.ticket_id == 98765)) is None


def test_ticket_update_and_history_roll_back_together(client):
    product = create_product(client)
    ticket = create_ticket(client, product["id"]).json()
    engine = client.app.state.test_engine
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TRIGGER fail_title_history BEFORE INSERT ON ticket_history "
                "WHEN NEW.changed_field = 'title' BEGIN SELECT RAISE(FAIL, 'forced history failure'); END"
            )
        )

    response = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"title": "Must roll back"})
    assert response.status_code == 409
    after = client.get(f"/api/v1/tickets/{ticket['id']}").json()
    assert after["title"] == "Cannot sign in"
    history = client.get(f"/api/v1/tickets/{ticket['id']}/history").json()
    assert [event["changed_field"] for event in history] == ["created"]


def test_ticket_creation_and_created_history_roll_back_together(client):
    product = create_product(client)
    engine = client.app.state.test_engine
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TRIGGER fail_created_history BEFORE INSERT ON ticket_history "
                "WHEN NEW.changed_field = 'created' BEGIN SELECT RAISE(FAIL, 'forced history failure'); END"
            )
        )

    response = create_ticket(client, product["id"])
    assert response.status_code == 409
    with Session(engine) as session:
        assert session.scalar(select(TicketRecord)) is None
        assert session.scalar(select(TicketHistory)) is None


def test_ticket_foreign_keys_enforce_module_product_and_customer_membership(client):
    product = create_product(client)
    other_product = create_product(client, "Taskforce", "TF")
    module = create_module(client, product["id"])
    customer = client.post(
        "/api/v1/customers",
        json={"name": "Example customer", "code": "EXAMPLE", "product_ids": [product["id"]]},
    ).json()
    engine = client.app.state.test_engine

    def invalid_ticket(**overrides):
        values = {
            "ticket_no": "TEX-900001",
            "title": "Invalid relation",
            "description": "Should be rejected by a database foreign key",
            "category": "General",
            "priority": "Medium",
        }
        values.update(overrides)
        return TicketRecord(**values)

    with Session(engine) as session:
        with pytest.raises(IntegrityError):
            with session.begin():
                session.add(invalid_ticket(product_id=other_product["id"], module_id=module["id"]))
                session.flush()
    with Session(engine) as session:
        with pytest.raises(IntegrityError):
            with session.begin():
                session.add(invalid_ticket(ticket_no="TEX-900002", product_id=other_product["id"], customer_id=customer["id"]))
                session.flush()


def test_legacy_patch_updates_fields_and_normalizes_lowercase_status_aliases(client):
    created = client.post("/tickets", json={"title": "Old title", "description": "Old description"})
    ticket_id = created.json()["id"]

    updated = client.patch(
        f"/tickets/{ticket_id}",
        json={"title": "New title", "description": "New description", "status": "in_progress"},
    )
    assert updated.status_code == 200
    assert updated.json() == {
        "id": ticket_id,
        "title": "New title",
        "description": "New description",
        "status": "In Progress",
    }

    reopened = client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "Closed"
