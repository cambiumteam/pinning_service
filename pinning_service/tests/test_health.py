from fastapi.testclient import TestClient

from pinning_service.main import app
from pinning_service.config import get_settings


settings = get_settings()


def test_health():
    with TestClient(app=app) as client:
        response = client.get("/health")
        health = response.json()

        # Test for correct addresses.
        assert health["manager_address"] == settings.REGEN_KEY_ADDRESS, "correct manager address"
        assert health["service_address"] == settings.REGEN_SERVICE_KEY_ADDRESS, "correct service address"

        # Test for correct authz grants.
        assert len(health["grants"]) == 1, "one authz grant exists"
        assert health["grants"][0]["authorization"]["@type"] == "/cosmos.authz.v1beta1.GenericAuthorization",\
            "service has generic authorization grant"
        assert health["grants"][0]["authorization"]["msg"] == "/regen.data.v1.MsgRegisterResolver",\
            "service has register resolver grant"

        # Test for correct feegrant allowances.
        assert health["allowance"]["granter"] == settings.REGEN_KEY_ADDRESS, "manager is the allowance granter"
        assert health["allowance"]["grantee"] == settings.REGEN_SERVICE_KEY_ADDRESS, "service is the allowance grantee"
        assert health["allowance"]["allowance"]["@type"] == "/cosmos.feegrant.v1beta1.BasicAllowance",\
            "allowance is BasicAllowance"
        assert len(health["allowance"]["allowance"]["spend_limit"]) == 1, "allowance has a spend limit"

        # Test for correct balances.
        assert len(health["balances"]) == 2, "correct number of balances"
        assert len(health["balances"][settings.REGEN_KEY_ADDRESS]) > 0, "manager has balances"
        assert len(health["balances"][settings.REGEN_SERVICE_KEY_ADDRESS]) == 0, "service has no balances"

        # Test for correct block header.
        assert int(health["latest_block_header"]["height"]) > 0, "latest block header is greater than 0"

        # Test for pending jobs.
        # TODO: Add pending jobs.
        assert health["pending_jobs"] == 0, "no pending jobs"
