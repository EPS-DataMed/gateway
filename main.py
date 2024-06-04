from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from config import SERVICE_URLS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, service: str, path: str):
    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")
    
    url = f"{SERVICE_URLS[service]}/{service}/{path}"
    logging.info(f"Proxying request to URL: {url}")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            if request.method == "GET":
                response = await client.get(url, params=request.query_params)
            elif request.method == "POST":
                response = await client.post(url, json=await request.json())
            elif request.method == "PUT":
                response = await client.put(url, json=await request.json())
            elif request.method == "DELETE":
                response = await client.delete(url)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            response.raise_for_status()  # Levanta uma exceção para códigos de status HTTP não 2xx

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
