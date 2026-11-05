import os
import re
from collections.abc import Callable, Generator
from datetime import UTC, datetime
from functools import lru_cache
from typing import TypeVar

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, create_engine, func, or_, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from backend.models import (
    Assignee,
    Customer,
    CustomerProduct,
    Product,
    ProductModule,
    TicketComment,
    TicketHistory,
    TicketRecord,
)
from backend.schemas import (
    AssigneeCreate,
    AssigneeResponse,
    AssigneeUpdate,
    Category,
    CommentCreate,
    CommentResponse,
    CustomerCreate,
    CustomerProductsUpdate,
    CustomerResponse,
    CustomerUpdate,
    DashboardSummary,
    HistoryResponse,
    LegacyTicketCreate,
    LegacyTicketUpdate,
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
    Priority,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    Question,
    Status,
    TicketCreate,
    TicketDetail,
    TicketPage,
    TicketResponse,
    TicketUpdate,
)

app = FastAPI(title="Texol AI Support Hub", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_ACTOR = "Local demo operator"
VALID_STATUSES = {"Open", "Triaged", "In Progress", "Testing", "Resolved", "Closed"}
LEGACY_STATUS_ALIASES = {
    "open": "Open",
    "triaged": "Triaged",
    "in_progress": "In Progress",
    "in progress": "In Progress",
    "testing": "Testing",
    "resolved": "Resolved",
    "closed": "Closed",
}
T = TypeVar("T")


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set before using the database")
    return create_engine(database_url, pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    try:
        factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    with factory() as session:
        yield session


def _write(db: Session, work: Callable[[], T], message: str = "Unable to save changes") -> T:
    try:
        with db.begin():
            return work()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="The request conflicts with existing data") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=message) from exc


