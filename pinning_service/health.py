import asyncio

from httpx import AsyncClient, RequestError, HTTPStatusError
from fastapi import APIRouter

from .config import get_settings

settings = get_settings()

# Start an API router.
router = APIRouter()


@router.get("/health")
async def health():

    manager_address = settings.REGEN_KEY_ADDRESS
    service_address = settings.REGEN_SERVICE_KEY_ADDRESS

    # Build dict of requests to execute.
    session = AsyncClient(base_url=settings.REGEN_NODE_REST_URL)
    requests = {
        "grants": get_authz_grants(session, manager_address, service_address),
        "allowance": get_feegrant_allowance(session, manager_address, service_address),
        "balances": get_multiple_account_balances(session, [manager_address, service_address]),
        "latest_block_header": get_latest_block(session),
    }

    # Collect all responses, keeping exceptions.
    responses = await asyncio.gather(*requests.values(), return_exceptions=True)
    await session.aclose()

    # Replace any exceptions with useful messages.
    final = list(map(clean_responses, responses))

    mapped_responses = dict(zip(
        requests.keys(),
        final
    ))

    return {
        "manager_address": manager_address,
        "service_address": service_address,
        **mapped_responses,
    }


def clean_responses(response: any):
    if isinstance(response, RequestError):
        return f"Failed to request data from regen node: {settings.REGEN_NODE_REST_URL}"
    elif isinstance(response, HTTPStatusError):
        return f"Invalid request. Ensure addresses are correctly configured and exist on-chain."
    elif isinstance(response, Exception):
        return "Unknown error."
    else:
        return response


async def get_latest_block(session: AsyncClient) -> dict:
    response = await session.get("blocks/latest")
    return response.json().get("block", {}).get("header", {})


async def get_authz_grants(session: AsyncClient, granter_address: str, grantee_address: str) -> dict:
    response = await session.get("cosmos/authz/v1beta1/grants", params={"granter": granter_address, "grantee": grantee_address})
    return response.json().get("grants", [])


async def get_feegrant_allowance(session: AsyncClient, granter_address: str, grantee_address: str) -> dict:
    response = await session.get(f"cosmos/feegrant/v1beta1/allowance/{granter_address}/{grantee_address}")
    return response.json().get("allowance", {})


async def get_multiple_account_balances(session: AsyncClient, addresses: list[str]) -> dict:
    return {address: await get_account_balances(session, address) for address in addresses}


async def get_account_balances(session: AsyncClient, address: str) -> list:
    response = await session.get(f"cosmos/bank/v1beta1/balances/{address}")
    return response.json().get("balances", [])
