"""
SDK 异常类定义（支持国际化）
"""
from typing import Optional


class DocflowException(Exception):
    """
    SDK 基础异常

    支持国际化（i18n）的异常基类
    """

    def __init__(self, message: str, i18n_key: Optional[str] = None, **kwargs):
        """
        初始化异常

        Args:
            message: 错误消息（用作后备）
            i18n_key: 国际化消息键
            **kwargs: 用于消息格式化的参数
        """
        self.i18n_key = i18n_key
        self.format_params = kwargs
        self._original_message = message

        # 尝试使用 i18n 翻译
        if i18n_key:
            try:
                from .i18n import translate
                message = translate(i18n_key, **kwargs)
            except (ImportError, Exception):
                # 如果 i18n 不可用或翻译失败，使用原始消息
                pass

        self.message = message
        super().__init__(message)


class AuthenticationError(DocflowException):
    """认证失败异常"""

    def __init__(self, message: str = None, **kwargs):
        if message is None:
            message = "Authentication failed"
        super().__init__(
            message,
            i18n_key='error.auth.failed',
            **kwargs
        )


class ValidationError(DocflowException):
    """参数校验异常"""

    def __init__(self, message: str, i18n_key: Optional[str] = None, **kwargs):
        if i18n_key is None:
            # 如果没有指定 i18n_key，保持原始消息
            i18n_key = None
        super().__init__(message, i18n_key=i18n_key, **kwargs)


class ResourceNotFoundError(DocflowException):
    """资源不存在异常"""

    def __init__(self, message: str = None, **kwargs):
        if message is None:
            message = "Resource not found"
        super().__init__(
            message,
            i18n_key='error.resource.not_found',
            **kwargs
        )


class PermissionDeniedError(DocflowException):
    """权限不足异常"""

    def __init__(self, message: str = None, **kwargs):
        if message is None:
            message = "Permission denied"
        super().__init__(
            message,
            i18n_key='error.permission.denied',
            **kwargs
        )


class APIError(DocflowException):
    """API 调用异常"""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: Optional[str] = None,
        trace_id: Optional[str] = None,
        i18n_key: Optional[str] = None
    ):
        self.status_code = status_code
        self.code = code
        self.trace_id = trace_id

        # 服务端已给出业务错误码时保留具体原因，避免 HTTP 通用翻译覆盖业务消息。
        if i18n_key is None and code is None and status_code in [400, 401, 403, 404, 423, 429, 500, 502, 503, 504, 900]:
            i18n_key = f'error.http.{status_code}'

        # 格式化错误消息
        error_msg = f"[{status_code}] {message}"
        if code:
            error_msg += f" (code: {code})"
        if trace_id:
            error_msg += f" (traceId: {trace_id})"

        super().__init__(
            error_msg,
            i18n_key=i18n_key,
            status_code=status_code,
            error_message=message,
            code=code,
            trace_id=trace_id
        )


class NetworkError(DocflowException):
    """网络异常"""

    def __init__(self, message: str, i18n_key: Optional[str] = None, **kwargs):
        if i18n_key is None:
            i18n_key = 'error.network'
        super().__init__(message, i18n_key=i18n_key, **kwargs)
