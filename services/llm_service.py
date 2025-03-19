from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage , AIMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from services.promt import promt
from utils.logger import setup_logger
from vector_store.chat_history import ChatHistory
from server.send_message import send_text_message
from services.tools import get_tools
from config.config import Config


logger = setup_logger("llm_service")
history_chat = ChatHistory()


chat_memories: dict[str, ConversationBufferMemory] = {}


async def thread(message_text: str, chat_id: str, lead_id: str) -> str:
    try:
        # Если для данного chat_id ещё не создана память, инициализируем её и загружаем историю.
        if chat_id not in chat_memories:
            memory = ConversationBufferMemory(
                return_messages=True,
                input_key="input",
                memory_key="chat_history"
            )
            chat_memories[chat_id] = memory

            # Загрузка истории переписки из Chroma (уже асинхронная)
            history = await history_chat.load_history_from_chroma(chat_id)
            for msg in history:
                print(f"Загруженное сообщение: {msg}")
                memory.chat_memory.add_message(msg)
        else:
            # Если память уже существует, используем её и обновляем базу
            memory = chat_memories[chat_id]

            # Преобразование сообщений в словарь для сохранения
            messages_dict = []
            for msg in memory.chat_memory.messages:
                if isinstance(msg, HumanMessage):
                    messages_dict.append({"role": "human", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages_dict.append({"role": "ai", "content": msg.content})
                else:
                    messages_dict.append({"role": "system", "content": msg.content})

            # Асинхронное сохранение в Chroma
            await history_chat.save_to_chroma(chat_id, messages_dict)

        # Инициализация модели языка и шаблона подсказки
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=Config.OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=promt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Создание агента для вызова инструментов
        agent = create_tool_calling_agent(
            llm=llm,
            tools=await get_tools(lead_id, chat_id),
            prompt=prompt
        )

        # Создание исполнителя агента с передачей памяти и инструментов
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=await get_tools(lead_id, chat_id),
            memory=memory,
            verbose=True
        )

        # Асинхронный вызов агента с входящим сообщением
        response = await agent_executor.ainvoke({"input": message_text})
        result = response["output"]

        # Асинхронная отправка сообщения
        await send_text_message(result, chat_id)

        return result  # Возвращаем результат асинхронно

    except Exception as e:
        print(f"Ошибка в функции thread: {e}")
        return "Произошла ошибка при обработке вашего запроса."