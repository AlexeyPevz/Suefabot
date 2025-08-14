from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    WebAppInfo
)
from config import settings


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎮 Играть",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/play")
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 Профиль",
                callback_data="profile"
            ),
            InlineKeyboardButton(
                text="🛍 Магазин",
                callback_data="shop"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏆 Рейтинг",
                callback_data="rating"
            ),
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="❓ Помощь",
                callback_data="help"
            )
        ]
    ])
    return keyboard


def get_game_mode_keyboard() -> InlineKeyboardMarkup:
    """Выбор режима игры"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎲 Обычный матч",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/play/casual")
            )
        ],
        [
            InlineKeyboardButton(
                text="🤝 Матч на спор",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/play/bet")
            )
        ],
        [
            InlineKeyboardButton(
                text="⭐ PvP на Stars",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/play/stars")
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard


def get_challenge_keyboard(match_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для принятия вызова"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Принять вызов",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/match/{match_id}")
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"decline_{match_id}"
            )
        ]
    ])
    return keyboard


def get_match_result_keyboard(match_id: str) -> InlineKeyboardMarkup:
    """Клавиатура после матча"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔁 Реванш",
                callback_data=f"rematch_{match_id}"
            ),
            InlineKeyboardButton(
                text="📤 Поделиться",
                switch_inline_query=f"match_{match_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎮 Новая игра",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/play")
            )
        ]
    ])
    return keyboard


def get_shop_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура магазина"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✋ Руки",
                callback_data="shop_hands"
            ),
            InlineKeyboardButton(
                text="👕 Рукава",
                callback_data="shop_sleeves"
            )
        ],
        [
            InlineKeyboardButton(
                text="💍 Аксессуары",
                callback_data="shop_accessories"
            ),
            InlineKeyboardButton(
                text="🎨 Предметы",
                callback_data="shop_items"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏟 Арены",
                callback_data="shop_arenas"
            ),
            InlineKeyboardButton(
                text="🎁 Сундуки",
                callback_data="shop_chests"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="main_menu"
            )
        ]
    ])
    return keyboard


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка 'Назад'"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back"
            )
        ]
    ])
    return keyboard


def get_inline_game_button() -> InlineKeyboardMarkup:
    """Кнопка для inline режима"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎮 Играть в Suefabot",
                web_app=WebAppInfo(url=settings.webapp_url)
            )
        ]
    ])
    return keyboard