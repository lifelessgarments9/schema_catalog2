import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import openai
from django.conf import settings

client = openai.OpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_BASE_URL, )
models=client.models.list()
for model in models.data:
    print(model)
