"""
工作空间资源操作类
"""
from typing import List, Optional, Union, TYPE_CHECKING
from .base import BaseResource
from ..models.workspace import (
    WorkspaceCreateResponse,
    WorkspaceListResponse,
    WorkspaceDetailResponse,
)
from ..exceptions import ValidationError
from ..enums import AuthScope
from .._constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, API_PREFIX

if TYPE_CHECKING:
    from ..context import WorkspaceContext


class WorkspaceResource(BaseResource):
    """
    工作空间相关操作

    提供工作空间的创建、查询、更新、删除等功能

    也可以通过调用方式绑定工作空间上下文：
        >>> ws = client.workspace("123")
        >>> ws.get()  # 获取工作空间详情
        >>> cat = ws.category("456")  # 链式调用类别
    """

    def __init__(self, http_client, category_resource=None, review_resource=None):
        """
        初始化工作空间资源

        Args:
            http_client: HTTP 客户端
            category_resource: 类别资源（可选，用于链式调用）
            review_resource: 审核规则资源（可选，用于链式调用）
        """
        super().__init__(http_client)
        self._category_resource = category_resource
        self._review_resource = review_resource

    def __call__(self, workspace_id: str) -> "WorkspaceContext":
        """
        绑定工作空间上下文，实现链式调用

        Args:
            workspace_id: 工作空间 ID

        Returns:
            WorkspaceContext: 工作空间上下文对象

        Examples:
            >>> # 绑定工作空间
            >>> ws = client.workspace("123")
            >>>
            >>> # 获取详情
            >>> detail = ws.get()
            >>>
            >>> # 更新工作空间
            >>> ws.update(name="新名称", auth_scope=AuthScope.PUBLIC)
            >>>
            >>> # 链式调用：操作类别
            >>> cat = ws.category("456")
            >>> cat.fields.add(name="税率")
            >>>
            >>> # 链式调用：操作审核规则
            >>> repo = ws.review.create_repo(name="发票审核规则库")
        """
        from ..context import WorkspaceContext
        from .category import CategoryResource
        from .review import ReviewResource

        # 使用传入的 category_resource 或创建新实例
        category_resource = self._category_resource
        if category_resource is None:
            category_resource = CategoryResource(self.http_client)

        # 使用传入的 review_resource 或创建新实例
        review_resource = self._review_resource
        if review_resource is None:
            review_resource = ReviewResource(self.http_client)

        return WorkspaceContext(
            http_client=self.http_client,
            workspace_resource=self,
            category_resource=category_resource,
            review_resource=review_resource,
            workspace_id=workspace_id,
        )

    def create(
        self,
        name: str,
        auth_scope: Union[AuthScope, int],
        description: Optional[str] = None,
        **kwargs
    ) -> WorkspaceCreateResponse:
        """
        创建工作空间

        注意：企业ID通过请求头 x-ti-enterprise-id 传递，需要在初始化客户端时配置：
        - 从环境变量：export DOCFLOW_ENTERPRISE_ID="12345"
        - 代码配置：client = DocflowClient(..., enterprise_id="12345")

        Args:
            name: 工作空间名称（最大 50 字符）
            auth_scope: 权限范围（AuthScope.PRIVATE=0 或 AuthScope.PUBLIC=1，必填）
            description: 空间描述（可选，最大 200 字符）
            **kwargs: 其他可选参数

        Returns:
            WorkspaceCreateResponse: 包含新创建的工作空间 ID

        Raises:
            ValidationError: 参数校验失败
            APIError: API 调用失败

        Examples:
            >>> from docflow import AuthScope
            >>>
            >>> # 方式1：从环境变量配置企业ID
            >>> # export DOCFLOW_ENTERPRISE_ID="12345"
            >>> client = DocflowClient.from_env()
            >>> workspace = client.workspace.create(
            ...     name="我的工作空间",
            ...     auth_scope=AuthScope.PUBLIC,
            ...     description="这是一个用于处理发票的工作空间"
            ... )
            >>>
            >>> # 方式2：代码中配置企业ID
            >>> client = DocflowClient(
            ...     app_id="your-app-id",
            ...     secret_code="your-secret-code",
            ...     enterprise_id="12345"
            ... )
            >>> workspace = client.workspace.create(
            ...     name="我的工作空间",
            ...     auth_scope=1  # 也支持直接使用数字
            ... )
            >>> print(workspace.workspace_id)
        """
        # 参数校验
        if not name or not name.strip():
            raise ValidationError(
                "工作空间名称不能为空",
                i18n_key='error.workspace.name_empty'
            )

        if len(name) > 50:
            raise ValidationError(
                "工作空间名称不能超过 50 个字符",
                i18n_key='error.workspace.name_too_long',
                max_length=50
            )

        if description is not None and len(description) > 200:
            raise ValidationError(
                "工作空间描述不能超过 200 个字符",
                i18n_key='error.workspace.description_too_long',
                max_length=200
            )

        # 支持 AuthScope 枚举和 int 类型
        auth_scope_value = auth_scope.value if isinstance(auth_scope, AuthScope) else auth_scope
        if auth_scope_value not in (0, 1):
            raise ValidationError(
                "auth_scope 只能是 AuthScope.PRIVATE(0) 或 AuthScope.PUBLIC(1)",
                i18n_key='error.workspace.auth_scope_invalid'
            )

        payload = {
            "name": name,
            "auth_scope": auth_scope_value,
        }

        if description is not None:
            payload["description"] = description

        payload.update(kwargs)

        response = self.http_client.post(
            f"{API_PREFIX}/workspace/create", json_data=payload
        )

        return WorkspaceCreateResponse.from_dict(response["result"])

    def list(
        self, page: int = DEFAULT_PAGE, page_size: int = DEFAULT_PAGE_SIZE
    ) -> WorkspaceListResponse:
        """
        获取工作空间列表

        注意：企业ID通过请求头 x-ti-enterprise-id 传递，需要在初始化客户端时配置：
        - 从环境变量：export DOCFLOW_ENTERPRISE_ID="12345"
        - 代码配置：client = DocflowClient(..., enterprise_id="12345")

        Args:
            page: 页码，从 1 开始，默认 1
            page_size: 每页数量，默认 20

        Returns:
            WorkspaceListResponse: 工作空间列表响应

        Raises:
            ValidationError: 参数校验失败
            APIError: API 调用失败

        Examples:
            >>> # 方式1：从环境变量配置企业ID
            >>> # export DOCFLOW_ENTERPRISE_ID="12345"
            >>> client = DocflowClient.from_env()
            >>> workspaces = client.workspace.list(page=1, page_size=20)
            >>> for ws in workspaces.workspaces:
            ...     print(f"{ws.workspace_id}: {ws.name}")
            >>>
            >>> # 方式2：代码中配置企业ID
            >>> client = DocflowClient(
            ...     app_id="your-app-id",
            ...     secret_code="your-secret-code",
            ...     enterprise_id="12345"
            ... )
            >>> workspaces = client.workspace.list()
        """
        if page < 1:
            raise ValidationError(
                "页码必须大于等于 1",
                i18n_key='error.workspace.page_invalid'
            )

        if page_size < 1 or page_size > 100:
            raise ValidationError(
                "每页数量必须在 1-100 之间",
                i18n_key='error.workspace.page_size_invalid'
            )

        params = {"page": page, "page_size": page_size}

        response = self.http_client.get(f"{API_PREFIX}/workspace/list", params=params)

        return WorkspaceListResponse.from_dict(response["result"])

    def get(self, workspace_id: str) -> WorkspaceDetailResponse:
        """
        获取工作空间详情

        Args:
            workspace_id: 工作空间 ID

        Returns:
            WorkspaceDetailResponse: 工作空间详细信息

        Raises:
            ValidationError: 参数校验失败
            ResourceNotFoundError: 工作空间不存在
            APIError: API 调用失败

        Examples:
            >>> detail = client.workspace.get(workspace_id="123")
            >>> print(detail.name)
        """
        if not workspace_id or not workspace_id.strip():
            raise ValidationError(
                "工作空间 ID 不能为空",
                i18n_key='error.workspace.id_empty'
            )

        # 校验 workspace_id 格式（必须是数字字符串）
        if not workspace_id.isdigit():
            raise ValidationError(
                "工作空间 ID 格式错误，必须是数字",
                i18n_key='error.workspace.id_invalid'
            )

        params = {"workspace_id": workspace_id}

        response = self.http_client.get(f"{API_PREFIX}/workspace/get", params=params)

        return WorkspaceDetailResponse.from_dict(response["result"])

    def update(
        self,
        workspace_id: str,
        name: str,
        auth_scope: Union[AuthScope, int],
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        callback_retry_time: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        更新工作空间

        Args:
            workspace_id: 工作空间 ID
            name: 工作空间名称（最大 50 字符）
            auth_scope: 权限范围（AuthScope.PRIVATE=0 或 AuthScope.PUBLIC=1）
            description: 空间描述（可选，最大 200 字符）
            callback_url: 回调URL（可选）
            callback_retry_time: 回调重试次数（可选，范围 1-3）
            **kwargs: 其他可选参数

        Raises:
            ValidationError: 参数校验失败
            ResourceNotFoundError: 工作空间不存在
            PermissionDeniedError: 权限不足
            APIError: API 调用失败

        Examples:
            >>> from docflow import AuthScope
            >>>
            >>> # 使用枚举（推荐）
            >>> client.workspace.update(
            ...     workspace_id="123",
            ...     name="新的工作空间名称",
            ...     auth_scope=AuthScope.PRIVATE,
            ...     description="更新后的描述",
            ...     callback_url="https://example.com/callback",
            ...     callback_retry_time=3
            ... )
            >>>
            >>> # 也支持直接使用数字
            >>> client.workspace.update(
            ...     workspace_id="123",
            ...     name="新的工作空间名称",
            ...     auth_scope=0
            ... )
        """
        if not workspace_id or not workspace_id.strip():
            raise ValidationError(
                "工作空间 ID 不能为空",
                i18n_key='error.workspace.id_empty'
            )

        if not workspace_id.isdigit():
            raise ValidationError(
                "工作空间 ID 格式错误，必须是数字",
                i18n_key='error.workspace.id_invalid'
            )

        if not name or not name.strip():
            raise ValidationError(
                "工作空间名称不能为空",
                i18n_key='error.workspace.name_empty'
            )

        if len(name) > 50:
            raise ValidationError(
                "工作空间名称不能超过 50 个字符",
                i18n_key='error.workspace.name_too_long',
                max_length=50
            )

        # 支持 AuthScope 枚举和 int 类型
        auth_scope_value = auth_scope.value if isinstance(auth_scope, AuthScope) else auth_scope
        if auth_scope_value not in (0, 1):
            raise ValidationError(
                "auth_scope 只能是 AuthScope.PRIVATE(0) 或 AuthScope.PUBLIC(1)",
                i18n_key='error.workspace.auth_scope_invalid'
            )

        if description is not None and len(description) > 200:
            raise ValidationError(
                "工作空间描述不能超过 200 个字符",
                i18n_key='error.workspace.description_too_long',
                max_length=200
            )

        if callback_retry_time is not None and (callback_retry_time < 1 or callback_retry_time > 3):
            raise ValidationError(
                "回调重试次数必须在 1-3 之间",
                i18n_key='error.workspace.callback_retry_time_invalid'
            )

        payload = {
            "workspace_id": workspace_id,
            "name": name,
            "auth_scope": auth_scope_value
        }

        if description is not None:
            payload["description"] = description

        if callback_url is not None:
            payload["callback_url"] = callback_url

        if callback_retry_time is not None:
            payload["callback_retry_time"] = callback_retry_time

        payload.update(kwargs)

        self.http_client.post(f"{API_PREFIX}/workspace/update", json_data=payload)

    def delete(self, workspace_ids: List[str]) -> None:
        """
        批量删除工作空间

        Args:
            workspace_ids: 要删除的工作空间 ID 列表

        Raises:
            ValidationError: 参数校验失败
            PermissionDeniedError: 权限不足
            APIError: API 调用失败

        Examples:
            >>> client.workspace.delete(workspace_ids=["123", "456"])
        """
        if not workspace_ids:
            raise ValidationError(
                "workspace_ids 不能为空",
                i18n_key='error.workspace.delete_list_empty'
            )

        # 校验每个 workspace_id 的格式
        for workspace_id in workspace_ids:
            if not workspace_id or not workspace_id.strip():
                raise ValidationError(
                    "工作空间 ID 不能为空",
                    i18n_key='error.workspace.id_empty'
                )
            if not workspace_id.isdigit():
                raise ValidationError(
                    f"工作空间 ID 格式错误: {workspace_id}",
                    i18n_key='error.workspace.id_invalid'
                )

        payload = {"workspace_ids": workspace_ids}

        self.http_client.post(f"{API_PREFIX}/workspace/delete", json_data=payload)

    def iter(
        self,
        page_size: int = 20,
        max_pages: Optional[int] = None
    ):
        """
        迭代获取工作空间列表，自动处理分页

        注意：企业ID通过请求头 x-ti-enterprise-id 传递，需要在初始化客户端时配置：
        - 从环境变量：export DOCFLOW_ENTERPRISE_ID="12345"
        - 代码配置：client = DocflowClient(..., enterprise_id="12345")

        Args:
            page_size: 每页数量，默认 20，最大 100
            max_pages: 最大页数限制（可选，用于防止无限循环）

        Yields:
            WorkspaceDetailResponse: 工作空间详细信息

        Examples:
            >>> # 方式1：从环境变量配置企业ID
            >>> # export DOCFLOW_ENTERPRISE_ID="12345"
            >>> client = DocflowClient.from_env()
            >>>
            >>> # 遍历所有工作空间
            >>> for workspace in client.workspace.iter():
            ...     print(f"{workspace.workspace_id}: {workspace.name}")
            ...     if some_condition:
            ...         break  # 可以随时中断
            >>>
            >>> # 限制最大页数
            >>> for workspace in client.workspace.iter(max_pages=5):
            ...     print(workspace.name)
            >>>
            >>> # 转换为列表（获取所有数据）
            >>> all_workspaces = list(client.workspace.iter())
            >>>
            >>> # 方式2：代码中配置企业ID
            >>> client = DocflowClient(
            ...     app_id="your-app-id",
            ...     secret_code="your-secret-code",
            ...     enterprise_id="12345"
            ... )
            >>> for workspace in client.workspace.iter():
            ...     print(workspace.name)
        """
        page = 1
        pages_fetched = 0

        while True:
            # 检查是否达到最大页数限制
            if max_pages is not None and pages_fetched >= max_pages:
                break

            # 获取当前页数据
            response = self.list(
                page=page,
                page_size=page_size
            )

            # 逐个yield工作空间
            for workspace in response.workspaces:
                yield workspace

            # 检查是否还有下一页
            if page * page_size >= response.total:
                break

            page += 1
            pages_fetched += 1
