from models import Base, User, Category, Expence, async_session
from sqlalchemy import select, insert
from models import User


async def find_id_by_tg_id(tg_id):
    async with async_session() as session:
        query = select(User).filter_by(tg_id = tg_id)
        result = await session.execute(query)
        our_user = result.scalars().all()
        for i in our_user:
            return i.id


async def add_category(category_name, tg_id):
    user_id = await find_id_by_tg_id(tg_id)
    async with async_session() as session:
        new_category = Category(name = category_name, user_id = user_id, sum = 0)
        session.add(new_category)
        await session.commit()


async def get_categories(tg_id):
    async with async_session() as session:
        user_id = await find_id_by_tg_id(tg_id)
        query = select(Category).filter_by(user_id = user_id)
        result = await session.execute(query)
        cat_dict = result.scalars().all()
        dict_sorted_by_name = dict()
        for i in cat_dict:
            dict_sorted_by_name.update({i.id : i.name})
        return dict_sorted_by_name


async def check_for_user(int):
    async with async_session() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        for u in users:
            if u.tg_id == int:
                return False
        return True


async def add_new_user(tg_id):
    new_user = User(tg_id = tg_id)
    async with async_session() as session:
        session.add(new_user)
        await session.commit()
    await add_category('Прочее', tg_id)

'''
async def get_tgid_from_categoryid(id):
    async with async_session() as session:
        query = select(Category).filter_by(id = id)
        result = await session.execute(query)
        user = result.scalars().all()
        for u in user:
            query2 = select(User).filter_by(id = u.user_id)
            result2 = await session.execute(query2)
            our_tg_id = result2.scalars().all()
            for tg_id in our_tg_id:
                return tg_id.tg_id
            '''

async def add_expension(data: dict):
    category_id = data.get('cat_id')
    date = data.get('date')
    sum = data.get('sum')
    comment = data.get('comment')
    async with async_session() as session:
        new_expence = Expence(category = category_id, date = date, sum = sum, comment=comment)
        session.add(new_expence)
        await session.commit()


async def get_category_name_from_category_id(cat_id):
    async with async_session() as session:
        query = select(Category).filter_by(id = cat_id)
        result = await session.execute(query)
        name = result.scalars().all()
        for n in name:
            return n.name
        

async def get_list_of_expenses_from_category_id(cat_id):
    async with async_session() as session:
        query = select(Expence).filter_by(category = cat_id)
        result = await session.execute(query)
        exp = result.scalars().all()
        exp_list = []
        for e in exp:
            exp_list.append(e)
        return exp_list
        

async def get_list_of_all_expenses(tg_id):
    exp_list = []
    cat_list = await get_categories(tg_id)
    for c in cat_list:
        e = await get_list_of_expenses_from_category_id(c)
        for elem in e:
            exp_list.append(elem)
    return exp_list