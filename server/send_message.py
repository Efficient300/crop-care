import re
import aiohttp
from pathlib import Path
from config.config import Config
from server.amo_data import amo_api_data
from utils.logger import setup_logger
from utils.MarkdownProcessor import MarkdownProcessor

logger = setup_logger("send_message")
PHOTOS_DIR = Path(__file__).resolve().parent.parent / "photos"

async def send_text_message(massage, chat_id):
    amo_data = amo_api_data()
    clean_text = re.sub(r'~|【.*?】.*', '', await MarkdownProcessor.strip_markdown(massage))

    for part in re.split(r"\n\s*\n", clean_text):
        msg = part.strip()
        if not msg:
            continue

        data = {
            "message": msg,
            "chat_id": chat_id,
            "chat_token": amo_data["chat_token"],
            "amojo_id": amo_data["amojo_id"],
            "token": Config.SEND_ID
        }

        async with aiohttp.ClientSession() as s:
            async with s.post(Config.MESSAGE_SAND_URL, data=data) as r:
                r.raise_for_status()
                logger.info("Сообщение отправлено")
