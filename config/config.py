from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
    ASSIST_ID = os.getenv('OPENAI_ASSISTANT_ID')
    ORDER_GROUP_ID = os.getenv('ORDER_GROUP_ID')
    TG_BOT_TOKEN = os.getenv('TOKEN')
    SEND_ID = os.getenv("SEND_ID")
    MESSAGE_SAND_URL = os.getenv("MESSAGE_SAND_URL")
    TOKEN_GET_URL = os.getenv("TOKEN_GET_URL")
    AMO_HOST = os.getenv("AMO_HOST")
    AMO_PASSWORD = os.getenv("AMO_PASSWORD")
    AMO_EMAIL = os.getenv("AMO_EMAIL")
    URL = os.getenv("URL")
    VECTOR_ID = os.getenv("VECTOR_ID")
    AI_WORKS = int(os.getenv("AI_WORKS"))
    UNSORTED = int(os.getenv("UNSORTED"))
