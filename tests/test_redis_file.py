# import pytest
# import redis
#
#
# @pytest.mark.asyncio
# async def test_redis_connection():
#     r = redis.Redis(host="localhost", port=6379, decode_responses=True)
#     try:
#         pong = r.ping()
#         assert pong is True
#         print("✅ Успешное подключение к Redis!")
#     except redis.exceptions.ConnectionError as e:
#        pytest.fail("❌ Ошибка подключения к Redis:", e)



