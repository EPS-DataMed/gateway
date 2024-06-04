from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from config import SERVICE_URLS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, service: str, path: str):
    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")
    
    url = f"{SERVICE_URLS[service]}/{service}/{path}"
    async with httpx.AsyncClient() as client:
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
    
    return {
        "status_code": response.status_code,
        "content": response.json()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
