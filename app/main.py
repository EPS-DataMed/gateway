import os
import jwt
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from app.config import SERVICE_URLS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logging.info(f"Token verified: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logging.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        logging.warning("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

security = HTTPBearer()

async def proxy_request(request: Request, service: str, path: str, credentials: HTTPAuthorizationCredentials = None):
    if service not in SERVICE_URLS:
        logging.error(f"Service not found: {service}")
        raise HTTPException(status_code=404, detail="Service not found")

    if service not in ["auth", "term"]:
        if not credentials:
            logging.warning("Not authenticated")
            raise HTTPException(status_code=403, detail="Not authenticated")
        token = credentials.credentials
        verify_token(token)

    url = f"{SERVICE_URLS[service]}/{service}/{path}"
    logging.info(f"Proxying request to URL: {url}")

    async with httpx.AsyncClient(timeout=120.0) as client:
        return await forward_request(client, request, url)

async def forward_request(client: httpx.AsyncClient, request: Request, url: str):
    try:
        logging.info(f"Forwarding {request.method} request to {url}")

        if request.method == "GET":
            response = await client.get(url, params=request.query_params)
        elif request.method == "POST":
            content_type = request.headers.get("Content-Type")
            logging.info(f"Content-Type: {content_type}")

            if content_type == "application/x-www-form-urlencoded":
                form = await request.form()
                response = await client.post(url, data=form)
            elif content_type == "application/json":
                response = await client.post(url, json=await request.json())
            else:
                response = await client.post(url, content=await request.body())
        elif request.method == "PUT":
            if request.headers.get("Content-Type") == "application/json":
                response = await client.put(url, json=await request.json())
            else:
                response = await client.put(url, content=await request.body())
        elif request.method == "PATCH":
            if request.headers.get("Content-Type") == "application/json":
                response = await client.patch(url, json=await request.json())
            else:
                response = await client.patch(url, content=await request.body())
        elif request.method == "DELETE":
            response = await client.delete(url)
        else:
            logging.error(f"Method not allowed: {request.method}")
            raise HTTPException(status_code=405, detail="Method not allowed")

        response.raise_for_status()

        try:
            content = response.json()
            logging.info(f"Response received with status {response.status_code}: {content}")
        except ValueError:
            content = response.text
            logging.info(f"Response received with status {response.status_code}: {content}")

        return {
            "status_code": response.status_code,
            "content": content
        }
    except httpx.RequestError as exc:
        logging.error(f"An error occurred while requesting {exc.request.url!r}.")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except httpx.HTTPStatusError as exc:
        logging.error(f"Non-successful status code {exc.response.status_code} while requesting {exc.request.url!r}.")
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.TimeoutException:
        logging.error(f"Request to {url} timed out.")
        raise HTTPException(status_code=504, detail="Gateway Timeout")


@app.api_route("/term/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_without_auth(request: Request, path: str):
    service = request.url.path.split('/')[1]
    logging.info(f"Request received for service: {service}, path: {path}")
    return await proxy_request(request, service, path)

@app.api_route("/user/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.api_route("/data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/file/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_with_auth(request: Request, path: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    service = request.url.path.split('/')[1]
    logging.info(f"Authenticated request received for service: {service}, path: {path}")
    return await proxy_request(request, service, path, credentials)