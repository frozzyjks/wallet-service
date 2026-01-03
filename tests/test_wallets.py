import uuid
import asyncio
import pytest

pytestmark = pytest.mark.asyncio


async def test_healthcheck(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_deposit_creates_wallet(client):
    wallet_id = str(uuid.uuid4())
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 1000},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 1000


async def test_withdraw_success(client):
    wallet_id = str(uuid.uuid4())
    await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 1000},
    )
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 400},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 600


async def test_withdraw_not_enough_money(client):
    wallet_id = str(uuid.uuid4())
    await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 300},
    )
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 500},
    )
    assert response.status_code == 400


async def test_concurrent_withdraw(client):
    wallet_id = str(uuid.uuid4())
    await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 1000},
    )

    r1 = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 600},
    )
    r2 = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 600},
    )

    statuses = sorted([r1.status_code, r2.status_code])
    assert statuses == [200, 400]  # Один успел, второму не хватило