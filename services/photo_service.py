import aiohttp
import base64
import ssl
import certifi
import asyncio
from aiohttp import TCPConnector
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from utils.logger import setup_logger

# Настройка логгера
logger = setup_logger("photo_service")

class PhotoDescription(BaseModel):
    description: str = Field(description="Краткое описание")

class PhotoService:
    def __init__(self):
        # Инициализация LangChain модели
        self.model = ChatOpenAI(model="gpt-4o")  # Убедитесь, что модель указана правильно
        self.parser = PydanticOutputParser(pydantic_object=PhotoDescription)

        # Шаблон для обработки изображений
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Верните запрашиваемый объект ответа на русском языке.\n'{format_instructions}'\n"),
            ("human", [
                {
                    "type": "image_url",
                    "image_url": "{image_url}",
                },
            ]),
        ])
        self.chain = self.prompt | self.model | self.parser
        logger.info("PhotoService инициализирован.")

    async def validate_url(self, image_url: str) -> bool:
        """Проверяет доступность URL."""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        try:
            async with aiohttp.ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
                async with session.head(image_url, timeout=5) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Ошибка проверки доступности URL: {e}")
            return False

    async def fetch_image(self, image_url: str) -> bytes:
        """Загружаем изображение с помощью aiohttp."""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        try:
            async with aiohttp.ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
                async with session.get(image_url, timeout=10) as response:
                    if response.status != 200:
                        raise Exception(f"Не удалось загрузить изображение. Статус: {response.status}, URL: {image_url}")
                    return await response.read()
        except Exception as e:
            logger.error(f"Ошибка при загрузке изображения с {image_url}: {e}", exc_info=True)
            raise

    async def process_image_from_url(self, image_url: str):
        """Обрабатываем изображение по URL."""
        try:
            # Проверяем доступность URL
            if not await self.validate_url(image_url):
                raise Exception(f"URL недоступен или ресурс не найден: {image_url}")

            # Загружаем изображение
            image_bytes = await self.fetch_image(image_url)

            # Кодируем в base64
            image_data = base64.b64encode(image_bytes).decode("utf-8")
            image_payload = f"data:image/jpeg;base64,{image_data}"

            # Обрабатываем изображение через LangChain
            result = await asyncio.to_thread(
                self.chain.invoke,
                {
                    "language": "Russian",
                    "format_instructions": self.parser.get_format_instructions(),
                    "image_url": image_payload
                }
            )
            logger.info("Изображение успешно обработано.")
            return result.model_dump_json(indent=2)
        except Exception as e:
            logger.error(f"Ошибка при обработке изображения из URL: {e}", exc_info=True)
            return None
