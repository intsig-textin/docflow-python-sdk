"""
HTTP 请求客户端
"""
import json
import logging
import time
import requests
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import (
    APIError,
    AuthenticationError,
    ResourceNotFoundError,
    PermissionDeniedError,
    NetworkError,
)
from .._constants import POOL_CONNECTIONS, POOL_MAXSIZE

# 配置日志
logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP 请求客户端

    支持重试、超时、连接池等特性
    """

    def __init__(self, base_url: str, auth_handler: Any, config: Any):
        """
        初始化 HTTP 客户端

        Args:
            base_url: API 基础地址
            auth_handler: 认证处理器
            config: 配置对象
        """
        self.base_url = base_url.rstrip("/")
        self.auth_handler = auth_handler
        self.config = config
        self.session = requests.Session()
        self.retry_count = 0  # 当前重试次数统计

        # 配置重试策略
        # Retry 会自动处理以下场景：
        # 1. 连接失败
        # 2. 超时
        # 3. 特定的 HTTP 状态码
        retry_strategy = Retry(
            total=config.max_retries,  # 总重试次数
            status_forcelist=config.retry_status_codes,  # 需要重试的HTTP状态码（可配置）
            # 默认: [423, 429, 500, 503, 504, 900]
            # 423: Locked (资源被锁定)
            # 429: Too Many Requests (请求过多)
            # 500: Internal Server Error (服务器内部错误)
            # 503: Service Unavailable (服务不可用)
            # 504: Gateway Timeout (网关超时)
            # 900: 自定义业务错误码
            allowed_methods=config.retry_methods,  # 允许重试的HTTP方法（可配置）
            # 默认: ["GET", "POST", "PUT", "DELETE"]
            backoff_factor=config.retry_backoff_factor,  # 重试间隔计算因子（可配置）
            # 计算公式：{backoff_factor} * (2 ** (重试次数 - 1))
            # 例如：backoff_factor=1 时，重试间隔为 0s, 2s, 4s, 8s...
            raise_on_status=False,  # 不自动抛出异常，由我们的 _handle_response 处理
        )

        # 配置 HTTP 适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=POOL_CONNECTIONS,  # 连接池大小
            pool_maxsize=POOL_MAXSIZE  # 连接池最大连接数
        )

        # 为 HTTP 和 HTTPS 挂载适配器
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.debug(
            f"HTTPClient 初始化完成: base_url={base_url}, "
            f"max_retries={config.max_retries}, timeout={config.timeout}s"
        )

    def _decode_msg(self, msg: str) -> str:
        """
        解码 UTF-8 编码的错误消息

        当后端返回的 JSON 中 msg 字段是 UTF-8 编码的字节序列时，
        requests 会将其解析为 latin-1 编码的字符串。

        Args:
            msg: 可能是 UTF-8 编码序列的字符串

        Returns:
            str: 解码后的字符串
        """
        if not msg:
            return msg

        try:
            # 尝试将 latin-1 编码的字符串转换为 utf-8
            # 这会将 \xe5 等字符正确解码为中文
            return msg.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
            # 如果解码失败，说明消息本身就是正常的字符串，直接返回
            return msg

    def _build_headers(self, headers: Optional[Dict] = None) -> Dict[str, str]:
        """
        构建请求头

        Args:
            headers: 额外的请求头

        Returns:
            Dict[str, str]: 完整的请求头
        """
        default_headers = {
            "User-Agent": "DocflowSDK/1.0.0 Python",
        }

        # 添加认证头
        auth_headers = self.auth_handler.get_auth_headers()
        default_headers.update(auth_headers)

        # 添加语言头
        if hasattr(self.config, 'language') and self.config.language:
            default_headers["lang"] = self.config.language

        # 添加企业ID头
        if hasattr(self.config, 'enterprise_id') and self.config.enterprise_id:
            default_headers["x-ti-enterprise-id"] = str(self.config.enterprise_id)

        if headers:
            default_headers.update(headers)

        return default_headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        处理响应

        Args:
            response: HTTP 响应对象

        Returns:
            Dict[str, Any]: 响应数据

        Raises:
            AuthenticationError: 认证失败
            PermissionDeniedError: 权限不足
            ResourceNotFoundError: 资源不存在
            APIError: API 调用失败
        """
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("认证失败，请检查 app_id 和 secret_code")
            elif response.status_code == 403:
                raise PermissionDeniedError("权限不足")
            elif response.status_code == 404:
                raise ResourceNotFoundError("资源不存在")
            else:
                try:
                    error_data = response.json()
                    # 优先使用 msg 字段，回退到 message
                    message = error_data.get("msg") or error_data.get("message", str(e))
                    # 解码 UTF-8 编码的错误消息
                    message = self._decode_msg(message)
                    code = error_data.get("code")
                    trace_id = error_data.get("traceId")
                except:
                    message = str(e)
                    code = None
                    trace_id = None
                raise APIError(response.status_code, message, code=code, trace_id=trace_id)

        try:
            data = response.json()
            # 检查业务状态码
            if data.get("code") != 200:
                # 获取错误消息，优先使用 msg 字段，回退到 message
                error_msg = data.get("msg") or data.get("message", "未知错误")
                # 解码 UTF-8 编码的错误消息
                error_msg = self._decode_msg(error_msg)

                raise APIError(
                    response.status_code,
                    error_msg,
                    code=str(data.get("code")),
                    trace_id=data.get("traceId")
                )
            return data
        except json.JSONDecodeError:
            raise APIError(response.status_code, "响应解析失败")

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求（支持自动重试）

        Args:
            method: HTTP 方法
            path: 请求路径
            params: URL 参数
            json_data: JSON 数据
            files: 文件数据
            data: 表单数据
            headers: 请求头
            retry_count: 内部参数，当前重试次数

        Returns:
            Dict[str, Any]: 响应数据

        Raises:
            NetworkError: 网络错误
            APIError: API 调用失败
        """
        url = f"{self.base_url}{path}"
        headers = self._build_headers(headers)

        # 记录请求日志
        logger.debug(f"发送请求: {method} {url}, retry={retry_count}")

        try:
            start_time = time.time()

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                files=files,
                data=data,
                headers=headers,
                timeout=self.config.timeout,
            )

            # 计算请求耗时
            elapsed = time.time() - start_time
            logger.debug(
                f"请求完成: {method} {url}, "
                f"status={response.status_code}, elapsed={elapsed:.2f}s"
            )

            # 记录重试统计
            if retry_count > 0:
                logger.info(
                    f"重试成功: {method} {url}, "
                    f"retry_count={retry_count}, status={response.status_code}"
                )

            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            logger.warning(f"请求超时: {method} {url}, retry={retry_count}")
            raise NetworkError(f"请求超时: {str(e)}")

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"网络连接失败: {method} {url}, retry={retry_count}")
            raise NetworkError(f"网络连接失败: {str(e)}")

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {method} {url}, error={str(e)}")
            raise NetworkError(f"网络请求失败: {str(e)}")

    def get(
        self, path: str, params: Optional[Dict] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        GET 请求

        Args:
            path: 请求路径
            params: URL 参数
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 响应数据
        """
        return self.request("GET", path, params=params, **kwargs)

    def post(
        self, path: str, json_data: Optional[Dict] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        POST 请求

        Args:
            path: 请求路径
            json_data: JSON 数据
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 响应数据
        """
        return self.request("POST", path, json_data=json_data, **kwargs)

    def get_retry_stats(self) -> Dict[str, Any]:
        """
        获取重试统计信息

        Returns:
            Dict[str, Any]: 重试统计信息
        """
        return {
            "max_retries": self.config.max_retries,
            "retry_status_codes": [423, 429, 500, 503, 504, 900],
            "backoff_factor": 1,
        }

    def close(self):
        """关闭会话，释放连接池资源"""
        logger.debug("关闭 HTTPClient 会话")
        self.session.close()
