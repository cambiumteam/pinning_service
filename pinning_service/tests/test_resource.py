def test_valid_resource_post(client, test_jsonld_document):

    # Test that no resources exist.
    response = client.get('/resources')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

    # Post the test jsonld document.
    test_data, test_iri = test_jsonld_document
    response = client.post(
        '/resource',
        data=test_data,
        headers={
            'content-type': 'application/ld+json',
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "iri" in data
    assert data["iri"] == test_iri

    # Test that the resource was created.
    response = client.get('/resources')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    # Check the resource status.
    response = client.get(f"/resource/{test_iri}/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "pending"