def _not_found(entity: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{entity} not found")


def _ticket_number(db: Session) -> tuple[int, str]:
    if db.get_bind().dialect.name == "postgresql":
        next_id = db.scalar(text("SELECT nextval(pg_get_serial_sequence('tickets', 'id'))"))
    else:
        next_id = db.scalar(select(func.coalesce(func.max(TicketRecord.id), 0) + 1))
    ticket_id = int(next_id)
    return ticket_id, f"TEX-{ticket_id:06d}"


def _module_code(name: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", name.upper())
    if not words:
        raise HTTPException(status_code=422, detail="Module name must contain letters or numbers")
    return "_".join(words)


def _validate_products(db: Session, product_ids: list[int]) -> list[Product]:
    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(status_code=422, detail="Product IDs must not contain duplicates")
    products = list(db.scalars(select(Product).where(Product.id.in_(product_ids), Product.is_active.is_(True))))
    if len(products) != len(product_ids):
        raise HTTPException(status_code=422, detail="One or more products are missing or inactive")
    return products


def _validate_ticket_relations(
    db: Session,
    *,
    product_id: int,
    module_id: int | None,
    customer_id: int | None,
    assigned_to: int | None,
) -> None:
    product = db.get(Product, product_id)
    if product is None or not product.is_active:
        raise HTTPException(status_code=422, detail="Product is missing or inactive")
    if module_id is not None:
        module = db.get(ProductModule, module_id)
        if module is None or module.product_id != product_id or not module.is_active:
            raise HTTPException(status_code=422, detail="Module must be active and belong to the selected product")
    if customer_id is not None:
        customer = db.get(Customer, customer_id)
        membership = db.get(CustomerProduct, (customer_id, product_id))
        if customer is None or not customer.is_active or membership is None:
            raise HTTPException(status_code=422, detail="Customer must be active and associated with the selected product")
    if assigned_to is not None:
        assignee = db.get(Assignee, assigned_to)
        if assignee is None or not assignee.is_active:
            raise HTTPException(status_code=422, detail="Assignee is missing or inactive")


def _history_value(db: Session, field: str, value: object) -> str | None:
    if value is None:
        return None
    lookups = {
        "product_id": (Product, "name"),
        "module_id": (ProductModule, "name"),
        "customer_id": (Customer, "name"),
        "assigned_to": (Assignee, "name"),
    }
    if field in lookups:
        model, label = lookups[field]
        entity = db.get(model, value)
        return str(getattr(entity, label)) if entity is not None else str(value)
    return value.isoformat() if isinstance(value, datetime) else str(value)


def _record_history(db: Session, ticket_id: int, field: str, old: object, new: object) -> None:
    db.add(
        TicketHistory(
            ticket_id=ticket_id,
            changed_field=field,
            old_value=_history_value(db, field, old),
            new_value=_history_value(db, field, new),
            actor_label=DEMO_ACTOR,
        )
    )


def _ticket_detail(db: Session, ticket_id: int) -> TicketDetail:
    row = db.execute(
        select(TicketRecord, Product.name, ProductModule.name, Customer.name, Assignee.name)
        .outerjoin(Product, Product.id == TicketRecord.product_id)
        .outerjoin(
            ProductModule,
            and_(ProductModule.id == TicketRecord.module_id, ProductModule.product_id == TicketRecord.product_id),
        )
        .outerjoin(Customer, Customer.id == TicketRecord.customer_id)
        .outerjoin(Assignee, Assignee.id == TicketRecord.assigned_to)
        .where(TicketRecord.id == ticket_id)
    ).one_or_none()
    if row is None:
        raise _not_found("Ticket")
    ticket, product_name, module_name, customer_name, assignee_name = row
    return TicketDetail(
        id=ticket.id,
        ticket_no=ticket.ticket_no,
        product_id=ticket.product_id,
        product_name=product_name,
        module_id=ticket.module_id,
        module_name=module_name,
        customer_id=ticket.customer_id,
        customer_name=customer_name,
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        assigned_to=ticket.assigned_to,
        assignee_name=assignee_name,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
    )


def _customer_response(db: Session, customer: Customer) -> CustomerResponse:
    product_ids = list(
        db.scalars(
            select(CustomerProduct.product_id)
            .where(CustomerProduct.customer_id == customer.id)
            .order_by(CustomerProduct.product_id)
        )
    )
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        code=customer.code,
        email=customer.email,
        phone=customer.phone,
        is_active=customer.is_active,
        product_ids=product_ids,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


def _page_tickets(
    db: Session,
    *,
    page: int,
    page_size: int,
    q: str | None,
    product_id: int | None,
    status: Status | None,
    priority: Priority | None,
) -> TicketPage:
    predicates = []
    if q:
        pattern = f"%{q.strip()}%"
        predicates.append(
            or_(TicketRecord.ticket_no.ilike(pattern), TicketRecord.title.ilike(pattern), TicketRecord.description.ilike(pattern))
        )
    if product_id is not None:
        predicates.append(TicketRecord.product_id == product_id)
    if status is not None:
        predicates.append(TicketRecord.status == status)
    if priority is not None:
        predicates.append(TicketRecord.priority == priority)
    total = db.scalar(select(func.count()).select_from(TicketRecord).where(*predicates)) or 0
    ids = list(
        db.scalars(
            select(TicketRecord.id)
            .where(*predicates)
            .order_by(TicketRecord.created_at.desc(), TicketRecord.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    items = [_ticket_detail(db, ticket_id) for ticket_id in ids]
    return TicketPage(items=items, page=page, page_size=page_size, total=total)


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)) -> list[TicketRecord]:
    return list(db.scalars(select(TicketRecord).order_by(TicketRecord.id.desc())))


@app.post("/tickets", response_model=TicketResponse)
def create_legacy_ticket(ticket: LegacyTicketCreate, db: Session = Depends(get_db)) -> TicketRecord:
    def create() -> TicketRecord:
        ticket_id, ticket_no = _ticket_number(db)
        record = TicketRecord(
            id=ticket_id,
            ticket_no=ticket_no,
            title=ticket.title,
            description=ticket.description,
            category="General",
            priority="Medium",
            status="Open",
        )
        db.add(record)
        db.flush()
        _record_history(db, record.id, "created", None, record.ticket_no)
        return record

    return _write(db, create, "Unable to create ticket")


def _update_ticket_record(db: Session, ticket_id: int, changes: dict[str, object]) -> TicketRecord:
    record = db.get(TicketRecord, ticket_id)
    if record is None:
        raise _not_found("Ticket")
    relation_fields = {"product_id", "module_id", "customer_id", "assigned_to"}
    if relation_fields.intersection(changes):
        final_product_id = changes.get("product_id", record.product_id)
        final_module_id = changes.get("module_id", record.module_id)
        final_customer_id = changes.get("customer_id", record.customer_id)
        final_assigned_to = changes.get("assigned_to", record.assigned_to)
        if final_product_id is None:
            if any(value is not None for value in (final_module_id, final_customer_id)):
                raise HTTPException(status_code=422, detail="Module and customer require a product")
            if "product_id" in changes:
                raise HTTPException(status_code=422, detail="Ticket product cannot be cleared")
            if final_assigned_to is not None:
                assignee = db.get(Assignee, final_assigned_to)
                if assignee is None or not assignee.is_active:
                    raise HTTPException(status_code=422, detail="Assignee is missing or inactive")
        else:
            _validate_ticket_relations(
                db,
                product_id=int(final_product_id),
                module_id=final_module_id,
                customer_id=final_customer_id,
                assigned_to=final_assigned_to,
            )
    old_status = record.status
    changed: list[tuple[str, object, object]] = []
    for field, value in changes.items():
        old_value = getattr(record, field)
        if old_value != value:
            setattr(record, field, value)
            changed.append((field, old_value, value))
    if "status" in changes:
        new_status = changes["status"]
        now = datetime.now(UTC)
        if new_status in {"Resolved", "Closed"} and record.resolved_at is None:
            record.resolved_at = now
        elif old_status in {"Resolved", "Closed"} and new_status not in {"Resolved", "Closed"}:
            record.resolved_at = None
    if changed:
        record.updated_at = datetime.now(UTC)
        for field, old_value, new_value in changed:
            _record_history(db, record.id, field, old_value, new_value)
    db.flush()
    return record


@app.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_legacy_ticket(
    ticket_id: int,
    changes: LegacyTicketUpdate,
    db: Session = Depends(get_db),
) -> TicketRecord:
    updates = changes.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] is not None:
        status = updates["status"].strip()
        updates["status"] = LEGACY_STATUS_ALIASES.get(status.lower(), status)
    return _write(db, lambda: _update_ticket_record(db, ticket_id, updates), "Unable to update ticket")


@app.get("/api/v1/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.name)))


@app.post("/api/v1/products", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    return _write(db, lambda: _insert_product(db, payload), "Unable to create product")


def _insert_product(db: Session, payload: ProductCreate) -> Product:
    item = Product(**payload.model_dump())
    db.add(item)
    db.flush()
    return item


@app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise _not_found("Product")
    return product


@app.patch("/api/v1/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, changes: ProductUpdate, db: Session = Depends(get_db)) -> Product:
    def update() -> Product:
        item = db.get(Product, product_id)
        if item is None:
            raise _not_found("Product")
        for field, value in changes.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.flush()
        return item

    return _write(db, update, "Unable to update product")


@app.get("/api/v1/products/{product_id}/modules", response_model=list[ModuleResponse])
def list_modules(product_id: int, db: Session = Depends(get_db)) -> list[ProductModule]:
    if db.get(Product, product_id) is None:
        raise _not_found("Product")
    return list(
        db.scalars(select(ProductModule).where(ProductModule.product_id == product_id).order_by(ProductModule.name))
    )


@app.post("/api/v1/products/{product_id}/modules", response_model=ModuleResponse, status_code=201)
def create_module(product_id: int, payload: ModuleCreate, db: Session = Depends(get_db)) -> ProductModule:
    def create() -> ProductModule:
        product = db.get(Product, product_id)
        if product is None or not product.is_active:
            raise _not_found("Active product")
        code = payload.code or _module_code(payload.name)
        item = ProductModule(
            product_id=product_id,
            name=payload.name,
            code=code,
            description=payload.description,
            is_active=payload.is_active,
        )
        db.add(item)
        db.flush()
        return item

    return _write(db, create, "Unable to create module")


@app.patch("/api/v1/modules/{module_id}", response_model=ModuleResponse)
def update_module(module_id: int, changes: ModuleUpdate, db: Session = Depends(get_db)) -> ProductModule:
    def update() -> ProductModule:
        item = db.get(ProductModule, module_id)
        if item is None:
            raise _not_found("Module")
        for field, value in changes.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.flush()
        return item

    return _write(db, update, "Unable to update module")


@app.get("/api/v1/customers", response_model=list[CustomerResponse])
def list_customers(
    product_id: int | None = None,
    q: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
) -> list[CustomerResponse]:
    statement = select(Customer)
    if product_id is not None:
        statement = statement.join(CustomerProduct).where(CustomerProduct.product_id == product_id)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(or_(Customer.name.ilike(pattern), Customer.code.ilike(pattern)))
    customers = db.scalars(statement.order_by(Customer.name)).all()
    return [_customer_response(db, customer) for customer in customers]


@app.post("/api/v1/customers", response_model=CustomerResponse, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> CustomerResponse:
    def create() -> CustomerResponse:
        products = _validate_products(db, payload.product_ids) if payload.product_ids else []
        customer = Customer(
            name=payload.name,
            code=payload.code,
            email=payload.email,
            phone=payload.phone,
            is_active=payload.is_active,
        )
        db.add(customer)
        db.flush()
        for product in products:
            db.add(CustomerProduct(customer_id=customer.id, product_id=product.id))
        db.flush()
        return _customer_response(db, customer)

    return _write(db, create, "Unable to create customer")


@app.get("/api/v1/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> CustomerResponse:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise _not_found("Customer")
    return _customer_response(db, customer)


@app.patch("/api/v1/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, changes: CustomerUpdate, db: Session = Depends(get_db)) -> CustomerResponse:
    def update() -> CustomerResponse:
        customer = db.get(Customer, customer_id)
        if customer is None:
            raise _not_found("Customer")
        updates = changes.model_dump(exclude_unset=True)
        product_ids = updates.pop("product_ids", None)
        products = _validate_products(db, product_ids) if product_ids is not None else None
        for field, value in updates.items():
            setattr(customer, field, value)
        if products is not None:
            db.query(CustomerProduct).filter(CustomerProduct.customer_id == customer_id).delete(
                synchronize_session=False
            )
            for product in products:
                db.add(CustomerProduct(customer_id=customer_id, product_id=product.id))
        db.flush()
        return _customer_response(db, customer)

    return _write(db, update, "Unable to update customer")


@app.put("/api/v1/customers/{customer_id}/products", response_model=CustomerResponse)
def replace_customer_products(
    customer_id: int,
    payload: CustomerProductsUpdate,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    def replace() -> CustomerResponse:
        customer = db.get(Customer, customer_id)
        if customer is None:
            raise _not_found("Customer")
        products = _validate_products(db, payload.product_ids) if payload.product_ids else []
        db.query(CustomerProduct).filter(CustomerProduct.customer_id == customer_id).delete(synchronize_session=False)
        for product in products:
            db.add(CustomerProduct(customer_id=customer_id, product_id=product.id))
        db.flush()
        return _customer_response(db, customer)

    return _write(db, replace, "Unable to update customer product membership")


@app.get("/api/v1/assignees", response_model=list[AssigneeResponse])
def list_assignees(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
) -> list[Assignee]:
    statement = select(Assignee)
    if not include_inactive:
        statement = statement.where(Assignee.is_active.is_(True))
    return list(db.scalars(statement.order_by(Assignee.name)))


@app.post("/api/v1/assignees", response_model=AssigneeResponse, status_code=201)
def create_assignee(payload: AssigneeCreate, db: Session = Depends(get_db)) -> Assignee:
    def create() -> Assignee:
        item = Assignee(**payload.model_dump())
        db.add(item)
        db.flush()
        return item

    return _write(db, create, "Unable to create assignee")


@app.patch("/api/v1/assignees/{assignee_id}", response_model=AssigneeResponse)
def update_assignee(assignee_id: int, changes: AssigneeUpdate, db: Session = Depends(get_db)) -> Assignee:
    def update() -> Assignee:
        item = db.get(Assignee, assignee_id)
        if item is None:
            raise _not_found("Assignee")
        for field, value in changes.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.flush()
        return item

    return _write(db, update, "Unable to update assignee")


@app.get("/api/v1/tickets", response_model=TicketPage)
def list_ticket_page(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    q: str | None = Query(default=None, max_length=200),
    product_id: int | None = Query(default=None, gt=0),
    status: Status | None = None,
    priority: Priority | None = None,
    db: Session = Depends(get_db),
) -> TicketPage:
    return _page_tickets(
        db,
        page=page,
        page_size=page_size,
        q=q,
        product_id=product_id,
        status=status,
        priority=priority,
    )


@app.post("/api/v1/tickets", response_model=TicketDetail, status_code=201)
def create_product_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> TicketDetail:
    def create() -> TicketDetail:
        _validate_ticket_relations(
            db,
            product_id=payload.product_id,
            module_id=payload.module_id,
            customer_id=payload.customer_id,
            assigned_to=payload.assigned_to,
        )
        ticket_id, ticket_no = _ticket_number(db)
        item = TicketRecord(
            id=ticket_id,
            ticket_no=ticket_no,
            **payload.model_dump(),
            status="Open",
        )
        db.add(item)
        db.flush()
        _record_history(db, item.id, "created", None, item.ticket_no)
        db.flush()
        return _ticket_detail(db, item.id)

    return _write(db, create, "Unable to create ticket")


@app.get("/api/v1/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> TicketDetail:
    return _ticket_detail(db, ticket_id)


@app.patch("/api/v1/tickets/{ticket_id}", response_model=TicketDetail)
def update_product_ticket(
    ticket_id: int,
    changes: TicketUpdate,
    db: Session = Depends(get_db),
) -> TicketDetail:
    def update() -> TicketDetail:
        _update_ticket_record(db, ticket_id, changes.model_dump(exclude_unset=True))
        return _ticket_detail(db, ticket_id)

    return _write(db, update, "Unable to update ticket")


@app.post("/api/v1/tickets/{ticket_id}/comments", response_model=CommentResponse, status_code=201)
def create_ticket_comment(ticket_id: int, payload: CommentCreate, db: Session = Depends(get_db)) -> TicketComment:
    def create() -> TicketComment:
        if db.get(TicketRecord, ticket_id) is None:
            raise _not_found("Ticket")
        item = TicketComment(ticket_id=ticket_id, author_label=DEMO_ACTOR, comment=payload.comment)
        db.add(item)
        db.flush()
        return item

    return _write(db, create, "Unable to add comment")


@app.get("/api/v1/tickets/{ticket_id}/history", response_model=list[HistoryResponse])
def list_ticket_history(ticket_id: int, db: Session = Depends(get_db)) -> list[TicketHistory]:
    if db.get(TicketRecord, ticket_id) is None:
        raise _not_found("Ticket")
    return list(
        db.scalars(
            select(TicketHistory)
            .where(TicketHistory.ticket_id == ticket_id)
            .order_by(TicketHistory.created_at, TicketHistory.id)
        )
    )


@app.get("/api/v1/tickets/{ticket_id}/comments", response_model=list[CommentResponse])
def list_ticket_comments(ticket_id: int, db: Session = Depends(get_db)) -> list[TicketComment]:
    if db.get(TicketRecord, ticket_id) is None:
        raise _not_found("Ticket")
    return list(
        db.scalars(
            select(TicketComment)
            .where(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at, TicketComment.id)
        )
    )


@app.get("/api/v1/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(product_id: int | None = Query(default=None, gt=0), db: Session = Depends(get_db)) -> DashboardSummary:
    base = select(TicketRecord)
    if product_id is not None:
        base = base.where(TicketRecord.product_id == product_id)
    tickets = db.scalars(base).all()
    counts = {
        "total_tickets": len(tickets),
        "open_tickets": sum(ticket.status == "Open" for ticket in tickets),
        "in_progress_tickets": sum(ticket.status == "In Progress" for ticket in tickets),
        "resolved_tickets": sum(ticket.status in {"Resolved", "Closed"} for ticket in tickets),
        "critical_tickets": sum(ticket.priority == "Critical" for ticket in tickets),
    }
    products_query = select(Product.id, Product.name, func.count(TicketRecord.id)).outerjoin(
        TicketRecord, TicketRecord.product_id == Product.id
    )
    if product_id is not None:
        products_query = products_query.where(Product.id == product_id)
    by_product = [
        {"product_id": pid, "product_name": name, "count": count}
        for pid, name, count in db.execute(products_query.group_by(Product.id, Product.name).order_by(Product.name))
    ]
    recent = sorted(tickets, key=lambda ticket: (ticket.created_at, ticket.id), reverse=True)[:8]
    recent_tickets = [_ticket_detail(db, ticket.id) for ticket in recent]
    return DashboardSummary(**counts, by_product=by_product, recent_tickets=recent_tickets)


@app.post("/assistant")
def assistant(question: Question) -> dict[str, str | bool]:
    question_text = question.question.strip()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return {
            "answer": "AI is not configured yet. Add OPENAI_API_KEY in your local environment to enable it.",
            "configured": False,
        }
    from openai import OpenAI

    client = OpenAI(api_key=key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions="You are a helpful support assistant. Do not claim to have accessed tickets or documents unless provided.",
        input=question_text,
    )
    return {"answer": response.output_text, "configured": True}
