import aiohttp
import logging
from typing import Dict, Optional
from config import settings

logger = logging.getLogger(__name__)


class APIClient:
    """Клиент для взаимодействия с backend API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.api_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_match(
        self, 
        telegram_id: str,
        username: str,
        full_name: str,
        promise: str = "",
        stake_amount: int = 0
    ) -> Dict:
        """
        Создать новый матч
        
        Returns:
            Данные созданного матча
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Сначала аутентифицируемся
            # В production нужно использовать реальную initData
            headers = {
                'X-Telegram-Init-Data': f'mock_data_for_{telegram_id}',
                'X-Dev-User-Id': telegram_id,
                'X-Dev-Username': username or ''
            }
            
            data = {
                'telegram_id': telegram_id,
                'username': username,
                'full_name': full_name,
                'promise': promise,
                'stake_amount': stake_amount
            }
            
            async with self.session.post(
                f"{self.base_url}/api/match/create",
                json=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.text()
                    logger.error(f"Failed to create match: {response.status} - {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating match: {e}")
            return None
    
    async def get_match_status(self, match_id: str) -> Optional[Dict]:
        """
        Получить статус матча
        
        Args:
            match_id: ID матча
            
        Returns:
            Статус матча или None
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/match/{match_id}/status"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting match status: {e}")
            return None
    
    async def get_user_profile(self, telegram_id: str) -> Optional[Dict]:
        """
        Получить профиль пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Профиль пользователя или None
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/user/{telegram_id}"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None


# Глобальный экземпляр клиента
api_client = APIClient()