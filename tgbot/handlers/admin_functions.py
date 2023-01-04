# - *- coding: utf- 8 - *-
import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import CantParseEntities


from tgbot.data.loader import dp, bot
from tgbot.keyboards.inline_admin import profile_search_finl, profile_search_return_finl
from tgbot.keyboards.inline_all import mail_confirm_inl
from tgbot.services.api_sqlite import *
from tgbot.utils.const_functions import is_number
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import open_profile_admin
from tgbot.utils.misc_functions import get_position_admin

file_photo_id = []
file_video_id = []

# Рассылка
@dp.message_handler(IsAdmin(), text="📢 Рассылка", state="*")
async def functions_mail(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_mail_text")
    await message.answer("<b>📢 Введите текст для рассылки пользователям</b>\n"
                         "❕ Вы можете использовать HTML разметку")


# Поиск профиля
@dp.message_handler(IsAdmin(), text="👤 Поиск профиля 🔍", state="*")
async def functions_profile(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_profile")
    await message.answer("<b>👤 Введите логин или айди пользователя</b>")


# Поиск чеков
@dp.message_handler(IsAdmin(), text="🧾 Поиск заказа 🔍", state="*")
async def functions_receipt(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_receipt")
    await message.answer("<b>🧾 Введите номер заказа</b>")


######################################## ПРИНЯТИЕ ПОИСКОВЫХ ДАННЫХ ########################################
# Принятие айди или логина для поиска профиля
@dp.message_handler(IsAdmin(), state="here_profile")
@dp.message_handler(IsAdmin(), text_startswith=".user")
async def functions_profile_get(message: Message, state: FSMContext):
    find_user = message.text

    if ".user" in find_user:
        find_user = message.text.split(" ")
        if len(find_user) > 1:
            find_user = find_user[1]
        else:
            await message.answer("<b>❌ Вы не указали логин или айди пользователя.</b>\n"
                                 "👤 Введите логин или айди пользователя.")
            return

    if find_user.isdigit():
        get_user = get_userx(user_id=find_user)
    else:
        if find_user.startswith("@"): find_user = find_user[1:]
        get_user = get_userx(user_login=find_user.lower())

    if get_user is not None:
        await state.finish()
        await message.answer(open_profile_admin(get_user['user_id']),
                             reply_markup=profile_search_finl(get_user['user_id']))
    else:
        await message.answer("<b>❌ Профиль не был найден</b>\n"
                             "👤 Введите логин или айди пользователя.")


# Принятие чека для поиска
@dp.message_handler(IsAdmin(), state="here_receipt")
@dp.message_handler(IsAdmin(), text_startswith=".rec")
async def functions_receipt_get(message: Message, state: FSMContext):
    find_receipt = message.text

    if ".rec" in find_receipt:
        find_receipt = message.text.split(" ")
        if len(find_receipt) > 1:
            find_receipt = find_receipt[1]
        else:
            await message.answer("<b>❌ Вы не указали номер заказа.</b>\n"
                                 "🧾 Введите номер заказа")
            return

    if find_receipt.startswith("#"): find_receipt = find_receipt[1:]


    get_purchase = get_purchasex(purchase_receipt=find_receipt)
    if get_purchase is not None:
        await state.finish()
        await message.answer(
            f"<b>🧾 Номер заказа: <code>#{get_purchase['purchase_receipt']}</code></b>\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"👤 Пользователь: <a href='tg://user?id={get_purchase['user_id']}'>{get_purchase['user_name']}</a> | <code>{get_purchase['user_id']}</code>\n"
            f"🏷 Название товара: <code>{get_purchase['purchase_position_name']}</code>\n"
            f"📦 Заказано товаров: <code>{get_purchase['purchase_count']}шт</code>\n"
            f"💰 Цена одного товара: <code>{get_purchase['purchase_price_one']}₽</code>\n"
            f"💸 Сумма заказа: <code>{get_purchase['purchase_price']}₽</code>\n"
            f"🕰 Дата заказа: <code>{get_purchase['purchase_date']}</code>"
        )
        return
    else:
        await message.answer("<b>❌ Заказ не был найден.</b>\n"
                             "🧾 Введите номер заказа")


######################################## РАССЫЛКА ########################################
# Принятие текста для рассылки
@dp.message_handler(IsAdmin(), state="here_mail_text")
async def functions_mail_get(message: Message, state: FSMContext):
    await state.update_data(here_mail_text=message.text)
    # Очистка глобальных списках перед ведением текста
    if file_photo_id != []:
        del file_photo_id[0]
    if file_video_id != []:
        del file_video_id[0]

    try:
        await state.set_state("here_mail_photo")
        await message.answer("<b>📁 Отправьте изображение 📸 или видео 📹 для рассылки </b>\n"
                             "❕ Отправьте <code>0</code> чтобы пропустить.")
    except CantParseEntities:
        await message.answer("<b>❌ Ошибка синтаксиса HTML.</b>\n"
                             "📢 Введите текст для рассылки пользователям.\n"
                             "❕ Вы можете использовать HTML разметку.")


# Принятие изображения или текста для рассылки
@dp.message_handler(IsAdmin(), content_types="photo", state="here_mail_photo")
@dp.message_handler(IsAdmin(), content_types="text", state="here_mail_photo")
async def mail_photo(message: Message, state: FSMContext):
    get_users = get_all_usersx()
    await state.update_data()

    if "text" in message:
        photo_id = " "
        file_video_id.append('0')
    else:
        photo_id = message.photo[-1].file_id
        file_video_id.append('0')

    file_photo_id.append(photo_id)
    cache_msg = (await state.get_data())['here_mail_text']

    if len(file_photo_id[0]) >= 5:
        await message.answer_photo(photo_id, cache_msg)
    else:
        await message.answer(cache_msg)
    await state.set_state("here_mail_confirm")
    await message.answer(
        f"<b>📢 Отправить <code>{len(get_users)}</code> юзерам сообщение?</b>\n",
        reply_markup=mail_confirm_inl,
        disable_web_page_preview=True
    )

# Принятие видео для рассылки
@dp.message_handler(IsAdmin(), content_types="video", state="here_mail_photo")
async def mail_video(message: Message, state: FSMContext):
    get_users = get_all_usersx()
    await state.update_data()
    video_id = message.video.file_id
    file_video_id.append(video_id)
    cache_msg = (await state.get_data())['here_mail_text']
    await state.set_state("here_mail_confirm")
    await message.answer_video(video_id, caption=cache_msg)
    file_photo_id.append('0')
    await message.answer(
        f"<b>📢 Отправить <code>{len(get_users)}</code> юзерам сообщение?</b>\n",
        reply_markup=mail_confirm_inl,
        disable_web_page_preview=True
    )


# Подтверждение отправки рассылки
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_mail", state="here_mail_confirm")
async def functions_mail_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    async with state.proxy() as data:
        send_message = data['here_mail_text']


    get_users = get_all_usersx()
    await state.finish()

    if get_action == "yes":
        await call.message.edit_text(f"<b>📢 Рассылка началась... (0/{len(get_users)})</b>")
        asyncio.create_task(functions_mail_make(send_message,  call))
    else:
        await call.message.edit_text("<b>📢 Вы отменили отправку рассылки ✅</b>")



# Сама отправка рассылки
async def functions_mail_make(message, call: CallbackQuery):
    receive_users, block_users, how_users = 0, 0, 0
    get_users = get_all_usersx()
    get_time = get_unix()
    photo_id = file_photo_id[0]
    video_id = file_video_id[0]

    for user in get_users:
        try:
            if len(photo_id) >= 5 and  len(video_id) <= 5:
                await bot.send_photo(user['user_id'], photo_id, message)
            elif len(video_id) >= 5 and len(photo_id) <= 5 :
                await bot.send_video(user['user_id'], video_id, caption=message)
            else:
                await bot.send_message(user['user_id'], message)

            receive_users += 1
        except:
            block_users += 1

        how_users += 1

        if how_users % 10 == 0:
            await call.message.edit_text(f"<b>📢 Рассылка началась... ({how_users}/{len(get_users)})</b>")

        await asyncio.sleep(0.08)

    await call.message.edit_text(
        f"<b>📢 Рассылка была завершена за <code>{get_unix() - get_time}сек</code></b>\n"
        f"👤 Всего пользователей: <code>{len(get_users)}</code>\n"
        f"✅ Пользователей получило сообщение: <code>{receive_users}</code>\n"
        f"❌ Пользователей не получило сообщение: <code>{block_users}</code>"
    )




######################################## УПРАВЛЕНИЕ ПРОФИЛЕМ ########################################
# Обновление профиля пользователя
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_refresh", state="*")
async def functions_profile_refresh(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    await state.finish()

    await call.message.delete()
    await call.message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))


# Покупки пользователя
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_purchases", state="*")
async def functions_profile_purchases(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    last_purchases = last_purchasesx(user_id, 10)

    if len(last_purchases) >= 1:
        await call.answer("🎁 Последние 10 покупок")
        await call.message.delete()

        for purchases in last_purchases:
            # link_items = await upload_text(call, purchases['purchase_item'])

            await call.message.answer(f"<b>🧾 Номер заказа: <code>#{purchases['purchase_receipt']}</code></b>\n"
                                      f"🎁 Товар: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}шт | {purchases['purchase_price']}₽</code>\n"
                                      f"🕰 Дата покупки: <code>{purchases['purchase_date']}</code>\n")

        await call.message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))
    else:
        await call.answer("❗ У пользователя отсутствуют покупки", True)


# Подтверждение платежа
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_balance_add", state="*")
async def functions_profile_balance_add(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    await state.update_data(here_profile=user_id)
    await state.set_state("here_profile_add")

    await call.message.edit_text("<b>💰 Введите сумму платежа</b>",
                                 reply_markup=profile_search_return_finl(user_id))


# Изменение баланса пользователю
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_balance_set", state="*")
async def functions_profile_balance_set(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    await state.update_data(here_profile=user_id)
    await state.set_state("here_profile_set")

    await call.message.edit_text("<b>💰 Введите сумму для изменения баланса</b>",
                                 reply_markup=profile_search_return_finl(user_id))


# Принятие суммы для подтверждение платежа
@dp.message_handler(IsAdmin(), state="here_profile_add")
async def functions_profile_balance_add_get(message: Message, state: FSMContext):
    user_id = (await state.get_data())['here_profile']

    if not message.text.isdigit():
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму платежа",
                             reply_markup=profile_search_return_finl(user_id))
        return

    if int(message.text) <= 0 or int(message.text) > 1000000000:
        await message.answer("<b>❌ Сумма выдачи не может быть меньше 1 и больше 1 000 000 000</b>\n"
                             "💰 Введите сумму платежа")
        return

    await state.finish()
    get_user = get_userx(user_id=user_id)
    update_userx(user_id, user_balance=get_user['user_balance'] + int(message.text))

    await message.answer(
        f"<b>✅ Пользователь <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
        f"оплатил заказы на <code>{message.text}₽</code></b>")

    await message.bot.send_message(user_id, f"<b>💰 Оплата <code>{message.text}₽</code> получена.</b>")
    await message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))


