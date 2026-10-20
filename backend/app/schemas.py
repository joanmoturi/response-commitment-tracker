from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Credentials(StrictModel):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=12, max_length=128)


class UserResponse(StrictModel):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)
    id: str
    email: str


class TokenResponse(StrictModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserResponse


class ProvidersResponse(StrictModel):
    local: bool
    registration_enabled: bool
    oidc: bool


class RunRequest(StrictModel):
    prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class RunResponse(StrictModel):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)
    id: str
    status: Literal["running", "completed", "failed"]
    answer: str | None
    error: str | None
    steps: int


class Arithmetic(StrictModel):
    operation: Literal["add", "subtract", "multiply", "divide"]
    left: str = Field(pattern=r"^-?\d{1,12}(\.\d{1,8})?$")
    right: str = Field(pattern=r"^-?\d{1,12}(\.\d{1,8})?$")


class Decision(StrictModel):
    """All fields required, nullable alternatives compatible with strict OpenAI output."""

    action: Literal["tool", "final"]
    tool: Arithmetic | None
    answer: str | None = Field(min_length=1, max_length=8000)


class TrackedRequestCreate(StrictModel):
    submission_key: Annotated[UUID, Field(strict=False)]
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    details: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
    owner: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    due_at: Annotated[AwareDatetime, Field(strict=False)]


class TrackedRequestUpdate(StrictModel):
    title: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
        | None
    ) = None
    details: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
        | None
    ) = None
    owner: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
        | None
    ) = None
    due_at: Annotated[AwareDatetime, Field(strict=False)] | None = None

    @model_validator(mode="after")
    def require_update_values(self) -> "TrackedRequestUpdate":
        if not self.model_fields_set or any(
            getattr(self, name) is None for name in self.model_fields_set
        ):
            raise ValueError("at least one non-null field is required")
        return self


class TrackedRequestComplete(StrictModel):
    response: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
        | None
    ) = None


class TrackedRequestResponse(StrictModel):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)
    id: str
    title: str
    details: str
    owner: str
    due_at: AwareDatetime
    status: Literal["open", "completed"]
    response: str | None
    completed_at: datetime | None
    created_at: AwareDatetime
    updated_at: AwareDatetime
    is_overdue: bool


class TrackedRequestListResponse(StrictModel):
    items: list[TrackedRequestResponse]
    total: int
    open_count: int
    overdue_count: int
    completed_count: int
