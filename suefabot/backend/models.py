from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserStatus(enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"
    INACTIVE = "inactive"


class MatchStatus(enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ItemRarity(enum.Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100))
    full_name = Column(String(200))
    
    # Game stats
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    
    # Economy
    stars_balance = Column(Integer, default=0)
    free_games_used = Column(Integer, default=0)
    free_games_reset_date = Column(DateTime)
    
    # Status
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    matches_as_player1 = relationship("Match", foreign_keys="Match.player1_id", back_populates="player1")
    matches_as_player2 = relationship("Match", foreign_keys="Match.player2_id", back_populates="player2")
    inventory = relationship("UserItem", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    
    @property
    def win_rate(self):
        if self.total_games == 0:
            return 0
        return (self.wins / self.total_games) * 100


class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(String(50), primary_key=True)  # UUID
    player1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    player2_id = Column(Integer, ForeignKey('users.id'))
    
    # Game data
    player1_choice = Column(String(20))
    player2_choice = Column(String(20))
    promise = Column(String(200))
    
    # Stakes
    stake_amount = Column(Integer, default=0)
    stake_item_id = Column(Integer, ForeignKey('items.id'))
    
    # Status
    status = Column(Enum(MatchStatus), default=MatchStatus.WAITING)
    winner_id = Column(Integer, ForeignKey('users.id'))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="matches_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="matches_as_player2")
    winner = relationship("User", foreign_keys=[winner_id])
    stake_item = relationship("Item")


class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category = Column(String(50))  # hands, sleeves, accessories, items, arenas
    type = Column(String(50))  # rock, scissors, paper (for items)
    
    # Economy
    price_stars = Column(Integer, default=0)
    rarity = Column(Enum(ItemRarity), default=ItemRarity.COMMON)
    
    # Visual
    image_url = Column(String(500))
    animation_url = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_seasonal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_items = relationship("UserItem", back_populates="item")


class UserItem(Base):
    __tablename__ = 'user_items'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    
    # Item data
    quantity = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)
    obtained_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="inventory")
    item = relationship("Item", back_populates="user_items")


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Transaction data
    type = Column(String(50))  # purchase, match_win, match_loss, chest_open
    amount = Column(Integer)
    stars_before = Column(Integer)
    stars_after = Column(Integer)
    
    # Additional data
    item_id = Column(Integer, ForeignKey('items.id'))
    match_id = Column(String(50), ForeignKey('matches.id'))
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    item = relationship("Item")
    match = relationship("Match")


class Chest(Base):
    __tablename__ = 'chests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    # Economy
    price_stars = Column(Integer, nullable=False)
    
    # Loot configuration
    items_count = Column(Integer, default=1)
    drop_rates = Column(JSON)  # {"common": 0.7, "rare": 0.2, "epic": 0.08, "legendary": 0.02}
    
    # Visual
    image_url = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_seasonal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)