# Принятие суммы для изменения баланса пользователя
@dp.message_handler(IsAdmin(), state="here_profile_set")
async def functions_profile_balance_set_get(message: Message, state: FSMContext):
    user_id = (await state.get_data())['here_profile']

    if is_number(message.text):
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для изменения баланса",
                             reply_markup=profile_search_return_finl(user_id))
        return

    if int(message.text) < -1000000000 or int(message.text) > 1000000000:
        await message.answer("<b>❌ Сумма изменения не может быть больше или меньше (-)1 000 000 000</b>\n"
                             "💰 Введите сумму для изменения баланса",
                             reply_markup=profile_search_return_finl(user_id))
        return

    await state.finish()
    get_user = get_userx(user_id=user_id)
    update_userx(user_id, user_balance=message.text)

    await message.answer(
        f"<b>✅ Пользователю <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
        f"изменён баланс на <code>{message.text}₽</code></b>")

    await message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))


# Отправка сообщения пользователю
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_message", state="*")
async def functions_profile_user_message(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    await state.update_data(here_profile=user_id)
    await state.set_state("here_profile_message")

    await call.message.edit_text("<b>💌 Введите сообщение для отправки</b>\n"
                                 "⚠ Сообщение будет сразу отправлено пользователю.",
                                 reply_markup=profile_search_return_finl(user_id))


# Принятие сообщения для пользователя
@dp.message_handler(IsAdmin(), state="here_profile_message")
async def functions_profile_user_message_get(message: Message, state: FSMContext):
    user_id = (await state.get_data())['here_profile']
    await state.finish()

    get_message = "<b>💌 Сообщение от администратора:</b>\n" + clear_html(message.text)
    get_user = get_userx(user_id=user_id)

    await message.bot.send_message(user_id, get_message)
    await message.answer(f"<b>✅ Пользователю <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
                         f"было отправлено сообщение:</b>\n"
                         f"{get_message}")

    await message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))
