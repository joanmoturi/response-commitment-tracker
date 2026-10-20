from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import ColumnElement

from app.auth import SessionDep, UserDep
from app.models import TrackedRequest, User, utcnow
from app.schemas import (
    TrackedRequestComplete,
    TrackedRequestCreate,
    TrackedRequestListResponse,
    TrackedRequestResponse,
    TrackedRequestUpdate,
)

router = APIRouter(prefix="/requests", tags=["requests"])
RequestStatus = Literal["all", "open", "overdue", "completed"]


def utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def to_response(request: TrackedRequest, now: datetime) -> TrackedRequestResponse:
    return TrackedRequestResponse(
        id=request.id,
        title=request.title,
        details=request.details,
        owner=request.owner,
        due_at=utc(request.due_at),
        status=request.status,
        response=request.response,
        completed_at=utc(request.completed_at) if request.completed_at else None,
        created_at=utc(request.created_at),
        updated_at=utc(request.updated_at),
        is_overdue=request.status == "open" and utc(request.due_at) < now,
    )


def search_clause(term: str) -> ColumnElement[bool]:
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{escaped}%"
    return or_(
        TrackedRequest.title.ilike(pattern, escape="\\"),
        TrackedRequest.details.ilike(pattern, escape="\\"),
        TrackedRequest.owner.ilike(pattern, escape="\\"),
    )


async def get_owned_request(request_id: str, user: User, session: SessionDep) -> TrackedRequest:
    request = await session.scalar(
        select(TrackedRequest).where(
            TrackedRequest.id == request_id, TrackedRequest.user_id == user.id
        )
    )
    if request is None:
        raise HTTPException(404, detail="request_not_found")
    return request


@router.post("", response_model=TrackedRequestResponse, status_code=201)
async def create_request(
    body: TrackedRequestCreate, user: UserDep, session: SessionDep, response: Response
) -> TrackedRequestResponse:
    now = utcnow()
    user_id = user.id
    existing = await session.scalar(
        select(TrackedRequest).where(
            TrackedRequest.user_id == user_id,
            TrackedRequest.submission_key == str(body.submission_key),
        )
    )
    if existing is not None:
        response.status_code = 200
        return to_response(existing, now)
    request = TrackedRequest(
        user_id=user_id,
        submission_key=str(body.submission_key),
        title=body.title,
        details=body.details,
        owner=body.owner,
        due_at=body.due_at.astimezone(UTC),
    )
    session.add(request)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        existing = await session.scalar(
            select(TrackedRequest).where(
                TrackedRequest.user_id == user_id,
                TrackedRequest.submission_key == str(body.submission_key),
            )
        )
        if existing is None:
            raise
        response.status_code = 200
        return to_response(existing, utcnow())
    await session.refresh(request)
    return to_response(request, now)


@router.get("", response_model=TrackedRequestListResponse)
async def list_requests(
    user: UserDep,
    session: SessionDep,
    status: RequestStatus = "open",
    q: Annotated[str | None, Query(max_length=120)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TrackedRequestListResponse:
    now = utcnow()
    base = TrackedRequest.user_id == user.id
    conditions = [base]
    if status == "open":
        conditions.append(TrackedRequest.status == "open")
    elif status == "completed":
        conditions.append(TrackedRequest.status == "completed")
    elif status == "overdue":
        conditions.extend([TrackedRequest.status == "open", TrackedRequest.due_at < now])
    if q and q.strip():
        conditions.append(search_clause(q.strip()))

    total = await session.scalar(
        select(func.count()).select_from(TrackedRequest).where(*conditions)
    )
    open_count = await session.scalar(
        select(func.count())
        .select_from(TrackedRequest)
        .where(base, TrackedRequest.status == "open")
    )
    overdue_count = await session.scalar(
        select(func.count())
        .select_from(TrackedRequest)
        .where(base, TrackedRequest.status == "open", TrackedRequest.due_at < now)
    )
    completed_count = await session.scalar(
        select(func.count())
        .select_from(TrackedRequest)
        .where(base, TrackedRequest.status == "completed")
    )
    requests = (
        await session.scalars(
            select(TrackedRequest)
            .where(*conditions)
            .order_by(TrackedRequest.due_at.asc(), TrackedRequest.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return TrackedRequestListResponse(
        items=[to_response(request, now) for request in requests],
        total=total or 0,
        open_count=open_count or 0,
        overdue_count=overdue_count or 0,
        completed_count=completed_count or 0,
    )


@router.get("/{request_id}", response_model=TrackedRequestResponse)
async def read_request(
    request_id: str, user: UserDep, session: SessionDep
) -> TrackedRequestResponse:
    return to_response(await get_owned_request(request_id, user, session), utcnow())


@router.patch("/{request_id}", response_model=TrackedRequestResponse)
async def update_request(
    request_id: str,
    body: TrackedRequestUpdate,
    user: UserDep,
    session: SessionDep,
) -> TrackedRequestResponse:
    statement = update(TrackedRequest).where(
        TrackedRequest.id == request_id,
        TrackedRequest.user_id == user.id,
        TrackedRequest.status == "open",
    )
    if body.title is not None:
        statement = statement.values(title=body.title)
    if body.details is not None:
        statement = statement.values(details=body.details)
    if body.owner is not None:
        statement = statement.values(owner=body.owner)
    if body.due_at is not None:
        statement = statement.values(due_at=body.due_at.astimezone(UTC))
    updated_id = await session.scalar(
        statement.values(updated_at=utcnow()).returning(TrackedRequest.id)
    )
    if updated_id is None:
        await get_owned_request(request_id, user, session)
        raise HTTPException(409, detail="request_not_open")
    await session.commit()
    request = await get_owned_request(request_id, user, session)
    return to_response(request, utcnow())


@router.post("/{request_id}/complete", response_model=TrackedRequestResponse)
async def complete_request(
    request_id: str,
    body: TrackedRequestComplete,
    user: UserDep,
    session: SessionDep,
) -> TrackedRequestResponse:
    now = utcnow()
    updated_id = await session.scalar(
        update(TrackedRequest)
        .where(
            TrackedRequest.id == request_id,
            TrackedRequest.user_id == user.id,
            TrackedRequest.status == "open",
        )
        .values(
            status="completed",
            response=body.response,
            completed_at=now,
            updated_at=now,
        )
        .returning(TrackedRequest.id)
    )
    if updated_id is None:
        await get_owned_request(request_id, user, session)
        raise HTTPException(409, detail="request_not_open")
    await session.commit()
    request = await get_owned_request(request_id, user, session)
    return to_response(request, now)
