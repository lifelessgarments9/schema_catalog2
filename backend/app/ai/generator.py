
import ollama

from app.ai.prompts import GENERATOR_PROMPT


class Generator:
    MODEL = "qwen2.5:1.5b"

    def generate(self, question: str, context: str, history: list) -> str:
        history_text="\n".join(f"{'Пользователь' if m['role']=='user' else 'Ассистент'}:{m['content']}" for m in history)

        user_content = (
            f"Контекст об оборудовании:\n{context}\n\n"
            f"История диалога:\n{history_text}\n\n"
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
            },
        )

        return response["message"]["content"]