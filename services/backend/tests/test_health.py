from fastapi import status


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "OK"}
