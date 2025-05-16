import os
import sys

import aiohttp
import pytest

from configs.passwords import yandex_gpt_api_key, yandex_gpt_catalog_id

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # нужно для норм видимости коневой папки


@pytest.mark.asyncio
async def test_yagpt():
    prompt = {
        "modelUri": f"gpt://{yandex_gpt_catalog_id}/yandexgpt",
        "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": "10"},
        "messages": [{"role": "system", "text": "тест"}],
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {yandex_gpt_api_key}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, headers=headers, json=prompt, ssl=False
        ) as response:
            answer = await response.json()
            keys_list = list(answer.keys())
            if "result" in keys_list:
                pass
            elif "error" in keys_list:
                if "Unknown api key" in answer["error"]["message"]:
                    pytest.fail("неверный yandex_gpt_api_key")
                elif "Specified folder ID" in answer["error"]["message"]:
                    pytest.fail("неверный yandex_gpt_catalog_id")
                else:
                    pytest.fail("не валидные параметры авторизации")
            else:
                pytest.fail("Не известная ошибка при проверке подключения yagpt")
