"""
Redis client wrapper with connection pooling and error handling

提供 Redis 连接管理和缓存操作工具
"""
import logging
import redis
from typing import Optional, Any, List
from ..config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis 客户端封装，提供连接池和基本缓存操作

    Configuration:
        - REDIS_HOST: Redis 服务器地址
        - REDIS_PORT: Redis 端口
        - REDIS_DB: 数据库编号
        - REDIS_PASSWORD: 密码（可选）
        - REDIS_DECODE_RESPONSES: 是否自动解码响应
    """

    def __init__(self):
        """初始化 Redis 客户端连接池"""
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._initialize()

    def _initialize(self):
        """初始化 Redis 连接"""
        try:
            # 创建连接池
            self._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # 创建 Redis 客户端
            self._client = redis.Redis(connection_pool=self._pool)

            # 测试连接
            self._client.ping()

            logger.info(
                f"[RedisClient] 成功连接到 Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            )

        except redis.ConnectionError as e:
            logger.error(f"[RedisClient] Redis 连接失败: {e}")
            logger.warning("[RedisClient] 缓存功能将被禁用")
            self._client = None
        except Exception as e:
            logger.error(f"[RedisClient] Redis 初始化失败: {e}")
            self._client = None

    def is_available(self) -> bool:
        """检查 Redis 是否可用"""
        if self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    def get(self, key: str) -> Optional[str]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在则返回 None
        """
        if not self.is_available():
            return None

        try:
            value = self._client.get(key)
            return value
        except Exception as e:
            logger.error(f"[RedisClient] 获取缓存失败: key={key}, error={e}")
            return None

    def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示永不过期

        Returns:
            是否设置成功
        """
        if not self.is_available():
            return False

        try:
            if ttl:
                self._client.setex(key, ttl, value)
            else:
                self._client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"[RedisClient] 设置缓存失败: key={key}, error={e}")
            return False

    def mget(self, keys: List[str]) -> List[Optional[str]]:
        """
        批量获取缓存值

        Args:
            keys: 缓存键列表

        Returns:
            缓存值列表，顺序与 keys 一致
        """
        if not self.is_available() or not keys:
            return [None] * len(keys)

        try:
            values = self._client.mget(keys)
            return list(values)  # 转换为列表
        except Exception as e:
            logger.error(f"[RedisClient] 批量获取缓存失败: keys={keys}, error={e}")
            return [None] * len(keys)

    def mset(self, mapping: dict[str, str], ttl: Optional[int] = None) -> bool:
        """
        批量设置缓存值

        Args:
            mapping: 键值对字典
            ttl: 过期时间（秒），None 表示永不过期

        Returns:
            是否设置成功
        """
        if not self.is_available() or not mapping:
            return False

        try:
            # 批量设置
            self._client.mset(mapping)

            # 如果需要设置过期时间
            if ttl:
                pipe = self._client.pipeline()
                for key in mapping.keys():
                    pipe.expire(key, ttl)
                pipe.execute()

            return True
        except Exception as e:
            logger.error(f"[RedisClient] 批量设置缓存失败: error={e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        if not self.is_available():
            return False

        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"[RedisClient] 删除缓存失败: key={key}, error={e}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 缓存键

        Returns:
            键是否存在
        """
        if not self.is_available():
            return False

        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"[RedisClient] 检查键存在失败: key={key}, error={e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        批量删除匹配模式的键

        Args:
            pattern: 键模式（如 "stock:*"）

        Returns:
            删除的键数量
        """
        if not self.is_available():
            return 0

        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"[RedisClient] 批量删除失败: pattern={pattern}, error={e}")
            return 0

    def close(self):
        """关闭 Redis 连接"""
        if self._pool:
            self._pool.disconnect()
            logger.info("[RedisClient] Redis 连接已关闭")


# 全局单例实例
redis_client = RedisClient()
