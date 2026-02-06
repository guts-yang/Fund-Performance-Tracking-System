"""
Efinance client wrapper with retry logic and timeout handling

包装 efinance 库的所有 API 调用，添加自动重试和错误处理机制。
"""
import logging
from typing import Optional
import pandas as pd
import efinance as ef
from ..config import get_settings
from ..utils.retry_helper import retry_with_backoff, APICallError

logger = logging.getLogger(__name__)
settings = get_settings()


class EfinanceClient:
    """
    Wrapper around efinance library with retry logic and timeout handling

    Note: efinance doesn't expose timeout configuration in its API.
    This wrapper provides retry logic and error classification.
    For actual timeout control, we rely on retry mechanism and fast failure.

    Configuration:
        - EFINANCE_TIMEOUT: Connection/read timeout in seconds
        - EFINANCE_MAX_RETRIES: Maximum number of retry attempts
        - EFINANCE_RETRY_BACKOFF: Base backoff time for exponential backoff
    """

    def __init__(self):
        """Initialize EfinanceClient with settings from config"""
        self._timeout = settings.EFINANCE_TIMEOUT
        self._max_retries = settings.EFINANCE_MAX_RETRIES
        self._backoff_base = settings.EFINANCE_RETRY_BACKOFF

        logger.info(
            f"[EfinanceClient] Initialized with timeout={self._timeout}s, "
            f"max_retries={self._max_retries}, backoff_base={self._backoff_base}s"
        )

    @retry_with_backoff(
        max_retries=3,
        backoff_base=1.0,
        retry_on_timeout=True,
        retry_on_connection_error=True
    )
    def get_base_info(self, fund_code: str) -> Optional[pd.Series]:
        """
        获取基金基本信息 (with retry)

        Args:
            fund_code: 基金代码

        Returns:
            基金信息 Series 或 None

        Raises:
            APICallError: 当所有重试都失败时
        """
        logger.debug(f"[EfinanceClient] Calling get_base_info for {fund_code}")
        return ef.fund.get_base_info(fund_code)

    @retry_with_backoff(
        max_retries=3,
        backoff_base=1.0,
        retry_on_timeout=True,
        retry_on_connection_error=True
    )
    def get_quote_history(
        self,
        fund_code: str,
        pz: int = None
    ) -> Optional[pd.DataFrame]:
        """
        获取基金历史净值 (with retry)

        Args:
            fund_code: 基金代码
            pz: 返回条数

        Returns:
            历史净值 DataFrame 或 None

        Raises:
            APICallError: 当所有重试都失败时
        """
        logger.debug(f"[EfinanceClient] Calling get_quote_history for {fund_code}, pz={pz}")
        if pz:
            return ef.fund.get_quote_history(fund_code, pz=pz)
        return ef.fund.get_quote_history(fund_code)

    @retry_with_backoff(
        max_retries=3,
        backoff_base=1.0,
        retry_on_timeout=True,
        retry_on_connection_error=True
    )
    def get_realtime_increase_rate(self, fund_codes) -> Optional[pd.DataFrame]:
        """
        获取基金实时估算涨跌幅 (with retry)

        Args:
            fund_codes: 基金代码或代码列表

        Returns:
            实时涨跌幅 DataFrame 或 None

        Raises:
            APICallError: 当所有重试都失败时
        """
        logger.debug(f"[EfinanceClient] Calling get_realtime_increase_rate for {fund_codes}")
        return ef.fund.get_realtime_increase_rate(fund_codes)

    @retry_with_backoff(
        max_retries=3,
        backoff_base=1.0,
        retry_on_timeout=True,
        retry_on_connection_error=True
    )
    def get_fund_codes(self) -> Optional[pd.DataFrame]:
        """
        获取所有基金代码列表 (with retry)

        Returns:
            基金代码列表 DataFrame 或 None

        Raises:
            APICallError: 当所有重试都失败时
        """
        logger.debug("[EfinanceClient] Calling get_fund_codes")
        return ef.fund.get_fund_codes()

    @retry_with_backoff(
        max_retries=3,
        backoff_base=1.0,
        retry_on_timeout=True,
        retry_on_connection_error=True
    )
    def get_realtime_quotes(self, market_type: str = None) -> Optional[pd.DataFrame]:
        """
        获取股票/ETF/LOF 实时行情 (with retry)

        Args:
            market_type: 市场类型 ('ETF', 'LOF' 等)

        Returns:
            实时行情 DataFrame 或 None

        Raises:
            APICallError: 当所有重试都失败时
        """
        logger.debug(f"[EfinanceClient] Calling get_realtime_quotes for {market_type}")
        return ef.stock.get_realtime_quotes(market_type)


# Global singleton instance
efinance_client = EfinanceClient()
