import pathlib
from datetime import datetime, timedelta

from loguru import logger
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_indexes import VectorSearchIndexType

from configs.passwords import yandex_gpt_api_key, yandex_gpt_catalog_id

PROMPTS_DIR = pathlib.Path("prompts/")
FILE_LABELS = [
    {"organization": "Файл с общей информацией о нашей организации и функциональности бота"},
    {"product_catalog": "Файл с общей информацией о товаре"},
    # {"products": "Файл содержащий подробные данные про каждый товар в виде словаря, где ключ включает в себя артикул и"
    #              "название товара разделенные '__'"}
]
INDEX_LABEL = {
    "promo": "Индекс содержит общую информацию о нашей организации и функциональности бота",
    "categories": "Индекс содержит информацию о категориях товаров",
    # "prod": "Индекс содержит информацию о товарах"
}


class AssistantManager:
    def __init__(self, sdk):
        self.sdk = sdk
        self.search_index = None
        self.assistant = None
        self.thread = None
        self.files = []
        self.last_update: datetime | None = None

    @classmethod
    async def create(cls):
        sdk = YCloudML(folder_id=yandex_gpt_catalog_id, auth=yandex_gpt_api_key)
        return cls(sdk)

    async def initialize(self):
        if not self.needs_update():
            logger.info("Ассистент актуален, переиспользуем текущие сущности.")
            return

        logger.info("Инициализация файлов, индекса и ассистента...")
        await self.cleanup()

        paths = list(PROMPTS_DIR.iterdir())
        for i, path in enumerate(paths):
            file = self.sdk.files.upload(
                path,
                ttl_days=10,
                expiration_policy="since_last_active",
                name=str(path.name),
                labels=FILE_LABELS[i % len(FILE_LABELS)],
            )
            self.files.append(file)

        operation = self.sdk.search_indexes.create_deferred(
            self.files,
            index_type=VectorSearchIndexType(),
            name="the-opt-from-china-index",
            labels=INDEX_LABEL,
        )
        self.search_index = operation.wait()

        tool = self.sdk.tools.search_index(self.search_index)
        self.assistant = self.sdk.assistants.create(
            "yandexgpt",
            tools=[tool],
            instruction="Ты ассистент, который вежливо помогает людям по информации из предоставленных источников. Отвечай четко и по делу."
        )
        self.thread = self.sdk.threads.create()
        self.last_update = datetime.now()
        logger.info("Инициализация завершена.")

    def needs_update(self) -> bool:
        return not self.last_update or (datetime.now() - self.last_update > timedelta(days=10))

    async def get_response(self, text: str) -> str:
        await self.initialize()
        self.thread.write(text)
        run = self.assistant.run(self.thread)
        result = run.wait()
        return result.text

    async def manual_reload(self):
        logger.info("Ручная перезагрузка ассистента по команде администратора.")
        await self.cleanup()
        await self.initialize()

    async def cleanup(self):
        logger.info("Очистка старых сущностей...")
        if self.thread:
            self.thread.delete()
            self.thread = None
        if self.assistant:
            self.assistant.delete()
            self.assistant = None
        if self.search_index:
            self.search_index.delete()
            self.search_index = None
        for f in self.files:
            f.delete()
        self.files.clear()
        logger.info("Очистка завершена.")


_assistant_instance = None

async def get_assistant_manager():
    global _assistant_instance
    if _assistant_instance is None:
        print("Создаю экземпляр AssistantManager...")
        _assistant_instance = await AssistantManager.create()
    return _assistant_instance


