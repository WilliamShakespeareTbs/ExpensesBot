from aiogram import Bot, Dispatcher
import asyncio
from dotenv import load_dotenv
import os

import add_expense
import config
import models
import commands, add_category, list_of_expenses

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
add_expense.bot = bot
list_of_expenses.bot = bot
dp = Dispatcher()
dp.include_routers(commands.router, add_category.router, list_of_expenses.router, add_expense.router)


async def main():
    await models.async_main()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')