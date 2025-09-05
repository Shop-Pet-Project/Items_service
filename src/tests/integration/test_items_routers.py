import uuid
import json
import pytest
import pytest_asyncio
from sqlalchemy import insert
from items_app.infrastructure.postgres.models import Company
from tests.integration.conftest import TestingSessionLocal, client


# --- Фикстура для передачи аргумента в роуты ---
@pytest_asyncio.fixture
async def company_id():
    async with TestingSessionLocal() as session:
        comp_id = uuid.uuid4()
        await session.execute(insert(Company).values(id=comp_id, name="Test Company"))
        await session.commit()
        return str(comp_id)


# --- Тесты ---
@pytest.mark.asyncio
async def test_create_item(client, company_id):
    response = await client.post(
        "/items",
        json={"title": "Candy", "price": 0.45, "company_id": company_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "New item created successfully"

    item_id = data["item"]["id"]
    assert uuid.UUID(item_id).version == 4
    assert data["item"]["title"] == "Candy"
    assert data["item"]["price"] == 0.45
    assert data["item"]["company_id"] == company_id


@pytest.mark.asyncio
async def test_create_item_with_invalid_data(client, company_id):
    resp = await client.post(
        "/items", json={"title": "", "price": -5, "company_id": company_id}
    )
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(error["loc"] == ["body", "title"] for error in errors)
    assert any(error["loc"] == ["body", "price"] for error in errors)


@pytest.mark.asyncio
async def test_get_item_by_id(client, company_id):
    create_resp = await client.post(
        "/items", json={"title": "Bombar", "price": 1.99, "company_id": company_id}
    )
    item_id = create_resp.json()["item"]["id"]

    get_resp = await client.get(f"/items/{item_id}", params={"company_id": company_id})
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == item_id
    assert data["title"] == "Bombar"
    assert data["price"] == 1.99
    assert data["company_id"] == company_id


@pytest.mark.asyncio
async def test_get_item_by_invalid_id(client, company_id):
    invalid_id = "123e4567-e89b-12d3-a456-426614174000"
    resp = await client.get(f"/items/{invalid_id}", params={"company_id": company_id})
    assert resp.status_code == 404
    assert resp.json()["detail"] == f"Item with item_id={invalid_id} not found"


@pytest.mark.asyncio
async def test_get_many_get_success(client, company_id):
    resp1 = await client.post(
        "/items", json={"title": "Item1", "price": 5.0, "company_id": company_id}
    )
    resp2 = await client.post(
        "/items", json={"title": "Item2", "price": 10.0, "company_id": company_id}
    )
    id1 = resp1.json()["item"]["id"]
    id2 = resp2.json()["item"]["id"]

    resp = await client.get(
        "/items/get-many",
        params={"company_id": company_id, "item_ids": [id1, id2]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert {item["id"] for item in data} == {id1, id2}


@pytest.mark.asyncio
async def test_get_many_get_empty_list(client, company_id):
    resp = await client.get("/items/get-many", params={"company_id": company_id})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "Empty list of item IDs provided"


@pytest.mark.asyncio
async def test_get_many_get_all_invalid_ids(client, company_id):
    id1 = str(uuid.uuid4())
    id2 = str(uuid.uuid4())

    resp = await client.get(
        "/items/get-many",
        params={"company_id": company_id, "item_ids": [id1, id2]},
    )
    assert resp.status_code == 404
    assert "No items found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_many_get_partial_invalid_ids(client, company_id):
    resp_valid = await client.post(
        "/items",
        json={"title": "ValidItem", "price": 7.5, "company_id": company_id},
    )
    valid_id = resp_valid.json()["item"]["id"]
    invalid_id = str(uuid.uuid4())

    resp = await client.get(
        "/items/get-many",
        params={"company_id": company_id, "item_ids": [valid_id, invalid_id]},
    )
    assert resp.status_code == 404
    assert invalid_id in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_many_post_success(client, company_id):
    resp1 = await client.post(
        "/items", json={"title": "PostItem1", "price": 5.0, "company_id": company_id}
    )
    resp2 = await client.post(
        "/items", json={"title": "PostItem2", "price": 10.0, "company_id": company_id}
    )
    id1 = resp1.json()["item"]["id"]
    id2 = resp2.json()["item"]["id"]

    payload = {"item_ids": [id1, id2]}
    resp = await client.post(
        "/items/get-many",
        params={"company_id": company_id},
        content=json.dumps(payload),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert {item["id"] for item in data} == {id1, id2}


@pytest.mark.asyncio
async def test_get_many_post_empty_list(client, company_id):
    payload = {"item_ids": []}
    resp = await client.post(
        "/items/get-many",
        params={"company_id": company_id},
        content=json.dumps(payload),
    )
    assert resp.status_code == 422
    assert resp.json()["detail"] == "Empty list of item IDs provided"


@pytest.mark.asyncio
async def test_get_many_post_all_invalid_ids(client, company_id):
    payload = {"item_ids": [str(uuid.uuid4()), str(uuid.uuid4())]}
    resp = await client.post(
        "/items/get-many",
        params={"company_id": company_id},
        content=json.dumps(payload),
    )
    assert resp.status_code == 404
    assert "No items found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_many_post_partial_invalid_ids(client, company_id):
    resp_valid = await client.post(
        "/items", json={"title": "PostValid", "price": 8.0, "company_id": company_id}
    )
    valid_id = resp_valid.json()["item"]["id"]
    invalid_id = str(uuid.uuid4())

    payload = {"item_ids": [valid_id, invalid_id]}
    resp = await client.post(
        "/items/get-many",
        params={"company_id": company_id},
        content=json.dumps(payload),
    )
    assert resp.status_code == 404
    assert invalid_id in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_all_items(client, company_id):
    await client.post(
        "/items", json={"title": "Candy", "price": 0.45, "company_id": company_id}
    )
    await client.post(
        "/items", json={"title": "Bombar", "price": 1.99, "company_id": company_id}
    )

    resp = await client.get("/items")
    assert resp.status_code == 200
    data = resp.json()
    titles = {item["title"] for item in data}
    assert {"Candy", "Bombar"} == titles


@pytest.mark.asyncio
async def test_get_all_items_with_empty_db(client):
    resp = await client.get("/items")
    data = resp.json()
    assert resp.status_code == 200
    assert data == {"message": "No items in database"}


@pytest.mark.asyncio
async def test_update_item_data_by_id(client, company_id):
    create_resp = await client.post(
        "/items", json={"title": "Cool Cola", "price": 1.45, "company_id": company_id}
    )
    item_id = create_resp.json()["item"]["id"]

    update_resp = await client.put(
        f"/items/{item_id}",
        json={"title": "Coca Cola", "price": 4.99, "company_id": company_id},
    )
    assert update_resp.status_code == 200
    upd_data = update_resp.json()
    assert upd_data["item"]["title"] == "Coca Cola"
    assert upd_data["item"]["price"] == 4.99

    get_resp = await client.get(f"/items/{item_id}", params={"company_id": company_id})
    assert get_resp.json()["title"] == "Coca Cola"


@pytest.mark.asyncio
async def test_update_item_with_invalid_data(client, company_id):
    create_resp = await client.post(
        "/items", json={"title": "Cool Cola", "price": 1.45, "company_id": company_id}
    )
    item_id = create_resp.json()["item"]["id"]

    update_resp = await client.put(
        f"/items/{item_id}", json={"title": "", "price": -10, "company_id": company_id}
    )
    assert update_resp.status_code == 422
    errors = update_resp.json()["detail"]
    assert any(error["loc"] == ["body", "title"] for error in errors)
    assert any(error["loc"] == ["body", "price"] for error in errors)


@pytest.mark.asyncio
async def test_delete_item_by_id(client, company_id):
    create_resp = await client.post(
        "/items", json={"title": "Temp", "price": 1.0, "company_id": company_id}
    )
    item_id = create_resp.json()["item"]["id"]

    del_resp = await client.delete(f"/items/{item_id}", params={"company_id": company_id})
    assert del_resp.status_code == 200
    assert f"{item_id}" in del_resp.json()["message"]

    get_resp = await client.get(f"/items/{item_id}", params={"company_id": company_id})
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_item_by_invalid_id(client, company_id):
    invalid_id = "123e4567-e89b-12d3-a456-426614174000"
    del_resp = await client.delete(f"/items/{invalid_id}", params={"company_id": company_id})
    assert del_resp.status_code == 404
    assert del_resp.json()["detail"] == f"No such item with item_id={invalid_id}"


@pytest.mark.asyncio
async def test_delete_items_by_ids(client, company_id):
    resp1 = await client.post(
        "/items", json={"title": "Item1", "price": 1.0, "company_id": company_id}
    )
    resp2 = await client.post(
        "/items", json={"title": "Item2", "price": 2.0, "company_id": company_id}
    )
    id1 = resp1.json()["item"]["id"]
    id2 = resp2.json()["item"]["id"]

    del_resp = await client.request(
        "DELETE",
        "/items/delete-many",
        params={"company_id": company_id},
        content=json.dumps({"item_ids": [id1, id2]}),
    )
    assert del_resp.status_code == 200
    assert (
        f"Items with IDs [{id1}, {id2}] have been deleted" == del_resp.json()["message"]
    )

    get_resp1 = await client.get(f"/items/{id1}", params={"company_id": company_id})
    get_resp2 = await client.get(f"/items/{id2}", params={"company_id": company_id})
    assert get_resp1.status_code == 404
    assert get_resp2.status_code == 404


@pytest.mark.asyncio
async def test_delete_items_by_invalid_ids(client, company_id):
    invalid_id1 = "123e4567-e89b-12d3-a456-426614174000"
    invalid_id2 = "123e4567-e89b-12d3-a456-426614174001"

    del_resp = await client.request(
        "DELETE",
        "/items/delete-many",
        params={"company_id": company_id},
        content=json.dumps({"item_ids": [invalid_id1, invalid_id2]}),
    )
    assert del_resp.status_code == 404
    assert (
        del_resp.json()["detail"]
        == f"No items found with IDs {invalid_id1}, {invalid_id2}"
    )


@pytest.mark.asyncio
async def test_delete_items_with_empty_list(client, company_id):
    del_resp = await client.request(
        "DELETE",
        "/items/delete-many",
        params={"company_id": company_id},
        content=json.dumps({"item_ids": []}),
    )
    assert del_resp.status_code == 422
    assert del_resp.json()["detail"] == "Empty list of item IDs provided"


@pytest.mark.asyncio
async def test_delete_items_with_partial_invalid_ids(client, company_id):
    resp = await client.post(
        "/items", json={"title": "ValidItem", "price": 3.0, "company_id": company_id}
    )
    valid_id = resp.json()["item"]["id"]
    invalid_id = "123e4567-e89b-12d3-a456-426614174000"

    del_resp = await client.request(
        "DELETE",
        "/items/delete-many",
        params={"company_id": company_id},
        content=json.dumps({"item_ids": [valid_id, invalid_id]}),
    )
    assert del_resp.status_code == 404
    assert del_resp.json()["detail"] == f"No items found with IDs {invalid_id}"
