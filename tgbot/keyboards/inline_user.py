# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💰 Заказать товар", callback_data=f"buy_item_open:{position_id}:{remover}") #Изменил купить на заказать
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard
