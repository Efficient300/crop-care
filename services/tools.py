from services.tools_func import Tools
from langchain.tools import Tool


async def get_tools(lead_id: str , chat_id: str):
    tools_instance = Tools(lead_id , chat_id)
    return [

        Tool(
            name="get_time",
            func=None,
            coroutine=tools_instance.get_current_time,
            description="Используйте, чтобы получить текущее время и дату"
        ),



    ]
