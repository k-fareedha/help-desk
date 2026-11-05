from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Category = Literal[
    "Bug",
    "Feature Request",
    "Technical Support",
    "Integration Issue",
    "Performance Issue",
    "General",
]
Priority = Literal["Low", "Medium", "High", "Critical"]
Status = Literal["Open", "Triaged", "In Progress", "Testing", "Resolved", "Closed"]


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class ProductCreate(InputModel):
    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=5000)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, value: str) -> str:
        return value.upper()


class ProductUpdate(InputModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    code: str | None = Field(default=None, min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=5000)
    is_active: bool | None = None

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @model_validator(mode="after")
    def validate_update(self) -> "ProductUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one product field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set if field != "description"):
            raise ValueError("Product fields other than description must not be null")
        return self


class ModuleCreate(InputModel):
    name: str = Field(min_length=1, max_length=120)
    code: str | None = Field(default=None, min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=5000)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class ModuleUpdate(InputModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    code: str | None = Field(default=None, min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=5000)
    is_active: bool | None = None

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @model_validator(mode="after")
    def validate_update(self) -> "ModuleUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one module field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set if field != "description"):
            raise ValueError("Module fields other than description must not be null")
        return self


class CustomerCreate(InputModel):
    name: str = Field(min_length=1, max_length=160)
    code: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    email: str | None = Field(default=None, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=64)
    is_active: bool = True
    product_ids: list[int] = Field(default_factory=list)

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, value: str) -> str:
        return value.upper()


class CustomerUpdate(InputModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    code: str | None = Field(default=None, min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    email: str | None = Field(default=None, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=64)
    is_active: bool | None = None
    product_ids: list[int] | None = None

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @model_validator(mode="after")
    def validate_update(self) -> "CustomerUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one customer field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set if field not in {"email", "phone"}):
            raise ValueError("Customer fields other than email and phone must not be null")
        return self


class CustomerProductsUpdate(InputModel):
    product_ids: list[int]


class AssigneeCreate(InputModel):
    name: str = Field(min_length=1, max_length=160)
    email: str | None = Field(default=None, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    is_active: bool = True


class AssigneeUpdate(InputModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "AssigneeUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one assignee field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set if field != "email"):
            raise ValueError("Assignee name and active state must not be null")
        return self


class LegacyTicketCreate(InputModel):
    title: str = Field(min_length=1, max_length=1000)
    description: str = Field(min_length=1, max_length=20000)


class TicketCreate(InputModel):
    product_id: int = Field(gt=0)
    module_id: int | None = Field(default=None, gt=0)
    customer_id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=1000)
    description: str = Field(min_length=1, max_length=20000)
    category: Category
    priority: Priority
    assigned_to: int | None = Field(default=None, gt=0)


class TicketUpdate(InputModel):
    product_id: int | None = Field(default=None, gt=0)
    module_id: int | None = Field(default=None, gt=0)
    customer_id: int | None = Field(default=None, gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=1000)
    description: str | None = Field(default=None, min_length=1, max_length=20000)
    category: Category | None = None
    priority: Priority | None = None
    status: Status | None = None
    assigned_to: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_update(self) -> "TicketUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one ticket field must be provided")
        for field in {"product_id", "title", "description", "category", "priority", "status"} & self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} must not be null")
        return self


class LegacyTicketUpdate(InputModel):
    title: str | None = Field(default=None, min_length=1, max_length=1000)
    description: str | None = Field(default=None, min_length=1, max_length=20000)
    status: str | None = Field(default=None, min_length=1, max_length=32)

    @model_validator(mode="after")
    def validate_update(self) -> "LegacyTicketUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one ticket field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Updated ticket fields must not be null")
        return self


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TicketResponse(ReadModel):
    id: int
    title: str
    description: str
    status: str


class TicketDetail(TicketResponse):
    ticket_no: str
    product_id: int | None
    product_name: str | None
    module_id: int | None
    module_name: str | None
    customer_id: int | None
    customer_name: str | None
    category: str
    priority: str
    assigned_to: int | None
    assignee_name: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class TicketPage(BaseModel):
    items: list[TicketDetail]
    page: int
    page_size: int
    total: int


class CommentCreate(InputModel):
    comment: str = Field(min_length=1, max_length=10000)


class CommentResponse(ReadModel):
    id: int
    ticket_id: int
    author_label: str
    comment: str
    created_at: datetime


class HistoryResponse(ReadModel):
    id: int
    ticket_id: int
    changed_field: str
    old_value: str | None
    new_value: str | None
    actor_label: str
    created_at: datetime


class ProductResponse(ReadModel):
    id: int
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ModuleResponse(ReadModel):
    id: int
    product_id: int
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CustomerResponse(ReadModel):
    id: int
    name: str
    code: str
    email: str | None
    phone: str | None
    is_active: bool
    product_ids: list[int]
    created_at: datetime
    updated_at: datetime


class AssigneeResponse(ReadModel):
    id: int
    name: str
    email: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DashboardSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    critical_tickets: int
    by_product: list[dict[str, int | str]]
    recent_tickets: list[TicketDetail]


class Question(InputModel):
    question: str = Field(min_length=1, max_length=10000)
