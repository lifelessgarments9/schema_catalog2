import openai
from django.conf import settings

client = openai.OpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_BASE_URL, )
models=client.models.list()
print(models.data)
