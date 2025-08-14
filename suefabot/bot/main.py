import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import settings
from keyboards import (
    get_main_menu_keyboard,
    get_game_mode_keyboard,
    get_challenge_keyboard,
    get_match_result_keyboard,
    get_shop_keyboard,
    get_back_button,
    get_inline_game_button
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.bot_token)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = (
        "🎮 <b>Добро пожаловать в Suefabot!</b>\n\n"
        "✊✌️✋ Решай споры красиво в игре «Камень, ножницы, бумага»!\n\n"
        "🎯 <b>Что умеет бот:</b>\n"
        "• Быстрые PvP-матчи в чатах\n"
        "• Кастомизация персонажа\n"
        "• Ставки на Telegram Stars\n"
        "• Турниры и рейтинги\n\n"
        "Выберите действие:"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "❓ <b>Помощь по Suefabot</b>\n\n"
        "📱 <b>Команды:</b>\n"
        "/start - Главное меню\n"
        "/play - Начать игру\n"
        "/profile - Ваш профиль\n"
        "/shop - Магазин скинов\n"
        "/rating - Глобальный рейтинг\n"
        "/help - Эта справка\n\n"
        "🎮 <b>Как играть:</b>\n"
        "1. Вызовите бота в чате через @suefabot\n"
        "2. Выберите режим игры\n"
        "3. Сделайте свой выбор: камень, ножницы или бумага\n"
        "4. Дождитесь выбора соперника\n"
        "5. Узнайте результат!\n\n"
        "⭐ <b>Telegram Stars:</b>\n"
        "Используйте Stars для покупки скинов и участия в турнирах!"
    )
    
    await message.answer(help_text, parse_mode="HTML")


