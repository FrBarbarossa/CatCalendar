from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import datetime
from calendar import monthrange
import DataWorkspace as dw
from CalendarDrawer import fill_calendar


class States(StatesGroup):
    MENU = State()
    DATE_CHOOSE = State()
    DATE_CHOSEN = State()


images = ["img/Angry.jpg",
          "img/Busy.jpg",
          "img/Cinema.jpg",
          "img/Happy.jpg",
          "img/Ill.jpg",
          "img/Playing.jpg",
          "img/Sport.jpg"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def generate_inline_kb(pos: int):
    next = (pos + 1) % len(images)
    prev = (pos - 1) % len(images)
    inline_btn_1 = types.InlineKeyboardButton('Следующий ➡', callback_data=f'choose_next {next}')
    inline_btn_2 = types.InlineKeyboardButton('⬅ Предыдущий', callback_data=f'choose_prev {prev}')
    inline_btn_3 = types.InlineKeyboardButton('Выбрать ✅', callback_data=f'choose {pos}')
    inline_kb = types.InlineKeyboardMarkup(row_width=2).add(inline_btn_2, inline_btn_1, inline_btn_3)
    return inline_kb


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    # print(message)
    await message.reply("Привет!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")


@dp.message_handler(commands=['1'], state=States.MENU)
async def process_command_1(message: types.Message):
    await bot.send_photo(chat_id=message.chat.id, photo=open("img/Angry.jpg", 'rb'), reply_markup=generate_inline_kb(0))
    state = dp.current_state(user=message.from_user.id)


@dp.message_handler(commands=['2'], state='*')
async def process_main_menu(message: types.Message):
    # state = dp.current_state(user=message.from_user.id)
    # state.finish()
    # await state.set_state(States.MENU)
    # print(await state.get_state())
    await States.MENU.set()

    key_cur = types.InlineKeyboardButton('Получить календарь за текущий месяц', callback_data='month_cur')
    key_prev = types.InlineKeyboardButton('Получить календарь за прошлый месяц', callback_data='month_prev')
    key_today = types.InlineKeyboardButton('Выбрать настроение на сегодня', callback_data='today')
    key_other = types.InlineKeyboardButton('Выбрать настроение на другой день', callback_data='other_day')
    inline_kb = types.InlineKeyboardMarkup(row_width=1).add(key_cur, key_prev, key_today, key_other)
    await bot.send_message(chat_id=message.chat.id,
                           reply_markup=inline_kb,
                           text='Меню')


@dp.callback_query_handler(lambda c: c.data.startswith('month_'), state=States.MENU)
async def process_send_month_calendar(callback_query: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=int(callback_query.message.message_id),
                                text='Выполняю запрос...')

    pos = int(callback_query.from_user.id)
    raw_data = dw.get_month_data(user_id=pos)
    prep_data = []
    c_day, target_month, c_year = map(int, reversed(str(datetime.date.today()).split('-')))
    if callback_query.data == 'month_prev': # Доделать на случай перехода через год!
        target_month -= 1

    for i in raw_data:
        d, m, y = map(int, i[0].split('/'))
        if y == c_year:
            if target_month == m:
                prep_data.append((d, m, i[1]))
    prep_data.sort()
    print(prep_data)
    out = fill_calendar(data=prep_data, year=c_year)
    await bot.send_photo(chat_id=callback_query.message.chat.id, photo=out)
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=int(callback_query.message.message_id))
    await process_main_menu(callback_query.message)


@dp.callback_query_handler(lambda c: c.data.startswith('choose_'), state=States.DATE_CHOSEN)
async def process_callback_choose_roller(callback_query: types.CallbackQuery):
    pos = int(callback_query.data.split()[-1])
    await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                 message_id=int(callback_query.message.message_id),
                                 media=types.InputMediaPhoto(open(images[pos], 'rb')),
                                 reply_markup=generate_inline_kb(pos))


@dp.callback_query_handler(lambda c: c.data.startswith("choose"), state=States.DATE_CHOSEN)
async def process_approve_menu(callback_query: types.CallbackQuery):
    pos = int(callback_query.data.split()[-1])
    key_yes = types.InlineKeyboardButton('✅ Подтвердить', callback_data=f'approve {pos}')
    key_no = types.InlineKeyboardButton('❌ Назад', callback_data=f'choose_next {pos}')
    inline_kb = types.InlineKeyboardMarkup(row_width=1).add(key_yes, key_no)
    await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                 message_id=int(callback_query.message.message_id),
                                 media=types.InputMediaPhoto(open(images[pos], 'rb')),
                                 reply_markup=inline_kb)


@dp.callback_query_handler(lambda c: c.data.startswith("approve"), state=States.DATE_CHOSEN)
async def process_approvment(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    current_date = user_data['chosen_day']

    pos = int(callback_query.data.split()[-1])
    dw.insert_data(user_id=int(callback_query.from_user.id), time=current_date, pic=images[pos])
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=int(callback_query.message.message_id))
    await bot.send_photo(chat_id=callback_query.message.chat.id, photo=open(images[pos], 'rb'),
                         caption=f'Такое настроение было у Вас {current_date}')
    await process_main_menu(callback_query.message)


@dp.callback_query_handler(lambda c: c.data == "today", state=States.MENU)
async def process_today(callback_query: types.CallbackQuery, state: FSMContext):
    current_date = '/'.join(reversed(str(datetime.date.today()).split('-')))
    # await state.set_state(States.DATE_CHOSEN)
    await state.update_data(chosen_day=current_date)
    await States.DATE_CHOSEN.set()

    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=int(callback_query.message.message_id))
    await process_command_1(callback_query.message)


@dp.callback_query_handler(lambda c: c.data == "other_day", state=States.MENU)
async def process_other_day(callback_query: types.CallbackQuery, state: FSMContext):
    # await state.set_state(States.DATE_CHOOSE)
    await States.DATE_CHOOSE.set()
    # print(await state.get_state())

    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=int(callback_query.message.message_id))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Введите дату в формате ДД/ММ/ГОД (Прим.:31.08.2021), для которой хотите выбрать эмоцию ')


@dp.message_handler(state=States.DATE_CHOOSE)
async def user_date_checking(message: types.Message, state: FSMContext):
    # print(message.from_user.id)
    # state = dp.current_state(user=message.from_user.id)
    # print(await state.get_state())
    current_date = list(reversed(str(datetime.date.today()).split('-')))

    try:
        day, month, year = map(int, (message.text.split('.')))
        if abs(year - int(current_date[2])) > 1 or abs(year - int(current_date[2])) == 1 and \
                int(current_date[1]) != 1 and month != 12:
            raise Exception
        if month not in range(1, 13) or abs(month - int(current_date[1])) > 1:
            raise Exception
        month_length = monthrange(year, month)[1]
        if day not in range(1, month_length + 1):
            raise Exception
        await state.update_data(chosen_day='/'.join([str(day), str(month), str(year)]))
        # await state.set_state(States.DATE_CHOSEN)
        await States.DATE_CHOSEN.set()
        await process_command_1(message)
    except Exception as ex:
        print(ex)
        await bot.send_message(chat_id=message.chat.id,
                               text='Неверный формат даты.\n Введите дату в формате ДД/ММ/ГОД (Прим.:31.08.2021)')


if __name__ == '__main__':
    executor.start_polling(dp)
