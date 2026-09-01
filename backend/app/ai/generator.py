
import ollama

from app.ai.prompts import GENERATOR_PROMPT


class Generator:
    MODEL = "qwen2.5:7b-instruct"

    def generate(self, question: str, context: str) -> str:

        user_content = (
            f"Контекст об оборудовании:\n{context}\n\n"
            f"Вопрос пользователя:\n{question}"
        )

        print(f"Запрос: model={self.MODEL}, {user_content}")

        response = ollama.chat(
            model=self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": GENERATOR_PROMPT
                },
                {
                    "role": "user",
                    "content": user_content
                },
            ],
            options={
                "temperature": 0.3,
                "num_predict": 400,
            },
        )

        return response["message"]["content"]