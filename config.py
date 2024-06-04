import os

def get_service_url(service_name, dev_port):
    env = os.getenv("ENV")
    if env == "development":
        return f"http://localhost:{dev_port}"
    else:
        return f"https://{service_name}.onrender.com"

SERVICE_URLS = {
    "auth": get_service_url("authentication-y2qu", 8001),
    "user": get_service_url("user-service-3uq2", 8002),
    "data": get_service_url("data-processing-service", 8003),
}
