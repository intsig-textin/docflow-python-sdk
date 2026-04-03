"""
配置管理
"""
from typing import Optional, List
from ._constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_FACTOR,
    RETRY_STATUS_CODES,
    RETRY_METHODS,
    DEFAULT_LANGUAGE,
)


class Config:
    """SDK 配置类"""

    def __init__(
        self,
        base_url: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_status_codes: Optional[List[int]] = None,
        retry_methods: Optional[List[str]] = None,
        retry_backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
        language: str = DEFAULT_LANGUAGE,
        enterprise_id: Optional[str] = None,
        **kwargs
    ):
        """
        初始化配置

        Args:
            base_url: API 基础地址
            timeout: 请求超时时间（秒），默认 30
            max_retries: 最大重试次数，默认 3
            retry_status_codes: 需要重试的HTTP状态码列表，默认 [423, 429, 500, 503, 504, 900]
            retry_methods: 允许重试的HTTP方法列表，默认 ["GET", "POST", "PUT", "DELETE"]
            retry_backoff_factor: 重试间隔计算因子，默认 1.0
            language: API 请求语言，默认 'zh_CN'
            enterprise_id: 企业ID（可选，会自动添加到请求头 x-ti-enterprise-id）
            **kwargs: 其他配置参数
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.language = language
        self.enterprise_id = enterprise_id

        # Retry 配置
        self.retry_status_codes = retry_status_codes or RETRY_STATUS_CODES
        self.retry_methods = retry_methods or RETRY_METHODS
        self.retry_backoff_factor = retry_backoff_factor

        self.extra = kwargs

    def get(self, key: str, default: Optional[any] = None) -> any:
        """获取配置项"""
        return self.extra.get(key, default)
