import aiohttp
from openai import AsyncOpenAI
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger("stt_service")

class STTService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def transcribe(self, url, model="whisper-1"):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    audio_content = await response.read()
                    try:
                        transcript = await self.client.audio.transcriptions.create(
                            model=model,
                            file=("audio_file.m4a", audio_content)
                        )
                        return transcript.text
                    except Exception as e:
                        logger.error(f"Ошибка транскрибирования: {e}")
                        return None
                else:
                    logger.error("Ошибка при скачивании аудиофайла")
                    return None