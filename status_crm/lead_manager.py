import aiohttp
from utils.logger import setup_logger
from config.config import Config

logger = setup_logger("lead_manager")

class LeadManager:
    def __init__(self):
        self.base_url = Config.URL
        self.headers = {
            "Authorization": f"Bearer {Config.SEND_ID}",
            "Content-Type": "application/json"
        }

    async def stage_info(self, lead_id: str) -> str | None:
        url = f"{self.base_url}/{lead_id}"
        logger.debug(f"Attempting to fetch stage info for lead_id {lead_id}")  # Debug log
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        status_id = data.get("status_id")
                        logger.info(f"status id of client: {status_id}")
                        return status_id
                    elif response.status == 404:
                        return None
                    else:
                        logger.error(f"Unexpected status code for lead_id {lead_id}: {response.status}")
                        return f"Error: Unexpected status code {response.status}"
        except aiohttp.ClientResponseError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
        except Exception as e:
            # Catch unexpected exceptions and log them
            logger.error(f"Unexpected error occurred while fetching stage info for lead_id {lead_id}: {e}")



