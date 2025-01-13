from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from src.config import GIGACHAT_API_KEY as GIGA_TOKEN


class LangChainService:
    def __init__(self):
        self.llm = GigaChat(
            credentials=GIGA_TOKEN,
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
            verify_ssl_certs=False,
            streaming=False
        )
        self.system_message = SystemMessage(
            content=(
                "Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы. "
                "Отправь 3 коротких совета для улучшения психологического состояния пользователя. "
                "Посетить психолога ты уже советовал."
            )
        )

    async def analyze_user_data(self, analysis_text: str) -> str:
        messages = [
            self.system_message,
            HumanMessage(
                content=(
                    f"Вот данные пользователя за разные периоды:\n\n"
                    f"{analysis_text}\n\n"
                    "Проанализируй данные. Какие есть закономерности или интересные моменты? Какие рекомендации можно дать пользователю?"
                )
            )
        ]
        response = self.llm.invoke(messages)
        return response.content