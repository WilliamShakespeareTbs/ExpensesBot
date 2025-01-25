from aiogram import Bot, Dispatcher
import asyncio
from dotenv import load_dotenv
import os

import add_expense
import models
import commands, add_category, list_of_expenses, delete_exp, delete_cat, edit_cat, edit_exp, listing_pages

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()
dp.include_routers(commands.router,
                   listing_pages.router,
                   add_category.router, 
                   list_of_expenses.router, 
                   add_expense.router,
                   delete_exp.router, 
                   delete_cat.router, 
                   edit_cat.router, 
                   edit_exp.router, 
                   )


async def main():
    await models.async_main()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
        