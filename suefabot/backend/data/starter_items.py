# Стартовые предметы для новых игроков

STARTER_SKINS = [
    # Скины для камня
    {
        'name': 'Золотой кулак',
        'description': 'Блестящий золотой кулак, символ богатства',
        'category': 'hands',
        'type': 'rock',
        'price_stars': 50,
        'rarity': 'rare',
        'image_url': '/skins/gold_fist.png',
        'properties': {
            'skin_id': 'gold',
            'effect': 'shimmer',
            'emoji': '✊',
            'color': 'gold'
        }
    },
    {
        'name': 'Огненный камень',
        'description': 'Пылающий камень из недр вулкана',
        'category': 'items',
        'type': 'rock',
        'price_stars': 100,
        'rarity': 'rare',
        'image_url': '/skins/fire_rock.png',
        'properties': {
            'skin_id': 'fire',
            'effect': 'glow-rare',
            'emoji': '🔥',
            'color': 'red-orange'
        }
    },
    {
        'name': 'Ледяной кристалл',
        'description': 'Замороженный кристалл вечной мерзлоты',
        'category': 'items',
        'type': 'rock',
        'price_stars': 100,
        'rarity': 'rare',
        'image_url': '/skins/ice_crystal.png',
        'properties': {
            'skin_id': 'ice',
            'effect': 'glow-rare',
            'emoji': '🧊',
            'color': 'cyan-blue'
        }
    },
    
    # Скины для ножниц
    {
        'name': 'Лазерные ножницы',
        'description': 'Высокотехнологичные ножницы с лазерным лезвием',
        'category': 'items',
        'type': 'scissors',
        'price_stars': 150,
        'rarity': 'epic',
        'image_url': '/skins/laser_scissors.png',
        'properties': {
            'skin_id': 'laser',
            'effect': 'glow-epic',
            'emoji': '⚡',
            'color': 'purple-pink'
        }
    },
    {
        'name': 'Клинок теней',
        'description': 'Древний клинок, окутанный тенью',
        'category': 'items',
        'type': 'scissors',
        'price_stars': 100,
        'rarity': 'rare',
        'image_url': '/skins/shadow_blade.png',
        'properties': {
            'skin_id': 'blade',
            'effect': 'glow-rare',
            'emoji': '🗡️',
            'color': 'gray-black'
        }
    },
    
    # Скины для бумаги
    {
        'name': 'Магический свиток',
        'description': 'Древний свиток с загадочными рунами',
        'category': 'items',
        'type': 'paper',
        'price_stars': 150,
        'rarity': 'epic',
        'image_url': '/skins/magic_scroll.png',
        'properties': {
            'skin_id': 'magic',
            'effect': 'glow-epic',
            'emoji': '📜',
            'color': 'purple-indigo'
        }
    },
    {
        'name': 'Щит защитника',
        'description': 'Непробиваемый щит древних воинов',
        'category': 'items',
        'type': 'paper',
        'price_stars': 100,
        'rarity': 'rare',
        'image_url': '/skins/shield.png',
        'properties': {
            'skin_id': 'shield',
            'effect': 'glow-rare',
            'emoji': '🛡️',
            'color': 'blue-gray'
        }
    },
    
    # Универсальные скины рук
    {
        'name': 'Золотые руки',
        'description': 'Руки Мидаса - всё превращается в золото',
        'category': 'hands',
        'type': None,
        'price_stars': 200,
        'rarity': 'epic',
        'image_url': '/skins/gold_hands.png',
        'properties': {
            'skin_id': 'gold_hands',
            'effect': 'shimmer',
            'applies_to': ['rock', 'scissors', 'paper']
        }
    },
    
    # Арены
    {
        'name': 'Киберпанк арена',
        'description': 'Неоновые огни ночного города',
        'category': 'arenas',
        'type': None,
        'price_stars': 300,
        'rarity': 'epic',
        'image_url': '/arenas/cyberpunk.png',
        'properties': {
            'background': 'cyberpunk',
            'effects': ['neon_lights', 'rain'],
            'music': 'cyberpunk_theme'
        }
    },
    {
        'name': 'Вулканическая арена',
        'description': 'Битва на краю действующего вулкана',
        'category': 'arenas',
        'type': None,
        'price_stars': 250,
        'rarity': 'rare',
        'image_url': '/arenas/volcano.png',
        'properties': {
            'background': 'volcano',
            'effects': ['lava_particles', 'smoke'],
            'music': 'epic_battle'
        }
    }
]

# Предметы для стартового лутбокса
STARTER_LOOTBOX_ITEMS = [
    # Гарантированный редкий предмет (один из трех)
    {
        'guaranteed': True,
        'items': [
            'Огненный камень',
            'Клинок теней', 
            'Щит защитника'
        ]
    },
    # Дополнительные обычные предметы
    {
        'guaranteed': False,
        'chance': 0.5,
        'items': [
            'Золотой кулак',
            'Ледяной кристалл'
        ]
    }
]

# Конфигурация лутбоксов
LOOTBOX_CONFIG = {
    'starter': {
        'name': 'Стартовый подарок',
        'description': 'Добро пожаловать в Suefabot! Откройте свой первый сундук',
        'price_stars': 0,
        'items_count': 2,
        'guaranteed_rarity': 'rare',
        'drop_rates': {
            'common': 0,
            'rare': 0.8,
            'epic': 0.2,
            'legendary': 0
        }
    },
    'common': {
        'name': 'Обычный сундук',
        'description': 'Содержит 1 случайный предмет',
        'price_stars': 10,
        'items_count': 1,
        'drop_rates': {
            'common': 0.7,
            'rare': 0.25,
            'epic': 0.05,
            'legendary': 0
        }
    },
    'rare': {
        'name': 'Редкий сундук',
        'description': 'Содержит 3 предмета с повышенным шансом редких',
        'price_stars': 50,
        'items_count': 3,
        'guaranteed_rarity': 'rare',
        'drop_rates': {
            'common': 0.4,
            'rare': 0.45,
            'epic': 0.14,
            'legendary': 0.01
        }
    },
    'epic': {
        'name': 'Эпический сундук',
        'description': 'Содержит 5 предметов, гарантирован эпический',
        'price_stars': 200,
        'items_count': 5,
        'guaranteed_rarity': 'epic',
        'drop_rates': {
            'common': 0.2,
            'rare': 0.5,
            'epic': 0.27,
            'legendary': 0.03
        }
    }
}