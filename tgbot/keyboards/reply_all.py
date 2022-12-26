# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup

from tgbot.data.config import get_admins


# Кнопки главного меню
def menu_frep(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🎁 Каталог", "👤 Профиль", "📜 Прайс")
    keyboard.row("☎ Поддержка", "ℹ FAQ" )

    if user_id in get_admins():
        keyboard.row("🎁 Управление товарами", "📊 Статистика")
        keyboard.row("⚙ Настройки", "🔆 Общие функции")

    return keyboard

# Кнопки общих функций
def functions_frep(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👤 Поиск профиля 🔍", "📢 Рассылка", "🧾 Поиск заказа 🔍")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Кнопки настроек
def settings_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🖍 Изменить данные", "🕹 Выключатели")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Кнопки изменения товаров
def items_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📁 Создать позицию ➕", "📁 Изменить позицию 🖍", "📁 Удалить все позиции ❌")
    keyboard.row("🗃 Создать категорию ➕", "🗃 Изменить категорию 🖍", "🗃 Удалить все категории ❌")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Завершение загрузки товаров
finish_load_rep = ReplyKeyboardMarkup(resize_keyboard=True)
finish_load_rep.row("📥 Закончить загрузку товаров")
