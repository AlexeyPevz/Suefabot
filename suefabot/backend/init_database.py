"""
Скрипт для инициализации базы данных с начальными данными
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import Base, Item, ItemRarity, Chest
from data.starter_items import STARTER_SKINS, LOOTBOX_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Инициализация базы данных"""
    # Создаем движок
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    # Создаем таблицы
    Base.metadata.create_all(engine)
    
    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Добавляем базовые предметы
        add_starter_items(session)
        
        # Добавляем лутбоксы
        add_lootboxes(session)
        
        session.commit()
        logger.info("Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        session.rollback()
    finally:
        session.close()


def add_starter_items(session):
    """Добавляет стартовые предметы"""
    logger.info("Adding starter items...")
    
    for item_data in STARTER_SKINS:
        # Проверяем, существует ли предмет
        existing = session.query(Item).filter_by(name=item_data['name']).first()
        if existing:
            logger.info(f"Item '{item_data['name']}' already exists, skipping...")
            continue
        
        # Создаем предмет
        item = Item(
            name=item_data['name'],
            description=item_data['description'],
            category=item_data['category'],
            type=item_data['type'],
            price_stars=item_data['price_stars'],
            rarity=ItemRarity[item_data['rarity'].upper()],
            image_url=item_data['image_url'],
            properties=item_data['properties']
        )
        
        session.add(item)
        logger.info(f"Added item: {item.name}")


def add_lootboxes(session):
    """Добавляет лутбоксы"""
    logger.info("Adding lootboxes...")
    
    for chest_type, config in LOOTBOX_CONFIG.items():
        # Проверяем, существует ли сундук
        existing = session.query(Chest).filter_by(name=config['name']).first()
        if existing:
            logger.info(f"Chest '{config['name']}' already exists, skipping...")
            continue
        
        # Создаем сундук
        chest = Chest(
            name=config['name'],
            description=config['description'],
            price_stars=config['price_stars'],
            items_count=config['items_count'],
            drop_rates=config['drop_rates']
        )
        
        # Специальные свойства для стартового сундука
        if chest_type == 'starter':
            chest.is_starter = True
            chest.price_stars = 0  # Бесплатный
        
        session.add(chest)
        logger.info(f"Added chest: {chest.name}")


if __name__ == "__main__":
    init_database()