from httpx import AsyncClient


async def test_create_contact_returns_201(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    assert profile_r.status_code == 201
    pid = profile_r.json()["id"]

    response = await http_client.post(
        f"/api/profiles/{pid}/contacts",
        json={"type": "email", "value": "huy@example.com"},
    )
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int) and body["id"] > 0
    assert body["profile_id"] == pid
    assert body["type"] == "email"
    assert body["value"] == "huy@example.com"


async def test_list_contacts_returns_200(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]
    await http_client.post(
        f"/api/profiles/{pid}/contacts", json={"type": "email", "value": "a@b.com"}
    )
    await http_client.post(f"/api/profiles/{pid}/contacts", json={"type": "phone", "value": "123"})

    response = await http_client.get(f"/api/profiles/{pid}/contacts")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


async def test_list_contacts_empty_returns_200(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]

    response = await http_client.get(f"/api/profiles/{pid}/contacts")
    assert response.status_code == 200
    assert response.json() == []


async def test_patch_contact_returns_200(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]
    contact_r = await http_client.post(
        f"/api/profiles/{pid}/contacts",
        json={"type": "email", "value": "old@example.com"},
    )
    assert contact_r.status_code == 201
    cid = contact_r.json()["id"]

    response = await http_client.patch(
        f"/api/profiles/{pid}/contacts/{cid}",
        json={"value": "new@example.com"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["value"] == "new@example.com"
    assert body["type"] == "email"


async def test_delete_contact_returns_204(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]
    contact_r = await http_client.post(
        f"/api/profiles/{pid}/contacts",
        json={"type": "email", "value": "a@b.com"},
    )
    assert contact_r.status_code == 201
    cid = contact_r.json()["id"]

    response = await http_client.delete(f"/api/profiles/{pid}/contacts/{cid}")
    assert response.status_code == 204
    assert response.content == b""


async def test_create_contact_invalid_type_returns_422(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]

    response = await http_client.post(
        f"/api/profiles/{pid}/contacts",
        json={"type": "fax", "value": "123"},
    )
    assert response.status_code == 422


async def test_create_contact_missing_value_returns_422(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]

    response = await http_client.post(
        f"/api/profiles/{pid}/contacts",
        json={"type": "email"},
    )
    assert response.status_code == 422


async def test_create_contact_nonexistent_profile_returns_404(http_client: AsyncClient) -> None:
    response = await http_client.post(
        "/api/profiles/99999/contacts",
        json={"type": "email", "value": "a@b.com"},
    )
    assert response.status_code == 404


async def test_list_contacts_nonexistent_profile_returns_404(http_client: AsyncClient) -> None:
    response = await http_client.get("/api/profiles/99999/contacts")
    assert response.status_code == 404


async def test_patch_nonexistent_contact_returns_404(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]

    response = await http_client.patch(
        f"/api/profiles/{pid}/contacts/99999",
        json={"value": "new@example.com"},
    )
    assert response.status_code == 404


async def test_delete_nonexistent_contact_returns_404(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]

    response = await http_client.delete(f"/api/profiles/{pid}/contacts/99999")
    assert response.status_code == 404


async def test_patch_nonexistent_profile_returns_404(http_client: AsyncClient) -> None:
    response = await http_client.patch(
        "/api/profiles/99999/contacts/1",
        json={"value": "new@example.com"},
    )
    assert response.status_code == 404


async def test_delete_nonexistent_profile_returns_404(http_client: AsyncClient) -> None:
    response = await http_client.delete("/api/profiles/99999/contacts/1")
    assert response.status_code == 404


async def test_profile_id_zero_returns_422(http_client: AsyncClient) -> None:
    response = await http_client.post(
        "/api/profiles/0/contacts",
        json={"type": "email", "value": "a@b.com"},
    )
    assert response.status_code == 422


async def test_contact_id_zero_returns_422(http_client: AsyncClient) -> None:
    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]

    response = await http_client.delete(f"/api/profiles/{pid}/contacts/0")
    assert response.status_code == 422


async def test_create_contact_at_limit_returns_422(http_client: AsyncClient) -> None:
    from app.constants.limits import MAX_CONTACTS_PER_PROFILE

    profile_r = await http_client.post("/api/profiles", json={"name": "Alice"})
    pid = profile_r.json()["id"]

    contact_types = ["email", "phone", "github", "linkedin", "website", "twitter"]
    for i in range(MAX_CONTACTS_PER_PROFILE):
        ct = contact_types[i % len(contact_types)]
        await http_client.post(
            f"/api/profiles/{pid}/contacts", json={"type": ct, "value": f"val{i}@x.com"}
        )

    response = await http_client.post(
        f"/api/profiles/{pid}/contacts",
        json={"type": "email", "value": "overflow@example.com"},
    )
    assert response.status_code == 422
