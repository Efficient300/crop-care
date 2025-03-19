import requests
from config.config import Config
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger("amo_data")

def amo_api_data() -> Optional[Dict[str, str]]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "amo_host": Config.AMO_HOST,
        "amo_password": Config.AMO_PASSWORD,
        "amo_email": Config.AMO_EMAIL
    }

    try:
        response = requests.post(Config.TOKEN_GET_URL, json=payload, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return {
                "amojo_id": response_data.get('amojo_id'),
                "chat_token": response_data.get('chat_token')
            }
        else:
            logger.error(f"HTTP ошибка: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Произошла неизвестная ошибка: {e}")

    return None
