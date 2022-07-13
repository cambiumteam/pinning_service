from datetime import datetime

import pytest

from pinning_service.database import update_iris_txhash
from pinning_service.regen import anchor


@pytest.mark.anyio
async def test_resource_post(client, test_jsonld_document):

    # Test that no resources exist.
    response = await client.get('/resources')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

    # Post the test jsonld document.
    test_data, test_iri = test_jsonld_document
    response = await client.post(
        '/resource',
        content=test_data,
        headers={
            'content-type': 'application/ld+json',
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "iri" in data
    assert data["iri"] == test_iri

    # Test that the resource was created.
    response = await client.get('/resources')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    # Check the resource status.
    response = await client.get(f"/resource/{test_iri}/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "pending"

    # Anchor the resource.
    txhash = anchor([test_iri])
    assert txhash is not None

    # Update the IRI txhash and status.
    await update_iris_txhash([test_iri], txhash, datetime.now())

    # Check the resource status.
    response = await client.get(f"/resource/{test_iri}/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
