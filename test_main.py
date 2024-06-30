import os
import pytest
import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app, verify_token, forward_request
from unittest.mock import patch, AsyncMock, MagicMock
import jwt
import asyncio

client = TestClient(app)

# Setup de variáveis de ambiente para testes
os.environ["SECRET_KEY"] = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
os.environ["ALGORITHM"] = "HS256"
os.environ["AUTH_SERVICE_NAME"] = "authentication-kw8k"
os.environ["USER_SERVICE_NAME"] = "user-service-evf6"
os.environ["FILE_SERVICE_NAME"] = "file-manager-iuhn"
os.environ["DATA_SERVICE_NAME"] = "data-processing-otv0"
os.environ["TERM_SERVICE_NAME"] = "term-service"
os.environ["SERVICE_DOMAIN"] = "onrender.com"

def test_root():
    response = client.get("/")
    assert response.status_code == 404  # Assumindo que "/" não está definido em main.py

@patch("main.SERVICE_URLS", {
    "auth": "https://authentication-kw8k.onrender.com",
    "term": "https://term-service.onrender.com"
})
@patch("main.forward_request", new_callable=AsyncMock)
def test_proxy_without_auth(mock_forward_request):
    mock_forward_request.return_value = MagicMock(status_code=200, json=MagicMock(return_value={"message": "success"}))
    response = client.get("/term/somepath")
    assert response.status_code == 200

@patch("main.SERVICE_URLS", {
    "user": "https://user-service-evf6.onrender.com",
    "data": "https://data-processing-otv0.onrender.com",
    "file": "https://file-manager-iuhn.onrender.com"
})
@patch("main.verify_token")
@patch("main.forward_request", new_callable=AsyncMock)
def test_proxy_with_auth(mock_forward_request, mock_verify_token):
    mock_verify_token.return_value = {"user_id": 123}
    mock_forward_request.return_value = MagicMock(status_code=200, json=MagicMock(return_value={"message": "success"}))
    response = client.get("/user/somepath", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200

def test_verify_token_invalid():
    with pytest.raises(HTTPException) as excinfo:
        invalid_token = "invalid.token.value"
        verify_token(invalid_token)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token"

def test_verify_token_expired():
    expired_token = jwt.encode({"exp": 0}, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    with pytest.raises(HTTPException) as excinfo:
        verify_token(expired_token)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token has expired"

def test_verify_token_valid():
    valid_token = jwt.encode({"user_id": 123}, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    payload = verify_token(valid_token)
    assert payload["user_id"] == 123

@patch("main.httpx.AsyncClient.get", new_callable=AsyncMock)
def test_forward_request_get(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"message": "success"})
    mock_response.text = '{"message": "success"}'
    mock_get.return_value = mock_response

    async def run_test():
        async with httpx.AsyncClient() as client:
            mock_request = MagicMock(method="GET", query_params={})
            response = await forward_request(client, mock_request, "https://example.com/test")
        response_content = await (response["content"] if callable(response["content"]) else response["content"])
        assert response["status_code"] == 200
        assert response_content == {"message": "success"}
        mock_get.assert_called_once_with("https://example.com/test", params={})

    asyncio.run(run_test())

@patch("main.httpx.AsyncClient.post", new_callable=AsyncMock)
def test_forward_request_post(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"message": "success"})
    mock_post.return_value = mock_response

    async def run_test():
        async with httpx.AsyncClient() as client:
            mock_request = MagicMock(method="POST", headers={"Content-Type": "application/json"}, json=AsyncMock(return_value={"key": "value"}))
            response = await forward_request(client, mock_request, "https://example.com/test")
        response_content = await (response["content"] if callable(response["content"]) else response["content"])
        assert response["status_code"] == 200
        assert response_content == {"message": "success"}
        mock_post.assert_called_once_with("https://example.com/test", json={"key": "value"})

    asyncio.run(run_test())

@patch("main.httpx.AsyncClient.put", new_callable=AsyncMock)
def test_forward_request_put(mock_put):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"message": "success"})
    mock_put.return_value = mock_response

    async def run_test():
        async with httpx.AsyncClient() as client:
            mock_request = MagicMock(method="PUT", headers={"Content-Type": "application/json"}, json=AsyncMock(return_value={"key": "value"}))
            response = await forward_request(client, mock_request, "https://example.com/test")
        response_content = await (response["content"] if callable(response["content"]) else response["content"])
        assert response["status_code"] == 200
        assert response_content == {"message": "success"}
        mock_put.assert_called_once_with("https://example.com/test", json={"key": "value"})

    asyncio.run(run_test())

@patch("main.httpx.AsyncClient.patch", new_callable=AsyncMock)
def test_forward_request_patch(mock_patch):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"message": "success"})
    mock_patch.return_value = mock_response

    async def run_test():
        async with httpx.AsyncClient() as client:
            mock_request = MagicMock(method="PATCH", headers={"Content-Type": "application/json"}, json=AsyncMock(return_value={"key": "value"}))
            response = await forward_request(client, mock_request, "https://example.com/test")
        response_content = await (response["content"] if callable(response["content"]) else response["content"])
        assert response["status_code"] == 200
        assert response_content == {"message": "success"}
        mock_patch.assert_called_once_with("https://example.com/test", json={"key": "value"})

    asyncio.run(run_test())

@patch("main.httpx.AsyncClient.delete", new_callable=AsyncMock)
def test_forward_request_delete(mock_delete):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"message": "success"})
    mock_delete.return_value = mock_response

    async def run_test():
        async with httpx.AsyncClient() as client:
            mock_request = MagicMock(method="DELETE")
            response = await forward_request(client, mock_request, "https://example.com/test")
        response_content = await (response["content"] if callable(response["content"]) else response["content"])
        assert response["status_code"] == 200
        assert response_content == {"message": "success"}
        mock_delete.assert_called_once_with("https://example.com/test")

    asyncio.run(run_test())

@patch("main.httpx.AsyncClient.get", new_callable=AsyncMock)
def test_forward_request_http_status_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_get.return_value = mock_response
    mock_get.side_effect = httpx.HTTPStatusError(
        message="Not Found",
        request=MagicMock(url="https://example.com/test"),
        response=mock_response,
    )

    async def run_test():
        async with httpx.AsyncClient() as client:
            mock_request = MagicMock(method="GET", query_params={})
            with pytest.raises(HTTPException) as excinfo:
                await forward_request(client, mock_request, "https://example.com/test")
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Not Found"

    asyncio.run(run_test())

@patch("main.httpx.AsyncClient.get", new_callable=AsyncMock)
def test_forward_request_request_error(mock_get):
    mock_get.side_effect = httpx.RequestError(
        message="Error",
        request=MagicMock(url="https://example.com/test")
    )

    async def run_test():
        async with httpx.AsyncClient() as client:
            mock_request = MagicMock(method="GET", query_params={})
            with pytest.raises(HTTPException) as excinfo:
                await forward_request(client, mock_request, "https://example.com/test")
        assert excinfo.value.status_code == 500
        assert excinfo.value.detail == "Internal Server Error"

    asyncio.run(run_test())

