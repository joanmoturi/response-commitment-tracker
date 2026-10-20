import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import commitments
from app.models import TrackedRequest
from tests.conftest import authorization, register


def request_body(
    title: str, due_at: datetime, *, owner: str = "Casey Example", details: str = "Send an update"
) -> dict[str, str]:
    return {
        "submission_key": str(uuid4()),
        "title": title,
        "details": details,
        "owner": owner,
        "due_at": due_at.isoformat(),
    }


async def create_request(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    title: str,
    due_at: datetime,
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/requests", headers=headers, json=request_body(title, due_at)
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_requests_are_private_to_the_authenticated_account(
    client: httpx.AsyncClient,
) -> None:
    alice = await register(client, "alice@example.com")
    alice_headers = authorization(alice)
    item = await create_request(
        client, alice_headers, "Prepare the renewal response", datetime(2030, 1, 1, tzinfo=UTC)
    )

    bob = await register(client, "bob@example.com")
    bob_headers = authorization(bob)
    bob_item = await create_request(
        client, bob_headers, "Review the supplier update", datetime(2030, 2, 1, tzinfo=UTC)
    )

    response = await client.get("/api/v1/requests", headers=bob_headers)
    assert response.status_code == 200
    assert [request["id"] for request in response.json()["items"]] == [bob_item["id"]]
    assert response.json()["total"] == 1
    response = await client.get("/api/v1/requests?status=all&q=renewal", headers=bob_headers)
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0
    response = await client.get(f"/api/v1/requests/{item['id']}", headers=bob_headers)
    assert response.status_code == 404
    response = await client.patch(
        f"/api/v1/requests/{item['id']}", headers=bob_headers, json={"owner": "Bob"}
    )
    assert response.status_code == 404
    response = await client.post(
        f"/api/v1/requests/{item['id']}/complete",
        headers=bob_headers,
        json={"response": "Not authorized"},
    )
    assert response.status_code == 404

    response = await client.get(f"/api/v1/requests/{bob_item['id']}", headers=alice_headers)
    assert response.status_code == 404
    response = await client.patch(
        f"/api/v1/requests/{bob_item['id']}", headers=alice_headers, json={"owner": "Alice"}
    )
    assert response.status_code == 404
    response = await client.post(
        f"/api/v1/requests/{bob_item['id']}/complete",
        headers=alice_headers,
        json={"response": "Not authorized"},
    )
    assert response.status_code == 404

    alice_list = await client.get("/api/v1/requests?status=all", headers=alice_headers)
    assert alice_list.status_code == 200
    assert [request["id"] for request in alice_list.json()["items"]] == [item["id"]]
    bob_list = await client.get("/api/v1/requests?status=all", headers=bob_headers)
    assert bob_list.status_code == 200
    assert [request["id"] for request in bob_list.json()["items"]] == [bob_item["id"]]
    unchanged_bob_item = await client.get(f"/api/v1/requests/{bob_item['id']}", headers=bob_headers)
    assert unchanged_bob_item.json()["owner"] == bob_item["owner"]
    assert unchanged_bob_item.json()["status"] == "open"


async def test_request_routes_require_bearer_auth_and_hide_unknown_ids(
    client: httpx.AsyncClient,
) -> None:
    tokens = await register(client)
    headers = authorization(tokens)
    item = await create_request(
        client, headers, "Authentication boundary", datetime(2030, 1, 1, tzinfo=UTC)
    )
    body = request_body("Anonymous create", datetime(2030, 1, 1, tzinfo=UTC))

    for response in [
        await client.post("/api/v1/requests", json=body),
        await client.get("/api/v1/requests?status=all"),
        await client.get(f"/api/v1/requests/{item['id']}"),
        await client.patch(f"/api/v1/requests/{item['id']}", json={"owner": "Intruder"}),
        await client.post(f"/api/v1/requests/{item['id']}/complete", json={"response": "Intruder"}),
    ]:
        assert response.status_code == 401

    missing_id = str(uuid4())
    assert (await client.get(f"/api/v1/requests/{missing_id}", headers=headers)).status_code == 404
    assert (
        await client.patch(
            f"/api/v1/requests/{missing_id}", headers=headers, json={"owner": "Nobody"}
        )
    ).status_code == 404
    assert (
        await client.post(
            f"/api/v1/requests/{missing_id}/complete",
            headers=headers,
            json={"response": "Nobody"},
        )
    ).status_code == 404


async def test_create_validates_required_content_and_timezone(
    client: httpx.AsyncClient,
) -> None:
    tokens = await register(client)
    headers = authorization(tokens)
    body = request_body("Valid title", datetime(2030, 1, 1, tzinfo=UTC))
    for changes in [
        {"title": "  "},
        {"details": ""},
        {"owner": " "},
        {"due_at": "2030-01-01T00:00:00"},
    ]:
        response = await client.post("/api/v1/requests", headers=headers, json=body | changes)
        assert response.status_code == 422

    response = await client.post(
        "/api/v1/requests", headers=headers, json=body | {"extra": "rejected"}
    )
    assert response.status_code == 422


async def test_repeated_create_with_same_submission_key_is_idempotent(
    client: httpx.AsyncClient,
) -> None:
    tokens = await register(client)
    headers = authorization(tokens)
    body = request_body("Send the revised proposal", datetime(2030, 1, 1, tzinfo=UTC))

    first = await client.post("/api/v1/requests", headers=headers, json=body)
    repeated = await client.post("/api/v1/requests", headers=headers, json=body)
    assert first.status_code == 201
    assert repeated.status_code == 200
    assert repeated.json()["id"] == first.json()["id"]

    listing = await client.get("/api/v1/requests?status=all", headers=headers)
    assert listing.json()["total"] == 1


async def test_concurrent_create_with_same_submission_key_creates_one_request(
    client: httpx.AsyncClient,
) -> None:
    tokens = await register(client)
    headers = authorization(tokens)
    body = request_body("Send the revised proposal", datetime(2030, 1, 1, tzinfo=UTC))

    first, second = await asyncio.gather(
        client.post("/api/v1/requests", headers=headers, json=body),
        client.post("/api/v1/requests", headers=headers, json=body),
    )
    assert sorted([first.status_code, second.status_code]) == [200, 201]
    assert first.json()["id"] == second.json()["id"]

    listing = await client.get("/api/v1/requests?status=all", headers=headers)
    assert listing.json()["total"] == 1


async def test_create_recovers_from_unique_conflict_after_initial_lookup(
    client: httpx.AsyncClient,
    application: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tokens = await register(client)
    headers = authorization(tokens)
    body = request_body("Send the revised proposal", datetime(2030, 1, 1, tzinfo=UTC))
    original_commit = AsyncSession.commit
    conflict_inserted = False

    async def commit_with_conflicting_insert(session: AsyncSession) -> None:
        nonlocal conflict_inserted
        candidate = next((item for item in session.new if isinstance(item, TrackedRequest)), None)
        if candidate is not None and not conflict_inserted:
            conflict_inserted = True
            async with application.state.test_sessions() as other_session:
                other_session.add(
                    TrackedRequest(
                        user_id=candidate.user_id,
                        submission_key=candidate.submission_key,
                        title=candidate.title,
                        details=candidate.details,
                        owner=candidate.owner,
                        due_at=candidate.due_at,
                    )
                )
                await original_commit(other_session)
        await original_commit(session)

    monkeypatch.setattr(AsyncSession, "commit", commit_with_conflicting_insert)
    response = await client.post("/api/v1/requests", headers=headers, json=body)
    assert conflict_inserted
    assert response.status_code == 200
    assert response.json()["title"] == body["title"]

    listing = await client.get("/api/v1/requests?status=all", headers=headers)
    assert listing.json()["total"] == 1


async def test_overdue_is_derived_from_deadline_and_completion(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixed_now = datetime(2026, 10, 16, 12, 0, tzinfo=UTC)
    monkeypatch.setattr(commitments, "utcnow", lambda: fixed_now)
    tokens = await register(client)
    headers = authorization(tokens)

    boundary = await create_request(client, headers, "Due now", fixed_now)
    overdue = await create_request(
        client, headers, "Past due", fixed_now - timedelta(microseconds=1)
    )
    completed = await create_request(
        client, headers, "Resolved late", fixed_now - timedelta(days=1)
    )
    completion = await client.post(
        f"/api/v1/requests/{completed['id']}/complete",
        headers=headers,
        json={"response": "Sent the final answer"},
    )
    assert completion.status_code == 200
    assert completion.json()["is_overdue"] is False
    assert completion.json()["response"] == "Sent the final answer"

    response = await client.get("/api/v1/requests?status=overdue", headers=headers)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [overdue["id"]]
    assert response.json()["overdue_count"] == 1

    response = await client.get("/api/v1/requests?status=completed", headers=headers)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [completed["id"]]

    response = await client.get("/api/v1/requests?status=all", headers=headers)
    by_id = {item["id"]: item for item in response.json()["items"]}
    assert by_id[boundary["id"]]["is_overdue"] is False
    assert by_id[overdue["id"]]["is_overdue"] is True
    assert by_id[completed["id"]]["is_overdue"] is False
    assert response.json()["open_count"] == 2
    assert response.json()["completed_count"] == 1


async def test_update_owner_deadline_search_and_completion_transition(
    client: httpx.AsyncClient,
) -> None:
    tokens = await register(client)
    headers = authorization(tokens)
    item = await create_request(
        client, headers, "Prepare the response", datetime(2030, 1, 1, tzinfo=UTC)
    )

    updated = await client.patch(
        f"/api/v1/requests/{item['id']}",
        headers=headers,
        json={
            "owner": "Jordan Lee",
            "due_at": "2029-12-31T10:00:00-05:00",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["owner"] == "Jordan Lee"
    assert updated.json()["due_at"] == "2029-12-31T15:00:00Z"

    response = await client.get("/api/v1/requests?q=JORDAN&status=open", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["id"] == item["id"]

    for body in [{}, {"owner": None}, {"status": "completed"}]:
        invalid = await client.patch(f"/api/v1/requests/{item['id']}", headers=headers, json=body)
        assert invalid.status_code == 422

    completed = await client.post(
        f"/api/v1/requests/{item['id']}/complete",
        headers=headers,
        json={"response": None},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["completed_at"] is not None
    assert completed.json()["response"] is None
    persisted = await client.get(f"/api/v1/requests/{item['id']}", headers=headers)
    assert persisted.status_code == 200
    assert persisted.json()["status"] == "completed"
    assert persisted.json()["response"] is None

    repeated = await client.post(
        f"/api/v1/requests/{item['id']}/complete",
        headers=headers,
        json={"response": "Duplicate"},
    )
    assert repeated.status_code == 409
    edited_after_completion = await client.patch(
        f"/api/v1/requests/{item['id']}", headers=headers, json={"owner": "Someone else"}
    )
    assert edited_after_completion.status_code == 409


async def test_pagination_and_search_wildcards_are_bounded(
    client: httpx.AsyncClient,
) -> None:
    tokens = await register(client)
    headers = authorization(tokens)
    for title in ["Alpha", "Beta_1", "BetaX1"]:
        await create_request(client, headers, title, datetime(2030, 1, 1, tzinfo=UTC))

    response = await client.get(
        "/api/v1/requests?status=all&q=Beta_1&limit=1&offset=0", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert [item["title"] for item in response.json()["items"]] == ["Beta_1"]
    assert response.json()["open_count"] == 3

    invalid_limit = await client.get("/api/v1/requests?limit=101", headers=headers)
    assert invalid_limit.status_code == 422
