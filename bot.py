import logging
import config
import sqlite3
import dickpick

import datetime
from aiogram import Bot, Dispatcher, executor, types


# bot initialization
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

db = sqlite3.connect('server.db')
cr = db.cursor()


def rating_table(data, paramatres):
    dick_dates = list({date[0]: date[1] for date in data}.items())
    dick_dates.sort(key=lambda i: i[1])
    dicks_rate = list(reversed(dick_dates))
    l_dick_rate = len(dicks_rate)

    if paramatres:
        if l_dick_rate >= 10:
            dicks_rate = dicks_rate[:10]

        text = 'Global rating:'
    else:
        if l_dick_rate >= 20:
            dicks_rate = dicks_rate[:20]

        text = 'Chat rating:'

    return text + ''.join(['\n' + '\t'*10 + f'@{user[0]} = {user[1]} cm,' for user in dicks_rate[:-1]] + [
        '\n' + '\t'*10 + f'@{user[0]} = {user[1]} cm.' for user in [dicks_rate[-1]]])


@dp.message_handler(commands=['play'])
async def start_game(message: types.Message):
    cr.execute(
        f'SELECT * FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
    )
    report_message = None

    if cr.fetchone() is None:
        nextday_date = (datetime.datetime.today() +
                        datetime.timedelta(days=1)).strftime('%d-%m-%Y-%H-%M')

        user_data = [
            message.chat.id,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            0,
            nextday_date
        ]

        cr.execute('INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)', user_data)
        db.commit()

        report_message = f'@{message.from_user.username} join to game!'
    else:
        report_message = f'@{message.from_user.username} is exist in game!'

    await bot.send_message(
        message.chat.id,
        report_message
    )


@dp.message_handler(commands=['dick'])
async def dick_pick(message: types.Message):
    cr.execute(
        f'SELECT * FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
    )

    if cr.fetchone() is not None:
        cr.execute(
            f'SELECT dick, pick_time FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
        )

        dick_n, pick_t = cr.fetchone()
        up_dick = dickpick.dick_grow()
        dick_size = dick_n + up_dick
        nowday_date = datetime.datetime.today()
        table_date = list(map(int, pick_t.split('-')))
        c_table_date = datetime.datetime(
            table_date[2], table_date[1], table_date[0], table_date[3], table_date[4])
        delta_t = c_table_date - nowday_date
        delta_day = datetime.timedelta(hours=6)

        if abs(delta_t) >= delta_day:
            nextday_date = (nowday_date + delta_day).strftime('%d-%m-%Y-%H-%M')

            cr.execute(
                f'UPDATE users SET dick = {dick_size}, pick_time = "{nextday_date}" WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}')
            db.commit()

            await bot.send_message(
                message.chat.id,
                f'@{message.from_user.username} grow up on {up_dick} cm!\n' +
                f'Curently dick is {dick_size} cm.'
            )
        else:
            format_date = str(delta_t)[:8].split(':')
            await bot.send_message(
                message.chat.id,
                f'@{message.from_user.username}, time left to next pick: {format_date[0]}h {format_date[1]}m {format_date[2]}s!\nPlease, try again later.'
            )
    else:
        await bot.send_message(
            message.chat.id,
            f'@{message.from_user.username} is not exist!'
        )


@dp.message_handler(commands=['leave'])
async def delete_user(message: types.Message):
    cr.execute(
        f'SELECT * FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
    )

    if cr.fetchone() is not None:
        cr.execute(
            f'SELECT * FROM users WHERE chat_id = {message.chat.id} AND user_id = "{message.from_user.id}"'
        )
        report_message = None

        if cr.fetchone() is not None:
            cr.execute(
                f'DELETE FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}')
            db.commit()
            report_message = f'@{message.from_user.username}, left game!'
        else:
            report_message = f'@{message.from_user.username}, don`t exist in game!'

        await bot.send_message(
            message.chat.id,
            report_message
        )
    else:
        await bot.send_message(
            message.chat.id,
            f'@{message.from_user.username} is not exist!'
        )


@dp.message_handler(commands=['score'])
async def show_myself_score(message: types.Message):
    cr.execute(
        f'SELECT * FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
    )

    if cr.fetchone() is not None:
        cr.execute(
            f'SELECT username, dick FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
        )

        dates = cr.fetchone()
        table_rate = 'Your rating:\n' + '\t' * \
            10 + f'@{dates[0]} = {dates[1]} cm.'

        await bot.send_message(
            message.chat.id,
            table_rate
        )
    else:
        await bot.send_message(
            message.chat.id,
            f'@{message.from_user.username} is not exist!'
        )


@dp.message_handler(commands=['chat_rating'])
async def show_local_score(message: types.Message):
    cr.execute(
        f'SELECT * FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
    )

    if cr.fetchone() is not None:
        cr.execute(
            f'SELECT username, dick FROM users WHERE chat_id = {message.chat.id}'
        )

        table_rate = rating_table(cr.fetchall(), 0)

        await bot.send_message(
            message.chat.id,
            table_rate
        )
    else:
        await bot.send_message(
            message.chat.id,
            f'@{message.from_user.username} is not exist!'
        )


@dp.message_handler(commands=['global_rating'])
async def show_global_rating(message: types.Message):
    cr.execute(
        f'SELECT * FROM users WHERE chat_id = {message.chat.id} AND user_id = {message.from_user.id}'
    )

    if cr.fetchone() is not None:
        cr.execute('SELECT username, dick FROM users')

        table_rate = rating_table(cr.fetchall(), 1)

        await bot.send_message(
            message.chat.id,
            table_rate
        )
    else:
        await bot.send_message(
            message.chat.id,
            f'@{message.from_user.username} is not exist!'
        )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
