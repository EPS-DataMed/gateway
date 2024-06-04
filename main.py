import jwt
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from config import SERVICE_URLS
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

security = HTTPBearer()

async def proxy_request(request: Request, service: str, path: str, credentials: HTTPAuthorizationCredentials = None):
    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")

    if service not in ["auth", "user"]:
        if not credentials:
            raise HTTPException(status_code=403, detail="Not authenticated")
        token = credentials.credentials
        verify_token(token)
    
    url = f"{SERVICE_URLS[service]}/{service}/{path}"
    logging.info(f"Proxying request to URL: {url}")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        return await forward_request(client, request, url)

async def forward_request(client: httpx.AsyncClient, request: Request, url: str):
    try:
        if request.method == "GET":
            response = await client.get(url, params=request.query_params)
        elif request.method == "POST":
            if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
                form = await request.form()
                response = await client.post(url, data=form)
            else:
                response = await client.post(url, json=await request.json())
        elif request.method == "PUT":
            response = await client.put(url, json=await request.json())
        elif request.method == "DELETE":
            response = await client.delete(url)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")

        response.raise_for_status()

        try:
            content = response.json()
        except ValueError:
            content = response.text

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

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/user/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_without_auth(request: Request, path: str):
    service = request.url.path.split('/')[1]
    return await proxy_request(request, service, path)

@app.api_route("/data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_with_auth(request: Request, service: str, path: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    service = request.url.path.split('/')[1]
    return await proxy_request(request, service, path, credentials)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
