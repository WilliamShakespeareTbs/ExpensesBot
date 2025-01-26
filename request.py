from models import Base, User, Category, Expense, async_session
from sqlalchemy import select, insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import aliased
from models import User


async def add_category(category_name, tg_id):
    async with async_session() as session:
        query = select(User).filter_by(tg_id = tg_id)
        result = await session.execute(query)
        user = result.scalar_one()
        new_category = Category(name = category_name, user_id = user.id, sum = 0)
        session.add(new_category)
        await session.commit()


async def get_categories(tg_id):
    async with async_session() as session:
        query = select(Category).join(User, Category.user_id == User.id).filter(User.tg_id == tg_id)
        result = await session.execute(query)
        cat_seq = result.scalars().all()
        dict_sorted_by_name = dict()
        for i in cat_seq:
            dict_sorted_by_name.update({i.id : i.name})
        return dict_sorted_by_name


async def check_for_user(tg_id):
    async with async_session() as session:
        query = select(User).filter_by(tg_id = tg_id)
        result = await session.execute(query)
        try:
            result.scalar_one()
            return True
        except NoResultFound:
            return False


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
        new_expense = Expense(category = category_id, date = date, sum = sum, comment=comment)
        session.add(new_expense)
        await session.commit()


async def get_category_name_from_category_id(cat_id):
    async with async_session() as session:
        query = select(Category).filter_by(id = cat_id)
        result = await session.execute(query)
        name = result.scalar_one()
        return name.name
        

async def get_list_of_expenses_from_category_id(cat_id):
    async with async_session() as session:
        query = select(Expense).filter_by(category = cat_id).order_by(Expense.date)
        result = await session.execute(query)
        exp = result.scalars().all()
        return exp
        

async def get_list_of_all_expenses_in_one_query(tg_id):
    async with async_session() as session:
        u = aliased(User)
        c = aliased(Category)
        e = aliased(Expense)
        query = select(e).join(c, e.category == c.id).join(u, c.user_id == u.id).filter(u.tg_id == tg_id).order_by(e.date)
        result = await session.execute(query)
        exps = result.scalars().all()
        return exps


async def delete_expence_by_exp_class(exp):
    async with async_session() as session:
        await session.delete(exp)
        await session.commit()


async def get_cat_id_from_cat_name(tg_id, cat_name):
    async with async_session() as session:
        query = select(Category).join(User, Category.user_id == User.id).filter(User.tg_id == tg_id)
        result = await session.execute(query)
        cats = result.scalars().all()
        for c in cats:
            if c.name == cat_name:
                return c.id
            

async def transfer_expense_to_another_cat(exp_to_edit, new_cat_id):
    async with async_session() as session:
        query = select(Expense).filter_by(id = exp_to_edit.id)
        result = await session.execute(query)
        exp = result.scalar_one()
        exp.category = new_cat_id
        await session.commit()


async def transger_all_expenses_to_other_cat(cat_id, other_cat_id):
    async with async_session() as session:
        query = select(Expense).filter_by(category = cat_id)
        result = await session.execute(query)
        exps = result.scalars().all()
        for exp in exps:
            exp.category = other_cat_id
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
        query = select(Expense).filter_by(id = exp_to_edit.id)
        result = await session.execute(query)
        exp = result.scalar_one()
        if prop_name == 'date':
            exp.date = new_prop
        if prop_name == 'sum':
            exp.sum = new_prop
        if prop_name == 'comment':
            exp.comment = new_prop
        await session.commit()