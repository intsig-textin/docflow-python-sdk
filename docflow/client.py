"""
Docflow SDK 主客户端
"""
import os
from typing import Optional, List
from .resources.workspace import WorkspaceResource
from .resources.category import CategoryResource
from .resources.file import FileResource
from .resources.review import ReviewResource
from .context import WorkspaceContext
from .utils.http_client import HTTPClient
from .auth import AuthHandler
from .config import Config
from ._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_FACTOR,
    DEFAULT_LANGUAGE,
)


class DocflowClient:
    """
    Docflow SDK 主客户端

    提供对工作空间、类别、字段、表格、样本等资源的访问接口

    Examples:
        >>> # 方式1: 直接初始化（使用默认 base_url）
        >>> client = DocflowClient(
        ...     app_id="your-app-id",
        ...     secret_code="your-secret-code"
        ... )

        >>> # 方式2: 从环境变量加载
        >>> client = DocflowClient.from_env()

        >>> # 方式3: 自定义 base_url
        >>> client = DocflowClient(
        ...     app_id="your-app-id",
        ...     secret_code="your-secret-code",
        ...     base_url="https://custom.api.com/api"
        ... )

        >>> workspace = client.workspace.create(
        ...     name="我的工作空间",
        ...     auth_scope=1
        ... )
    """

    @classmethod
    def from_env(
        cls,
        app_id_env: str = "DOCFLOW_APP_ID",
        secret_code_env: str = "DOCFLOW_SECRET_CODE",
        base_url_env: str = "DOCFLOW_BASE_URL",
        enterprise_id_env: str = "DOCFLOW_ENTERPRISE_ID",
        **kwargs
    ) -> "DocflowClient":
        """
        从环境变量创建客户端实例

        Args:
            app_id_env: 应用ID的环境变量名，默认 "DOCFLOW_APP_ID"
            secret_code_env: 密钥的环境变量名，默认 "DOCFLOW_SECRET_CODE"
            base_url_env: API地址的环境变量名，默认 "DOCFLOW_BASE_URL"
            enterprise_id_env: 企业ID的环境变量名，默认 "DOCFLOW_ENTERPRISE_ID"
            **kwargs: 其他配置参数

        Returns:
            DocflowClient: 客户端实例

        Raises:
            ValueError: 当必需的环境变量未设置时

        Examples:
            >>> # 设置环境变量
            >>> # export DOCFLOW_APP_ID="your-app-id"
            >>> # export DOCFLOW_SECRET_CODE="your-secret-code"
            >>> # export DOCFLOW_BASE_URL="https://docflow.textin.com/api"  # 可选
            >>> # export DOCFLOW_ENTERPRISE_ID="12345"  # 可选
            >>>
            >>> # 从环境变量创建客户端
            >>> client = DocflowClient.from_env()
            >>>
            >>> # 使用自定义环境变量名
            >>> client = DocflowClient.from_env(
            ...     app_id_env="MY_APP_ID",
            ...     secret_code_env="MY_SECRET"
            ... )
        """
        app_id = os.getenv(app_id_env)
        secret_code = os.getenv(secret_code_env)
        base_url = os.getenv(base_url_env)
        enterprise_id = os.getenv(enterprise_id_env)

        if not app_id:
            raise ValueError(f"环境变量 {app_id_env} 未设置")
        if not secret_code:
            raise ValueError(f"环境变量 {secret_code_env} 未设置")

        # base_url 和 enterprise_id 可选，如果未设置则使用默认值
        init_kwargs = {"app_id": app_id, "secret_code": secret_code}
        if base_url:
            init_kwargs["base_url"] = base_url
        if enterprise_id:
            init_kwargs["enterprise_id"] = enterprise_id

        init_kwargs.update(kwargs)

        return cls(**init_kwargs)

    def __init__(
        self,
        app_id: str,
        secret_code: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        language: str = DEFAULT_LANGUAGE,
        enterprise_id: Optional[str] = None,
        retry_status_codes: Optional[List[int]] = None,
        retry_methods: Optional[List[str]] = None,
        retry_backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
        **kwargs
    ):
        """
        初始化 SDK 客户端

        Args:
            app_id: 应用ID（对应请求头 x-ti-app-id）
            secret_code: 密钥（对应请求头 x-ti-secret-code）
            base_url: API 基础地址，默认 "https://docflow.textin.com/api"
            timeout: 请求超时时间（秒），默认 30 秒
            max_retries: 最大重试次数，默认 3 次
            language: 错误消息语言，支持 'zh_CN'（中文）、'en_US'（英文），默认 'zh_CN'
            retry_status_codes: 需要重试的HTTP状态码列表，默认 [423, 429, 500, 503, 504, 900]
            retry_methods: 允许重试的HTTP方法列表，默认 ["GET", "POST", "PUT", "DELETE"]
            retry_backoff_factor: 重试间隔计算因子，默认 1.0
            **kwargs: 其他配置参数

        Raises:
            ValueError: 当未提供 app_id 或 secret_code 时
        """
        if not app_id or not secret_code:
            raise ValueError("必须提供 app_id 和 secret_code")

        # 设置语言
        from .i18n import set_language
        try:
            set_language(language)
        except ValueError as e:
            # 如果语言不支持，使用默认语言并发出警告
            import warnings
            warnings.warn(str(e))
            set_language('zh_CN')

        # 初始化配置
        self.config = Config(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_status_codes=retry_status_codes,
            retry_methods=retry_methods,
            retry_backoff_factor=retry_backoff_factor,
            language=language,
            enterprise_id=enterprise_id,
            **kwargs
        )

        # 初始化认证处理器
        self.auth = AuthHandler(app_id=app_id, secret_code=secret_code)

        # 初始化 HTTP 客户端
        self.http_client = HTTPClient(
            base_url=base_url, auth_handler=self.auth, config=self.config
        )

        # 初始化资源访问接口
        self.category = CategoryResource(self.http_client)
        self.file = FileResource(self.http_client)
        self.review = ReviewResource(self.http_client)
        self.workspace = WorkspaceResource(
            self.http_client,
            category_resource=self.category,
            review_resource=self.review
        )

    def set_credentials(self, app_id: str, secret_code: str) -> None:
        """
        更新认证凭证

        Args:
            app_id: 新的应用ID
            secret_code: 新的密钥
        """
        self.auth.set_credentials(app_id, secret_code)

    def set_language(self, language: str) -> None:
        """
        设置错误消息语言和 API 请求语言

        Args:
            language: 语言代码，如 'zh_CN'（中文）、'en_US'（英文）

        Raises:
            ValueError: 当语言不支持时

        Examples:
            >>> client.set_language('en_US')  # 切换到英文
            >>> client.set_language('zh_CN')  # 切换到中文
        """
        from .i18n import set_language
        set_language(language)
        # 同步更新配置中的语言设置，影响 API 请求头
        self.config.language = language

    def get_language(self) -> str:
        """
        获取当前语言设置

        Returns:
            str: 当前语言代码
        """
        from .i18n import get_language
        return get_language()

    def get_available_languages(self) -> list:
        """
        获取所有可用语言

        Returns:
            list: 可用语言列表
        """
        from .i18n import i18n
        return i18n.get_available_languages()

    def close(self) -> None:
        """关闭客户端，释放资源"""
        self.http_client.close()

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()
