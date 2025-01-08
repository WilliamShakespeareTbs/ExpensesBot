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


async def delete_expence_by_exp_class(exp):
    async with async_session() as session:
        await session.delete(exp)
        await session.commit()


async def get_cat_id_from_cat_name(tg_id, cat_name):
    async with async_session() as session:
        query = select(User).filter_by(tg_id = tg_id)
        result = await session.execute(query)
        user = result.scalar_one()
        query_2 = select(Category).filter_by(user_id = user.id)
        result_2 = await session.execute(query_2)
        cats = result_2.scalars().all()
        for c in cats:
            if c.name == cat_name:
                return c.id
            

async def transfer_expense_to_another_cat(old_cat_id, new_cat_id):
    async with async_session() as session:
        query = select(Expence).filter_by(category = old_cat_id)
        result = await session.execute(query)
        exp_s = result.scalars().all()
        for e in exp_s:
            e.category = new_cat_id
        await session.commit()


async def delete_category(cat_id):
    async with async_session() as session:
        query = select(Category).filter_by(id = cat_id)
        result = await session.execute(query)
        cat_to_delete = result.scalar_one()
        await session.delete(cat_to_delete)
        await session.commit()


async def change_cat_name(cat_id, new_cat_name):
    async with async_session() as session:
        query = select(Category).filter_by(id = cat_id)
        result = await session.execute(query)
        cat = result.scalar_one()
        cat.name = new_cat_name
        await session.commit()


async def change_exp_prop(exp_to_edit, prop_name, new_prop):
    async with async_session() as session:
        query = select(Expence).filter_by(id = exp_to_edit.id)
        result = await session.execute(query)
        exp = result.scalar_one()
        if prop_name == 'date':
            exp.date = new_prop
        if prop_name == 'sum':
            exp.sum = new_prop
        if prop_name == 'comment':
            exp.comment = new_prop
        await session.commit()