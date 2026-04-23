from httpx import AsyncClient


async def test_create_profile_returns_201(http_client: AsyncClient) -> None:
    response = await http_client.post(
        "/api/profiles", json={"name": "Alice", "description": "Engineer"}
    )
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int) and body["id"] > 0
    assert body["name"] == "Alice"
    assert body["description"] == "Engineer"
    assert "created_at" in body
    assert "updated_at" in body


async def test_create_profile_optional_description(http_client: AsyncClient) -> None:
    response = await http_client.post("/api/profiles", json={"name": "Bob"})
    assert response.status_code == 201
    assert response.json()["description"] is None


async def test_create_profile_missing_name_returns_422(http_client: AsyncClient) -> None:
    response = await http_client.post("/api/profiles", json={"description": "no name"})
    assert response.status_code == 422


async def test_create_profile_empty_name_returns_422(http_client: AsyncClient) -> None:
    response = await http_client.post("/api/profiles", json={"name": ""})
    assert response.status_code == 422


async def test_list_profiles_empty(http_client: AsyncClient) -> None:
    response = await http_client.get("/api/profiles")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_profiles_returns_all_created(http_client: AsyncClient) -> None:
    r1 = await http_client.post("/api/profiles", json={"name": "Alice"})
    assert r1.status_code == 201
    r2 = await http_client.post("/api/profiles", json={"name": "Bob"})
    assert r2.status_code == 201
    response = await http_client.get("/api/profiles")
    assert response.status_code == 200
    profiles = response.json()
    assert len(profiles) == 2
    names = {p["name"] for p in profiles}
    assert names == {"Alice", "Bob"}


async def test_create_profile_whitespace_name_returns_422(http_client: AsyncClient) -> None:
    response = await http_client.post("/api/profiles", json={"name": "   "})
    assert response.status_code == 422


async def test_get_profile_found_returns_200(http_client: AsyncClient) -> None:
    r = await http_client.post("/api/profiles", json={"name": "Alice", "description": "Eng"})
    assert r.status_code == 201
    profile_id = r.json()["id"]

    response = await http_client.get(f"/api/profiles/{profile_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == profile_id
    assert body["name"] == "Alice"
    assert body["description"] == "Eng"


async def test_get_profile_not_found_returns_404(http_client: AsyncClient) -> None:
    response = await http_client.get("/api/profiles/99999")
    assert response.status_code == 404


async def test_patch_name_only_returns_200(http_client: AsyncClient) -> None:
    r = await http_client.post("/api/profiles", json={"name": "Alice", "description": "Eng"})
    profile_id = r.json()["id"]

    response = await http_client.patch(f"/api/profiles/{profile_id}", json={"name": "Alicia"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alicia"
    assert body["description"] == "Eng"


async def test_patch_description_only_returns_200(http_client: AsyncClient) -> None:
    r = await http_client.post("/api/profiles", json={"name": "Alice", "description": "Eng"})
    profile_id = r.json()["id"]

    response = await http_client.patch(f"/api/profiles/{profile_id}", json={"description": "Dev"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice"
    assert body["description"] == "Dev"


async def test_patch_both_fields_returns_200(http_client: AsyncClient) -> None:
    r = await http_client.post("/api/profiles", json={"name": "Alice", "description": "Eng"})
    profile_id = r.json()["id"]

    response = await http_client.patch(
        f"/api/profiles/{profile_id}", json={"name": "Bob", "description": "Dev"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Bob"
    assert body["description"] == "Dev"


async def test_patch_nonexistent_id_returns_404(http_client: AsyncClient) -> None:
    response = await http_client.patch("/api/profiles/99999", json={"name": "Ghost"})
    assert response.status_code == 404


async def test_patch_updated_at_changes(http_client: AsyncClient) -> None:
    r = await http_client.post("/api/profiles", json={"name": "Alice", "description": "Eng"})
    created_at = r.json()["created_at"]
    profile_id = r.json()["id"]

    patch_r = await http_client.patch(f"/api/profiles/{profile_id}", json={"name": "Alicia"})
    assert patch_r.status_code == 200
    body = patch_r.json()
    assert body["updated_at"] >= created_at
