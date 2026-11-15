import logging
import httpx
from bot.config import settings

logger = logging.getLogger(__name__)


class BackendAPIClient:
    def __init__(self):
        self.base_url = settings.BACKEND_URL.rstrip("/")

    async def create_product(
        self,
        title: str,
        file_bytes: bytes,
        filename: str = "photo.jpg",
        content_type: str = "image/jpeg",
        price: float = 0.0,
        description: str = "",
        telegram_file_id: str = None,
    ) -> dict:
        url = f"{self.base_url}/api/products/upload"
        files = {
            "file": (filename, file_bytes, content_type),
        }
        data = {
            "title": title,
            "price": str(price),
            "description": description,
        }
        if telegram_file_id:
            data["telegram_file_id"] = telegram_file_id

        headers = {
            "X-Admin-Secret": settings.ADMIN_API_KEY,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=data, files=files, headers=headers)
            if resp.status_code != 201:
                logger.error("Backend error %s: %s", resp.status_code, resp.text)
                raise RuntimeError(f"Backend API error: {resp.status_code} - {resp.text}")
            return resp.json()

    async def get_products(self) -> list[dict]:
        url = f"{self.base_url}/api/products"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])


api_client = BackendAPIClient()
