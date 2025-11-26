"""Repository layer package"""

from app.repositories.market_repository import MarketRepository
from app.repositories.oauth_repository import (
    OAuthStateRepository,
    SocialAccountRepository,
)
from app.repositories.portfolio_repository import (
    HoldingRepository,
    PortfolioRepository,
    TransactionRepository,
)
from app.repositories.screening_repository import ScreeningRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.repositories.watchlist_repository import (
    UserActivityRepository,
    UserPreferencesRepository,
    WatchlistRepository,
)

__all__ = [
    "UserRepository",
    "UserSessionRepository",
    "StockRepository",
    "MarketRepository",
    "ScreeningRepository",
    "WatchlistRepository",
    "UserActivityRepository",
    "UserPreferencesRepository",
    "PortfolioRepository",
    "HoldingRepository",
    "TransactionRepository",
    "SocialAccountRepository",
    "OAuthStateRepository",
]
