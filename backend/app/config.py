from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "fund_tracker"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Scheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_HOUR: int = 0
    SCHEDULER_MINUTE: int = 0

    # Tushare Pro
    TUSHARE_TOKEN: str = "" # 从 .env 文件中读取
    TUSHARE_TIMEOUT: int = 10

    # Efinance API Configuration
    EFINANCE_TIMEOUT: int = 15
    EFINANCE_MAX_RETRIES: int = 3
    EFINANCE_RETRY_BACKOFF: float = 1.0

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_DECODE_RESPONSES: bool = True
    STOCK_NAME_CACHE_TTL: int = 86400  # 24 hours (stock names don't change often)

    # Stock Realtime Quote Cache TTL
    STOCK_REALTIME_CACHE_TTL_TRADING: int = 30  # 30秒（交易时间）
    STOCK_REALTIME_CACHE_TTL_NON_TRADING: int = 3600  # 1小时（非交易时间）
    STOCK_REALTIME_CACHE_NULL_TTL: int = 60  # 1分钟（空值缓存）

    # Fund Data Cache TTL
    FUND_INFO_CACHE_TTL: int = 86400  # 24小时（基金信息）
    FUND_LATEST_NAV_CACHE_TTL: int = 1800  # 30分钟（最新净值）
    FUND_HISTORY_NAV_CACHE_TTL: int = 86400  # 24小时（历史净值）
    FUND_DATA_NULL_CACHE_TTL: int = 300  # 5分钟（空值缓存）

    # Fund Stock Positions Cache TTL
    FUND_POSITIONS_CACHE_TTL_WITH_DATE: int = 604800  # 7天（有报告期）
    FUND_POSITIONS_CACHE_TTL_LATEST: int = 86400  # 24小时（无报告期）
    FUND_POSITIONS_NULL_CACHE_TTL: int = 300  # 5分钟（空值缓存）

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略 .env 中的额外字段

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
