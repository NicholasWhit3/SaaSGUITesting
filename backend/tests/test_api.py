import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_run_test():
    response = client.post("/api/run-test", json={
        "figma_url": "https://www.figma.com/file/dZzzith0P3zg9XNfAve0GV/Example",
        "website_url": "https://example.com",
        "selectors": "body"
    })

    assert response.status_code == 200
    data = response.json()
    assert "differences" in data
    assert "matched" in data
