from utils.logger import setup_logger
from datetime import datetime


logger = setup_logger("llm_tools")


class Tools:
    def __init__(self, lead_id: str, chat_id: str):
        self.lead_ids = lead_id
        self.chat_id = chat_id



    @staticmethod
    async def get_current_time(*args, **kwargs):
        today = datetime.now()
        current_time = today.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Инструмент 'get_time' вызван. Возвращает: {current_time}")
        return {"tool_name": "get_time", "value": current_time}  # Возвращаем словарь







