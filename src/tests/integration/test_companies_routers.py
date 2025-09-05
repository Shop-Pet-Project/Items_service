import uuid
import pytest
from items_app.infrastructure.postgres.models import Base
from tests.integration.conftest import client


# --- Тесты ---
@pytest.mark.asyncio
async def test_create_company(client):
    resp = await client.post("/companies", json={"name": "Test Company"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "New company created successfully"
    assert data["company"]["name"] == "Test Company"
    assert uuid.UUID(data["company"]["id"])


@pytest.mark.asyncio
async def test_create_company_invalid_payload(client):
    resp = await client.post("/companies", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_company_missing_name(client):
    resp = await client.post("/companies", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_company_by_id(client):
    create_resp = await client.post("/companies", json={"name": "Acme Inc"})
    company_id = create_resp.json()["company"]["id"]

    get_resp = await client.get(f"/companies/{company_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == company_id
    assert data["name"] == "Acme Inc"


@pytest.mark.asyncio
async def test_get_company_by_id_not_found(client):
    random_id = str(uuid.uuid4())
    resp = await client.get(f"/companies/{random_id}")
    assert resp.status_code == 404
    assert f"company_id={random_id}" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_all_companies_success(client):
    await client.post("/companies", json={"name": "Comp1"})
    await client.post("/companies", json={"name": "Comp2"})

    resp = await client.get("/companies")
    assert resp.status_code == 200
    names = {c["name"] for c in resp.json()}
    assert {"Comp1", "Comp2"} <= names


@pytest.mark.asyncio
async def test_get_all_companies_pagination(client):
    for i in range(15):
        await client.post("/companies", json={"name": f"Comp{i}"})

    resp = await client.get("/companies?offset=5&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_get_all_companies_with_empty_db(client):
    resp = await client.get("/companies")
    assert resp.status_code == 200
    assert resp.json() == {"message": "No companies in database"}


@pytest.mark.asyncio
async def test_update_company_by_id(client):
    create_resp = await client.post("/companies", json={"name": "Old Name"})
    company_id = create_resp.json()["company"]["id"]

    update_payload = {"id": company_id, "name": "New Name"}
    update_resp = await client.put(f"/companies/{company_id}", json=update_payload)
    assert update_resp.status_code == 200
    upd_data = update_resp.json()
    assert upd_data["message"] == "Company updated successfully"
    assert upd_data["company"]["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_company_not_found(client):
    random_id = str(uuid.uuid4())
    update_payload = {"id": random_id, "name": "NoName"}
    resp = await client.put(f"/companies/{random_id}", json=update_payload)
    assert resp.status_code == 404
    assert f"company_id={random_id}" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_company_invalid_payload(client):
    resp = await client.put("/companies/some-id", json={"name": "NameOnly"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_delete_company_success(client):
    create_resp = await client.post("/companies", json={"name": "DeleteMe"})
    company_id = create_resp.json()["company"]["id"]

    del_resp = await client.delete(f"/companies/{company_id}")
    assert del_resp.status_code == 200
    assert "deleted successfully" in del_resp.json()["message"]


@pytest.mark.asyncio
async def test_delete_company_not_found(client):
    random_id = str(uuid.uuid4())
    resp = await client.delete(f"/companies/{random_id}")
    assert resp.status_code == 404
    assert f"company_id={random_id}" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_delete_company_invalid_id(client):
    resp = await client.delete("/companies/invalid-uuid")
    assert resp.status_code == 422
