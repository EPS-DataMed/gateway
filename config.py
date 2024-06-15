import os
from dotenv import load_dotenv

load_dotenv()

def get_service_url(service_name, domain):
    return f"https://{service_name}.{domain}"


auth_service_name = os.getenv("AUTH_SERVICE_NAME")
user_service_name = os.getenv("USER_SERVICE_NAME")
file_service_name = os.getenv("FILE_SERVICE_NAME")
data_service_name = os.getenv("DATA_SERVICE_NAME")

service_domain = os.getenv("SERVICE_DOMAIN")

SERVICE_URLS = {
    "auth": get_service_url(auth_service_name, service_domain),
    "user": get_service_url(user_service_name, service_domain),
    "file": get_service_url(file_service_name, service_domain),
    "data": get_service_url(data_service_name, service_domain)
}