@dp.message(Command("play"))
async def cmd_play(message: types.Message):
    """Обработчик команды /play"""
    await message.answer(
        "🎮 <b>Выберите режим игры:</b>",
        reply_markup=get_game_mode_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Обработчик команды /profile"""
    # TODO: Получить данные пользователя из БД
    profile_text = (
        f"👤 <b>Профиль игрока</b>\n\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"📛 Имя: {message.from_user.full_name}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"🎮 Всего игр: 0\n"
        f"✅ Побед: 0\n"
        f"❌ Поражений: 0\n"
        f"🤝 Ничьих: 0\n"
        f"📈 Винрейт: 0%\n\n"
        f"⭐ <b>Баланс Stars:</b> 0\n"
        f"🏆 <b>Лига:</b> Бронза\n"
        f"🥇 <b>Место в рейтинге:</b> -"
    )
    
    await message.answer(
        profile_text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )


@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    """Обработчик команды /shop"""
    await message.answer(
        "🛍 <b>Магазин Suefabot</b>\n\n"
        "Выберите категорию товаров:",
        reply_markup=get_shop_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("rating"))
async def cmd_rating(message: types.Message):
    """Обработчик команды /rating"""
    # TODO: Получить топ игроков из БД
    rating_text = (
        "🏆 <b>Топ-10 игроков</b>\n\n"
        "🥇 1. Player1 - 1000 побед\n"
        "🥈 2. Player2 - 950 побед\n"
        "🥉 3. Player3 - 900 побед\n"
        "4. Player4 - 850 побед\n"
        "5. Player5 - 800 побед\n"
        "6. Player6 - 750 побед\n"
        "7. Player7 - 700 побед\n"
        "8. Player8 - 650 побед\n"
        "9. Player9 - 600 побед\n"
        "10. Player10 - 550 побед\n\n"
        "📊 Ваше место: -"
    )
    
    await message.answer(
        rating_text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    welcome_text = (
        "🎮 <b>Главное меню Suefabot</b>\n\n"
        "Выберите действие:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "profile")
async def callback_profile(callback: types.CallbackQuery):
    """Показать профиль"""
    await cmd_profile(callback.message)
    await callback.answer()


@dp.callback_query(F.data == "shop")
async def callback_shop(callback: types.CallbackQuery):
    """Открыть магазин"""
    await callback.message.edit_text(
        "🛍 <b>Магазин Suefabot</b>\n\n"
        "Выберите категорию товаров:",
        reply_markup=get_shop_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "rating")
async def callback_rating(callback: types.CallbackQuery):
    """Показать рейтинг"""
    await cmd_rating(callback.message)
    await callback.answer()


@dp.callback_query(F.data == "stats")
async def callback_stats(callback: types.CallbackQuery):
    """Показать статистику"""
    stats_text = (
        "📊 <b>Статистика Suefabot</b>\n\n"
        "👥 Всего игроков: 0\n"
        "🎮 Игр сегодня: 0\n"
        "💰 Оборот Stars: 0\n"
        "🏆 Активных турниров: 0"
    )
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query(F.data == "help")
async def callback_help(callback: types.CallbackQuery):
    """Показать помощь"""
    await cmd_help(callback.message)
    await callback.answer()


@dp.callback_query(F.data == "back")
async def callback_back(callback: types.CallbackQuery):
    """Кнопка назад"""
    await callback_main_menu(callback)


@dp.callback_query(F.data.startswith("shop_"))
async def callback_shop_category(callback: types.CallbackQuery):
    """Обработчик категорий магазина"""
    category = callback.data.split("_")[1]
    
    category_names = {
        "hands": "✋ Руки",
        "sleeves": "👕 Рукава",
        "accessories": "💍 Аксессуары",
        "items": "🎨 Предметы",
        "arenas": "🏟 Арены",
        "chests": "🎁 Сундуки"
    }
    
    await callback.message.edit_text(
        f"{category_names.get(category, 'Товары')}\n\n"
        "🚧 <i>Раздел в разработке</i>",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@dp.inline_query()
async def inline_query_handler(query: InlineQuery):
    """Обработчик inline-запросов"""
    results = []
    
    # Результат для вызова на игру
    challenge_result = InlineQueryResultArticle(
        id="challenge",
        title="🎮 Вызвать на матч",
        description="Бросьте вызов в «Камень, ножницы, бумага»!",
        input_message_content=InputTextMessageContent(
            message_text=(
                f"⚔️ <b>{query.from_user.full_name} вызывает вас на матч!</b>\n\n"
                "Готовы решить спор в честном бою?"
            ),
            parse_mode="HTML"
        ),
        reply_markup=get_challenge_keyboard("temp_match_id"),
        thumb_url="https://via.placeholder.com/100x100.png?text=⚔️"
    )
    results.append(challenge_result)
    
    # Результат для приглашения в игру
    invite_result = InlineQueryResultArticle(
        id="invite",
        title="📢 Пригласить в Suefabot",
        description="Поделитесь ботом с друзьями",
        input_message_content=InputTextMessageContent(
            message_text=(
                "🎮 <b>Suefabot - Решай споры красиво!</b>\n\n"
                "✊✌️✋ Играй в «Камень, ножницы, бумага» прямо в Telegram!\n\n"
                "• Кастомизация персонажа\n"
                "• Ставки на Telegram Stars\n"
                "• Турниры и рейтинги\n\n"
                "Начни играть: @suefabot"
            ),
            parse_mode="HTML"
        ),
        reply_markup=get_inline_game_button(),
        thumb_url="https://via.placeholder.com/100x100.png?text=🎮"
    )
    results.append(invite_result)
    
    await query.answer(results, cache_time=300)


async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота"""
    logger.info("Bot is starting...")
    
    # Установка webhook в production
    if settings.environment == "production" and settings.webhook_host:
        webhook_url = f"{settings.webhook_host}{settings.webhook_path}"
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    
    # Получение информации о боте
    bot_info = await bot.get_me()
    logger.info(f"Bot @{bot_info.username} started!")


async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке бота"""
    logger.info("Bot is shutting down...")
    
    # Удаление webhook
    if settings.environment == "production":
        await bot.delete_webhook()
    
    await bot.session.close()


def main():
    """Главная функция запуска бота"""
    if settings.environment == "production" and settings.webhook_host:
        # Webhook mode для production
        app = web.Application()
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=settings.webhook_path)
        setup_application(app, dp, bot=bot)
        
        web.run_app(app, host="0.0.0.0", port=settings.webhook_port)
    else:
        # Polling mode для разработки
        asyncio.run(start_polling())


async def start_polling():
    """Запуск бота в режиме polling"""
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    main()