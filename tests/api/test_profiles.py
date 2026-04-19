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
