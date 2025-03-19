import os
import json
import chromadb
from datetime import datetime
from config.config import Config
from langchain_core.messages import HumanMessage, AIMessage
from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction
from utils.logger import setup_logger

logger = setup_logger("chat_history.py")

class ChatHistory:
    def __init__(self):
        # Определяем путь к корневой директории проекта
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.chroma_db_path = os.path.join(root_dir, 'chroma_db')

        # Проверяем, существует ли папка, и создаем её, если нет
        if not os.path.exists(self.chroma_db_path):
            os.makedirs(self.chroma_db_path)

        # Инициализируем клиент с абсолютным путём к папке chroma_db
        self.client = chromadb.PersistentClient(path=self.chroma_db_path)
        self.embedding_function = OpenAIEmbeddingFunction(
            api_key=Config.OPENAI_API_KEY,
            model_name="text-embedding-ada-002"
        )
        # Создаем или получаем коллекцию для истории чата
        self.collection = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    async def save_to_chroma(self, chat_id: str, messages: list):
        documents = []
        metadatas = []
        ids = []

        for i, msg in enumerate(messages):
            # Извлекаем контент и роль из сообщения
            if isinstance(msg, dict):
                content = msg.get("content", "")
                role = msg.get("role", "unknown")
            else:
                content = str(msg)
                role = "unknown"

            documents.append(content)
            metadatas.append({
                "chat_id": chat_id,
                "role": role,
                "timestamp": datetime.now().isoformat()
            })
            # Формируем уникальный идентификатор, комбинируя chat_id и индекс
            ids.append(f"{chat_id}_{i}")

        try:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info("Данные истории чата успешно сохранены в ChromaDB")
        except Exception as e:
            logger.error(f"Ошибка при сохранении истории чата в ChromaDB: {str(e)}")
            raise

        # Сохраняем список id в отдельном файле для последующего удаления
        ids_file = os.path.join(self.chroma_db_path, f'saved_chat_ids_{chat_id}.json')
        try:
            with open(ids_file, 'w', encoding='utf-8') as f:
                json.dump(ids, f)
            logger.info(f"Список id сохранён в файле {ids_file}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении id: {e}")

    async def load_history_from_chroma(self, chat_id: str) -> list:
        try:
            results = self.collection.get(
                where={"chat_id": chat_id},
                limit=100,
            )
        except Exception as e:
            logger.error(f"Ошибка при загрузке истории чата: {str(e)}")
            return []

        history = []
        for doc, meta in zip(results.get('documents', []), results.get('metadatas', [])):
            role = meta.get('role', 'unknown')
            if role == "human":
                history.append(HumanMessage(content=doc))
            else:
                history.append(AIMessage(content=doc))

        return history

    async def delete_all_chat_history(self, chat_id: str):
        """
        Удаляет все сообщения истории чата по заданному chat_id.
        Использует сохранённый файл с id для удаления данных из коллекции.
        """
        ids_file = os.path.join(self.chroma_db_path, f'saved_chat_ids_{chat_id}.json')

        # Проверка существования файла с id
        if not os.path.exists(ids_file):
            logger.warning(f"Файл {ids_file} не найден, удаление данных не требуется.")
            return

        try:
            with open(ids_file, 'r', encoding='utf-8') as f:
                saved_ids = json.load(f)
            logger.info(f"Считан список id для удаления: {saved_ids}")
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {ids_file}: {e}")
            return

        try:
            self.collection.delete(ids=saved_ids)
            logger.info("Все данные истории чата успешно удалены из базы данных")
            # Опционально: удаляем файл с id после успешного удаления данных
            os.remove(ids_file)
            logger.info(f"Файл {ids_file} удалён")
        except Exception as e:
            logger.error(f"Ошибка при удалении данных истории чата: {e}")
