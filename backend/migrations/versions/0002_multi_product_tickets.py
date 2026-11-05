"""Add product-aware ticket management while preserving starter tickets."""

from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa

revision: str = "0002_multi_product_tickets"
down_revision: Union[str, None] = "0001_initial_tickets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PRODUCTS = {"VF": "Vanforces", "TF": "Taskforce", "SO": "Speak Order"}
MODULES = {
    "VF": [
        "Mobile Sales",
        "ERP Integration",
        "Invoice Management",
        "Route Management",
        "Inventory",
        "Payment and Collection",
        "Reports",
    ],
    "TF": ["Task Management", "Workflow", "Assignment", "Approval", "Reports"],
    "SO": ["Voice Recognition", "Product Matching", "Order Processing", "Approval", "Integration"],
}


def _module_code(name: str) -> str:
    return "_".join("".join(character for character in word if character.isalnum()) for word in name.upper().split())


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_products_code"),
        sa.UniqueConstraint("name", name="uq_products_name"),
    )
    op.create_table(
        "product_modules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name="fk_product_modules_product", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "code", name="uq_product_modules_product_code"),
        sa.UniqueConstraint("product_id", "id", name="uq_product_modules_product_id"),
    )
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_customers_code"),
    )
    op.create_table(
        "customer_products",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], name="fk_customer_products_customer", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name="fk_customer_products_product", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("customer_id", "product_id"),
    )
    op.create_table(
        "assignees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_assignees_email"),
    )

    # Create new columns nullable/defaulted, backfill legacy rows, then enforce constraints.
    op.add_column("tickets", sa.Column("ticket_no", sa.String(length=32), nullable=True))
    op.add_column("tickets", sa.Column("product_id", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("module_id", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("customer_id", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("category", sa.String(length=40), server_default="General", nullable=False))
    op.add_column("tickets", sa.Column("priority", sa.String(length=16), server_default="Medium", nullable=False))
    op.add_column("tickets", sa.Column("assigned_to", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column("tickets", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column("tickets", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
    op.execute(
        sa.text(
            "UPDATE tickets SET status = CASE lower(status) "
            "WHEN 'open' THEN 'Open' WHEN 'closed' THEN 'Closed' ELSE status END"
        )
    )
    op.alter_column("tickets", "status", server_default="Open")
    op.execute(
        sa.text(
            "UPDATE tickets SET ticket_no = 'TEX-' || "
            "lpad(id::text, greatest(6, length(id::text)), '0')"
        )
    )
    op.alter_column("tickets", "ticket_no", nullable=False)
    op.create_unique_constraint("uq_tickets_ticket_no", "tickets", ["ticket_no"])
    op.create_foreign_key("fk_tickets_product", "tickets", "products", ["product_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_tickets_assignee", "tickets", "assignees", ["assigned_to"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key(
        "fk_tickets_product_module", "tickets", "product_modules", ["product_id", "module_id"],
        ["product_id", "id"], ondelete="RESTRICT"
    )
    op.create_foreign_key(
        "fk_tickets_customer_product", "tickets", "customer_products", ["customer_id", "product_id"],
        ["customer_id", "product_id"], ondelete="RESTRICT"
    )
    op.create_check_constraint("ck_tickets_module_requires_product", "tickets", "module_id IS NULL OR product_id IS NOT NULL")
    op.create_check_constraint("ck_tickets_customer_requires_product", "tickets", "customer_id IS NULL OR product_id IS NOT NULL")
    op.create_check_constraint(
        "ck_tickets_category",
        "tickets",
        "category IN ('Bug', 'Feature Request', 'Technical Support', 'Integration Issue', 'Performance Issue', 'General')",
    )
    op.create_check_constraint("ck_tickets_priority", "tickets", "priority IN ('Low', 'Medium', 'High', 'Critical')")
    op.create_index("ix_tickets_product_status", "tickets", ["product_id", "status"])
    op.create_index("ix_tickets_product_priority", "tickets", ["product_id", "priority"])
    op.create_index("ix_tickets_created_at", "tickets", ["created_at"])
    op.create_index("ix_tickets_module_id", "tickets", ["module_id"])
    op.create_index("ix_tickets_customer_id", "tickets", ["customer_id"])
    op.create_index("ix_tickets_assigned_to", "tickets", ["assigned_to"])
    op.create_index("ix_customer_products_product_id", "customer_products", ["product_id"])

    op.create_table(
        "ticket_comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("author_label", sa.String(length=160), server_default="Local demo operator", nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], name="fk_ticket_comments_ticket", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ticket_comments_ticket_id", "ticket_comments", ["ticket_id"])
    op.create_table(
        "ticket_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("changed_field", sa.String(length=64), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("actor_label", sa.String(length=160), server_default="Local demo operator", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], name="fk_ticket_history_ticket", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ticket_history_ticket_id", "ticket_history", ["ticket_id"])

    # Preserve the sequence if the legacy table was imported with explicit IDs.
    op.execute(
        sa.text(
            "SELECT setval(pg_get_serial_sequence('tickets', 'id'), "
            "GREATEST((SELECT COALESCE(MAX(id), 1) FROM tickets), 1), "
            "(SELECT COUNT(*) > 0 FROM tickets))"
        )
    )

    # Seeds are insert-only. Detect unrelated conflicts instead of silently omitting seeds.
    bind = op.get_bind()
    if not context.is_offline_mode():
        for product_code, product_name in PRODUCTS.items():
            existing = bind.execute(
                sa.text("SELECT name, code FROM products WHERE code = :code OR name = :name"),
                {"code": product_code, "name": product_name},
            ).all()
            if existing and (len(existing) != 1 or (existing[0].name, existing[0].code) != (product_name, product_code)):
                raise RuntimeError(f"Cannot seed product {product_code}: a conflicting name or code already exists")
        for product_code, names in MODULES.items():
            for module_name in names:
                module_code = _module_code(module_name)
                existing = bind.execute(
                    sa.text(
                        "SELECT m.name, m.code FROM product_modules AS m "
                        "JOIN products AS p ON p.id = m.product_id "
                        "WHERE p.code = :product_code AND p.name = :product_name "
                        "AND (m.code = :module_code OR m.name = :module_name)"
                    ),
                    {
                        "product_code": product_code,
                        "product_name": PRODUCTS[product_code],
                        "module_code": module_code,
                        "module_name": module_name,
                    },
                ).all()
                if any((row.name, row.code) != (module_name, module_code) for row in existing):
                    raise RuntimeError(
                        f"Cannot seed module {product_code}/{module_code}: a conflicting name or code already exists"
                    )

    op.execute(
        sa.text(
            "INSERT INTO products (name, code, is_active) VALUES "
            "('Vanforces', 'VF', true), ('Taskforce', 'TF', true), ('Speak Order', 'SO', true) "
            "ON CONFLICT DO NOTHING"
        )
    )
    for product_code, names in MODULES.items():
        for module_name in names:
            # These values are fixed migration constants, not user-provided SQL input.
            name_sql = module_name.replace("'", "''")
            code_sql = _module_code(module_name).replace("'", "''")
            product_name_sql = PRODUCTS[product_code].replace("'", "''")
            op.execute(
                sa.text(
                    "INSERT INTO product_modules (product_id, name, code, is_active) "
                    f"SELECT id, '{name_sql}', '{code_sql}', true FROM products "
                    f"WHERE code = '{product_code}' AND name = '{product_name_sql}' "
                    "ON CONFLICT DO NOTHING"
                )
            )
            if not context.is_offline_mode():
                seeded = bind.execute(
                    sa.text(
                        "SELECT 1 FROM product_modules AS m "
                        "JOIN products AS p ON p.id = m.product_id "
                        "WHERE p.code = :product_code AND p.name = :product_name "
                        "AND m.code = :module_code AND m.name = :module_name"
                    ),
                    {
                        "product_code": product_code,
                        "product_name": PRODUCTS[product_code],
                        "module_code": _module_code(module_name),
                        "module_name": module_name,
                    },
                ).first()
                if seeded is None:
                    raise RuntimeError(f"Could not seed module {product_code}/{_module_code(module_name)}")


def downgrade() -> None:
    # This downgrade drops Prompt 007 tables/data. Do not run against persistent data without approval.
    op.drop_index("ix_ticket_history_ticket_id", table_name="ticket_history")
    op.drop_table("ticket_history")
    op.drop_index("ix_ticket_comments_ticket_id", table_name="ticket_comments")
    op.drop_table("ticket_comments")
    op.drop_index("ix_customer_products_product_id", table_name="customer_products")
    op.drop_index("ix_tickets_assigned_to", table_name="tickets")
    op.drop_index("ix_tickets_customer_id", table_name="tickets")
    op.drop_index("ix_tickets_module_id", table_name="tickets")
    op.drop_constraint("ck_tickets_priority", "tickets", type_="check")
    op.drop_constraint("ck_tickets_category", "tickets", type_="check")
    op.drop_constraint("ck_tickets_customer_requires_product", "tickets", type_="check")
    op.drop_constraint("ck_tickets_module_requires_product", "tickets", type_="check")
    op.drop_index("ix_tickets_created_at", table_name="tickets")
    op.drop_index("ix_tickets_product_priority", table_name="tickets")
    op.drop_index("ix_tickets_product_status", table_name="tickets")
    op.drop_constraint("fk_tickets_customer_product", "tickets", type_="foreignkey")
    op.drop_constraint("fk_tickets_product_module", "tickets", type_="foreignkey")
    op.drop_constraint("fk_tickets_assignee", "tickets", type_="foreignkey")
    op.drop_constraint("fk_tickets_product", "tickets", type_="foreignkey")
    op.drop_constraint("uq_tickets_ticket_no", "tickets", type_="unique")
    for column in (
        "resolved_at", "updated_at", "created_at", "assigned_to", "priority", "category",
        "customer_id", "module_id", "product_id", "ticket_no",
    ):
        op.drop_column("tickets", column)
    op.alter_column("tickets", "status", server_default="open")
    op.drop_table("assignees")
    op.drop_table("customer_products")
    op.drop_table("customers")
    op.drop_table("product_modules")
    op.drop_table("products")
