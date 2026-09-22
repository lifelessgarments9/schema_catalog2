from openai import OpenAI
from django.conf import settings

from app.ai.prompts import GENERATOR_PROMPT


class Generator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.AI_API_KEY,base_url=settings.AI_BASE_URL,)

    def generate(self, question: str, context: str, history: list) -> str:
        messages = [
            {"role": "system","content": GENERATOR_PROMPT,}
        ]

        messages.extend(
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in history
        )
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Контекст об оборудовании:\n{context}\n\n"
                    f"Вопрос пользователя:\n{question}"
                ),
            }
        )

        print(
            f"Запрос: model={settings.AI_MODEL}\n"
            f"messages={messages}"
        )

        response = self.client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=0.3,
        )

        return response.choices[0].message.content