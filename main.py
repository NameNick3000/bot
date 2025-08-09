import asyncio
import datetime
from Bot import dp, bot, connect


async def main():
    await dp.start_polling(bot)


try:
    connect()
    print("\nStart!\n")
    asyncio.run(main())
except Exception as ex:
    print(f"{datetime.datetime.now()} ex: {ex}")
except KeyboardInterrupt:
    pass
print("\nStop!\n")
