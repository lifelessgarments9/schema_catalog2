import ollama

from app.ai.prompts import GENERATOR_PROMPT


class Generator:

    MODEL = "llama3.2:1b"

    def generate(self, question: str, context: str) -> str:

        user_content = (
            f"Контекст об оборудовании:\n{context}\n\n"
            f"Вопрос пользователя:\n{question}"
        )

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
                "num_predict": 200,
            },
        )

        return response["message"]["content"]