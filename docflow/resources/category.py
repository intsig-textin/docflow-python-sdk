"""
类别资源操作类
"""
import json
import os
import re
from typing import List, Optional, Union, BinaryIO, Dict, Any, Tuple
from urllib.parse import unquote

from .base import BaseResource
from ..exceptions import ValidationError, APIError
from ..models.category import (
    CategoryCreateResponse,
    CategoryListResponse,
    TableListResponse,
    TableAddResponse,
    FieldListResponse,
    FieldAddResponse,
    FieldConfigResponse,
    SampleUploadResponse,
    SampleListResponse,
)
from ..utils.file_handler import FileHandler
from ..enums import ExtractModel, EnabledStatus, EnabledFlag, FieldType
from .._constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, API_PREFIX


class CategoryResource(BaseResource):
    """
    文件类别相关操作

    Examples:
        >>> # 创建类别
        >>> category = client.category.create(
        ...     workspace_id="123",
        ...     name="发票类别",
        ...     extract_model="Model 1",
        ...     sample_files=["/path/to/sample.pdf"],
        ...     fields=[{"name": "发票号码"}]
        ... )

        >>> # 获取类别列表
        >>> categories = client.category.list(workspace_id="123")

        >>> # 操作字段
        >>> field = client.category.fields.add(
        ...     workspace_id="123",
        ...     category_id="456",
        ...     name="金额",
        ...     required=True
        ... )
    """

    def __init__(self, http_client):
        super().__init__(http_client)
        # 初始化子资源
        self.tables = CategoryTableResource(http_client)
        self.fields = CategoryFieldResource(http_client)
        self.samples = CategorySampleResource(http_client)

    def create(
        self,
        workspace_id: str,
        name: str,
        extract_model: Union[ExtractModel, str],
        sample_files: List[Union[str, BinaryIO]],
        fields: List[Dict[str, Any]],
        category_prompt: Optional[str] = None,
    ) -> CategoryCreateResponse:
        """
        创建文件类别

        Args:
            workspace_id: 工作空间 ID
            name: 类别名称（最大 50 字符）
            extract_model: 提取模型（ExtractModel.Model_1/Model_2/Model_3 或字符串 "Model 1"/"Model 2"/"Model 3"）
            sample_files: 样本文件列表（支持文件路径、文件对象）
            fields: 字段配置列表，例如:
                [
                    {"name": "发票号码", "description": "发票唯一标识"},
                    {"name": "金额", "description": "发票总金额"}
                ]
            category_prompt: 类别提示（最大 150 字符，可选）

        Returns:
            CategoryCreateResponse: 包含新创建的类别 ID

        Raises:
            ValidationError: 参数校验失败
            APIError: API 调用失败

        Examples:
            >>> from docflow import ExtractModel, FieldType
            >>>
            >>> # 使用枚举（推荐）
            >>> category = client.category.create(
            ...     workspace_id="123",
            ...     name="发票类别",
            ...     extract_model=ExtractModel.Model_1,
            ...     sample_files=[
            ...         "/path/to/sample1.pdf",
            ...         open("/path/to/sample2.pdf", "rb")
            ...     ],
            ...     fields=[
            ...         {"name": "发票号码", "description": "发票唯一标识"},
            ...         {
            ...             "name": "开票日期",
            ...             "transform_settings": {
            ...                 "type": FieldType.DATETIME.value,
            ...                 "datetime_settings": {"format": "yyyy-MM-dd"}
            ...             }
            ...         }
            ...     ],
            ...     category_prompt="这是发票类别"
            ... )
            >>>
            >>> # 也支持直接使用字符串
            >>> category = client.category.create(
            ...     workspace_id="123",
            ...     name="发票类别",
            ...     extract_model="Model 1",
            ...     sample_files=["/path/to/sample.pdf"],
            ...     fields=[{"name": "发票号码"}]
            ... )
            >>> print(category.category_id)
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)

        if not name or len(name) > 50:
            raise ValidationError(
                "类别名称不能为空且最大长度为 50 字符",
                i18n_key='error.category.name_invalid'
            )

        # 支持 ExtractModel 枚举和 str 类型
        extract_model_value = extract_model.value if isinstance(extract_model, ExtractModel) else extract_model
        if extract_model_value not in ("Model 1", "Model 2", "Model 3"):
            raise ValidationError(
                "extract_model 必须是 ExtractModel.Model_1/Model_2/Model_3 或对应的字符串",
                i18n_key='error.category.extract_model_invalid'
            )

        if not sample_files:
            raise ValidationError(
                "至少需要提供一个样本文件",
                i18n_key='error.category.sample_files_empty'
            )

        if not fields:
            raise ValidationError(
                "至少需要提供一个字段配置",
                i18n_key='error.category.fields_empty'
            )

        if category_prompt and len(category_prompt) > 150:
            raise ValidationError(
                "类别提示最大长度为 150 字符",
                i18n_key='error.category.prompt_too_long'
            )

        # 准备 multipart/form-data 表单数据
        data = {
            "workspace_id": workspace_id,
            "name": name,
            "extract_model": extract_model_value,
            "fields": json.dumps(fields, ensure_ascii=False),
        }

        if category_prompt:
            data["category_prompt"] = category_prompt

        # 准备文件
        files = FileHandler.prepare_files(sample_files, field_name="sample_files")

        # 发送请求
        response = self.http_client.request(
            method="POST",
            path=f"{API_PREFIX}/category/create",
            files=files,
            data=data,
        )

        return CategoryCreateResponse.from_dict(response["result"])

    def list(
        self,
        workspace_id: str,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        enabled: Union[EnabledStatus, str] = EnabledStatus.ENABLED,
    ) -> CategoryListResponse:
        """
        获取分类列表

        Args:
            workspace_id: 工作空间 ID
            page: 页码，从 1 开始，默认 1
            page_size: 每页数量，默认 20，最大 100
            enabled: 启用状态
                - EnabledStatus.ALL: 全部
                - EnabledStatus.DISABLED: 未启用
                - EnabledStatus.ENABLED: 已启用（默认）
                - EnabledStatus.OTHER: 其他状态

        Returns:
            CategoryListResponse: 分类列表响应

        Examples:
            >>> from docflow import EnabledStatus
            >>>
            >>> # 获取所有已启用的类别（使用枚举，推荐）
            >>> categories = client.category.list(
            ...     workspace_id="123",
            ...     page=1,
            ...     page_size=20,
            ...     enabled=EnabledStatus.ENABLED
            ... )
            >>> for cat in categories.categories:
            ...     print(f"{cat.id}: {cat.name}")

            >>> # 获取全部类别（包括未启用）
            >>> all_categories = client.category.list(
            ...     workspace_id="123",
            ...     enabled=EnabledStatus.ALL
            ... )
            >>>
            >>> # 也支持直接使用字符串
            >>> categories = client.category.list(
            ...     workspace_id="123",
            ...     enabled="1"
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_page_params(page, page_size)

        # 支持 EnabledStatus 枚举和 str 类型
        enabled_value = enabled.value if isinstance(enabled, EnabledStatus) else enabled
        if enabled_value not in ("all", "0", "1", "2"):
            raise ValidationError(
                "enabled 必须是 EnabledStatus.ALL/DISABLED/ENABLED/OTHER 或对应的字符串值",
                i18n_key='error.category.enabled_invalid'
            )

        params = {
            "workspace_id": workspace_id,
            "page": page,
            "page_size": page_size,
            "enabled": enabled_value,
        }

        response = self.http_client.get(f"{API_PREFIX}/category/list", params=params)

        return CategoryListResponse.from_dict(response["result"])

    def update(
        self,
        workspace_id: str,
        category_id: str,
        name: Optional[str] = None,
        category_prompt: Optional[str] = None,
        enabled: Optional[Union[EnabledFlag, int]] = None,
        extract_model: Optional[Union[ExtractModel, str]] = None,
        **kwargs,
    ) -> None:
        """
        更新文件类别

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            name: 新的类别名称（可选）
            category_prompt: 新的类别提示（可选）
            enabled: 启用状态（EnabledFlag.DISABLED=0 或 EnabledFlag.ENABLED=1，可选）
            extract_model: 提取模型（ExtractModel.Model_1/Model_2/Model_3，可选）
            **kwargs: 其他要更新的字段

        Examples:
            >>> from docflow import EnabledFlag, ExtractModel
            >>>
            >>> # 使用枚举（推荐）
            >>> client.category.update(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     name="更新后的类别名称",
            ...     category_prompt="新的提示",
            ...     enabled=EnabledFlag.ENABLED,
            ...     extract_model=ExtractModel.Model_2
            ... )
            >>>
            >>> # 也支持直接使用字符串
            >>> client.category.update(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     extract_model="Model 1"
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_category_id(category_id)

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
        }

        if name is not None:
            if not name or len(name) > 50:
                raise ValidationError(
                    "类别名称不能为空且最大长度为 50 字符",
                    i18n_key='error.category.name_invalid'
                )
            payload["name"] = name

        if category_prompt is not None:
            if len(category_prompt) > 150:
                raise ValidationError(
                    "类别提示最大长度为 150 字符",
                    i18n_key='error.category.prompt_too_long'
                )
            payload["category_prompt"] = category_prompt

        if extract_model is not None:
            # 支持 ExtractModel 枚举和 str 类型
            extract_model_value = extract_model.value if isinstance(extract_model, ExtractModel) else extract_model
            if extract_model_value not in ("Model 1", "Model 2", "Model 3"):
                raise ValidationError(
                    "extract_model 必须是 ExtractModel.Model_1/Model_2/Model_3 或对应的字符串",
                    i18n_key='error.category.extract_model_invalid'
                )
            payload["extract_model"] = extract_model_value

        if enabled is not None:
            # 支持 EnabledFlag 枚举和 int 类型
            enabled_value = enabled.value if isinstance(enabled, EnabledFlag) else enabled
            if enabled_value not in (0, 1):
                raise ValidationError(
                    "enabled 只能是 EnabledFlag.DISABLED(0) 或 EnabledFlag.ENABLED(1)",
                    i18n_key='error.category.enabled_flag_invalid'
                )
            payload["enabled"] = enabled_value

        payload.update(kwargs)

        self.http_client.post(f"{API_PREFIX}/category/update", json_data=payload)

    def delete(self, workspace_id: str, category_ids: List[str]) -> None:
        """
        批量删除文件类别

        Args:
            workspace_id: 工作空间 ID
            category_ids: 要删除的类别 ID 列表

        Examples:
            >>> client.category.delete(
            ...     workspace_id="123",
            ...     category_ids=["456", "789"]
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)

        if not category_ids:
            raise ValidationError(
                "category_ids 不能为空",
                i18n_key='error.category.delete_list_empty'
            )

        for category_id in category_ids:
            self._validate_category_id(category_id)

        payload = {"workspace_id": workspace_id, "category_ids": category_ids}

        self.http_client.post(f"{API_PREFIX}/category/delete", json_data=payload)

    def iter(
        self,
        workspace_id: str,
        page_size: int = 20,
        enabled: Union[EnabledStatus, str] = EnabledStatus.ENABLED,
        max_pages: Optional[int] = None
    ):
        """
        迭代获取类别列表，自动处理分页

        Args:
            workspace_id: 工作空间 ID
            page_size: 每页数量，默认 20，最大 100
            enabled: 启用状态（EnabledStatus 枚举或字符串），默认 EnabledStatus.ENABLED
            max_pages: 最大页数限制（可选，用于防止无限循环）

        Yields:
            Category: 类别信息

        Examples:
            >>> from docflow import EnabledStatus
            >>>
            >>> # 遍历所有类别（使用枚举，推荐）
            >>> for category in client.category.iter(
            ...     workspace_id="123",
            ...     enabled=EnabledStatus.ENABLED
            ... ):
            ...     print(f"{category.category_id}: {category.name}")
            ...     if some_condition:
            ...         break  # 可以随时中断
            >>>
            >>> # 获取所有未启用的类别
            >>> disabled_categories = list(
            ...     client.category.iter(workspace_id="123", enabled=EnabledStatus.DISABLED)
            ... )
            >>>
            >>> # 限制最大页数
            >>> for category in client.category.iter(
            ...     workspace_id="123",
            ...     max_pages=3
            ... ):
            ...     print(category.name)
            >>>
            >>> # 也支持直接使用字符串
            >>> for category in client.category.iter(workspace_id="123", enabled="1"):
            ...     print(category.name)
        """
        page = 1
        pages_fetched = 0

        while True:
            # 检查是否达到最大页数限制
            if max_pages is not None and pages_fetched >= max_pages:
                break

            # 获取当前页数据
            response = self.list(
                workspace_id=workspace_id,
                page=page,
                page_size=page_size,
                enabled=enabled
            )

            # 逐个yield类别
            for category in response.categories:
                yield category

            # 检查是否还有下一页
            if page * page_size >= response.total:
                break

            page += 1
            pages_fetched += 1

    def _validate_category_id(self, category_id: str) -> None:
        """校验类别 ID"""
        if not category_id:
            raise ValidationError(
                "类别 ID 不能为空",
                i18n_key='error.category.id_empty'
            )
        if not category_id.isdigit():
            raise ValidationError(
                "类别 ID 必须是数字字符串",
                i18n_key='error.category.id_invalid'
            )


class CategoryTableResource(BaseResource):
    """
    类别表格操作

    Examples:
        >>> # 获取表格列表
        >>> tables = client.category.tables.list(
        ...     workspace_id="123",
        ...     category_id="456"
        ... )

        >>> # 新增表格
        >>> table = client.category.tables.add(
        ...     workspace_id="123",
        ...     category_id="456",
        ...     name="商品明细表"
        ... )
    """

    def list(self, workspace_id: str, category_id: str) -> TableListResponse:
        """
        获取表格列表

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID

        Returns:
            TableListResponse: 表格列表响应

        Examples:
            >>> tables = client.category.tables.list(
            ...     workspace_id="123",
            ...     category_id="456"
            ... )
            >>> for table in tables.tables:
            ...     print(f"{table.id}: {table.name}")
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        params = {"workspace_id": workspace_id, "category_id": category_id}

        response = self.http_client.get(
            f"{API_PREFIX}/category/tables/list", params=params
        )

        return TableListResponse.from_dict(response["result"])

    def add(
        self,
        workspace_id: str,
        category_id: str,
        name: str,
        prompt: Optional[str] = None,
        collect_from_multi_table: Optional[bool] = None,
        extract_model: Optional[Union[ExtractModel, str]] = None,
        **kwargs,
    ) -> TableAddResponse:
        """
        新增表格

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            name: 表格名称
            prompt: 表格语义抽取提示词（可选，最大200字符）
            collect_from_multi_table: 多表合并（可选）
            extract_model: 表格级别抽取模型（ExtractModel.Model_1/Model_2/Model_3，可选）
            **kwargs: 其他表格配置参数

        Returns:
            TableAddResponse: 包含新创建的表格 ID

        Examples:
            >>> from docflow import ExtractModel
            >>> table = client.category.tables.add(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     name="商品明细表",
            ...     prompt="请抽取每行的品名、数量和金额",
            ...     extract_model=ExtractModel.Model_1
            ... )
            >>> print(table.table_id)
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        if not name:
            raise ValidationError(
                "表格名称不能为空",
                i18n_key='error.table.name_empty'
            )

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "name": name,
        }

        if prompt is not None:
            payload["prompt"] = prompt

        if collect_from_multi_table is not None:
            payload["collect_from_multi_table"] = collect_from_multi_table

        if extract_model is not None:
            # 支持 ExtractModel 枚举和 str 类型
            extract_model_value = extract_model.value if isinstance(extract_model, ExtractModel) else extract_model
            if extract_model_value not in ("Model 1", "Model 2", "Model 3"):
                raise ValidationError(
                    "extract_model 必须是 ExtractModel.Model_1/Model_2/Model_3 或对应的字符串",
                    i18n_key='error.table.extract_model_invalid'
                )
            payload["extract_model"] = extract_model_value

        payload.update(kwargs)

        response = self.http_client.post(
            f"{API_PREFIX}/category/tables/add", json_data=payload
        )

        return TableAddResponse.from_dict(response["result"])

    def update(
        self,
        workspace_id: str,
        category_id: str,
        table_id: str,
        collect_from_multi_table: bool,
        name: Optional[str] = None,
        prompt: Optional[str] = None,
        extract_model: Optional[Union[ExtractModel, str]] = None,
        **kwargs,
    ) -> None:
        """
        更新表格

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            table_id: 表格 ID
            collect_from_multi_table: 多表合并（必填）
            name: 新的表格名称（可选，最大50字符）
            prompt: 新的表格语义抽取提示词（可选，最大200字符）
            extract_model: 表格级别抽取模型（ExtractModel.Model_1/Model_2/Model_3，可选）
            **kwargs: 其他要更新的字段

        Examples:
            >>> from docflow import ExtractModel
            >>> client.category.tables.update(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     table_id="789",
            ...     collect_from_multi_table=True,
            ...     name="更新后的表格名称",
            ...     extract_model=ExtractModel.Model_2
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")
        self._validate_id(table_id, "表格 ID")

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "table_id": table_id,
            "collect_from_multi_table": collect_from_multi_table,
        }

        if name is not None:
            if not name:
                raise ValidationError(
                "表格名称不能为空",
                i18n_key='error.table.name_empty'
            )
            payload["name"] = name

        if prompt is not None:
            payload["prompt"] = prompt

        if extract_model is not None:
            # 支持 ExtractModel 枚举和 str 类型
            extract_model_value = extract_model.value if isinstance(extract_model, ExtractModel) else extract_model
            if extract_model_value not in ("Model 1", "Model 2", "Model 3"):
                raise ValidationError(
                    "extract_model 必须是 ExtractModel.Model_1/Model_2/Model_3 或对应的字符串",
                    i18n_key='error.table.extract_model_invalid'
                )
            payload["extract_model"] = extract_model_value

        payload.update(kwargs)

        self.http_client.post(
            f"{API_PREFIX}/category/tables/update", json_data=payload
        )

    def delete(
        self, workspace_id: str, category_id: str, table_ids: List[str]
    ) -> None:
        """
        批量删除表格

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            table_ids: 要删除的表格 ID 列表

        Examples:
            >>> client.category.tables.delete(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     table_ids=["789", "101"]
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        if not table_ids:
            raise ValidationError(
                "table_ids 不能为空",
                i18n_key='error.table.delete_list_empty'
            )

        for table_id in table_ids:
            self._validate_id(table_id, "表格 ID")

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "table_ids": table_ids,
        }

        self.http_client.post(
            f"{API_PREFIX}/category/tables/delete", json_data=payload
        )


class CategoryFieldResource(BaseResource):
    """
    类别字段操作

    Examples:
        >>> # 获取字段列表
        >>> fields = client.category.fields.list(
        ...     workspace_id="123",
        ...     category_id="456"
        ... )

        >>> # 新增字段
        >>> field = client.category.fields.add(
        ...     workspace_id="123",
        ...     category_id="456",
        ...     name="金额"
        ... )
    """

    def list(self, workspace_id: str, category_id: str) -> FieldListResponse:
        """
        获取字段列表

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID

        Returns:
            FieldListResponse: 字段列表响应

        Examples:
            >>> fields = client.category.fields.list(
            ...     workspace_id="123",
            ...     category_id="456"
            ... )
            >>> for field in fields.fields:
            ...     print(f"{field.id}: {field.name}")
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        params = {"workspace_id": workspace_id, "category_id": category_id}

        response = self.http_client.get(
            f"{API_PREFIX}/category/fields/list", params=params
        )

        return FieldListResponse.from_dict(response["result"])

    def add(
        self,
        workspace_id: str,
        category_id: str,
        name: str,
        description: Optional[str] = None,
        table_id: Optional[str] = None,
        extract_model: Optional[Union[ExtractModel, str]] = None,
        **kwargs,
    ) -> FieldAddResponse:
        """
        新增字段

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            name: 字段名称
            description: 字段描述（可选）
            table_id: 字段所属表格id（可选）
            extract_model: 字段级别抽取模型（ExtractModel.Model_1/Model_2/Model_3，可选，仅支持普通字段）
            **kwargs: 其他字段配置参数，如：
                - prompt: 语义抽取提示词
                - use_prompt: 是否使用语义提示词
                - alias: 字段别名列表
                - identity: 导出字段名
                - multi_value: 是否多值抽取
                - duplicate_value_distinct: 是否重复值去重
                - transform_settings: 转换配置（字典），包含：
                    - type: 转换类型（FieldType 枚举，如 FieldType.DATETIME）
                    - datetime_settings: 时间类型转换配置
                    - enumerate_settings: 枚举类型转换配置
                    - regex_settings: 正则类型转换配置
                    - mismatch_action: 不匹配时的处理动作

        Returns:
            FieldAddResponse: 包含新创建的字段 ID

        Examples:
            >>> from docflow import FieldType, MismatchAction, ExtractModel
            >>>
            >>> # 创建基础字段
            >>> field = client.category.fields.add(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     name="发票号码",
            ...     description="发票唯一标识",
            ...     extract_model=ExtractModel.Model_1
            ... )
            >>>
            >>> # 创建带日期时间转换的字段
            >>> field = client.category.fields.add(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     name="开票日期",
            ...     transform_settings={
            ...         "type": FieldType.DATETIME.value,
            ...         "datetime_settings": {
            ...             "format": "yyyy-MM-dd"
            ...         }
            ...     }
            ... )
            >>>
            >>> # 创建带枚举转换的字段
            >>> field = client.category.fields.add(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     name="发票类型",
            ...     transform_settings={
            ...         "type": FieldType.ENUMERATE.value,
            ...         "enumerate_settings": {
            ...             "items": ["增值税专用发票", "增值税普通发票"]
            ...         },
            ...         "mismatch_action": {
            ...             "mode": MismatchAction.WARNING.value
            ...         }
            ...     },
            ...     extract_model=ExtractModel.Model_2
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        if not name:
            raise ValidationError(
                "字段名称不能为空",
                i18n_key='error.field.name_empty'
            )

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "name": name,
        }

        if description:
            payload["description"] = description

        if table_id:
            payload["table_id"] = table_id

        if extract_model is not None:
            # 支持 ExtractModel 枚举和 str 类型
            extract_model_value = extract_model.value if isinstance(extract_model, ExtractModel) else extract_model
            if extract_model_value not in ("Model 1", "Model 2", "Model 3"):
                raise ValidationError(
                    "extract_model 必须是 ExtractModel.Model_1/Model_2/Model_3 或对应的字符串",
                    i18n_key='error.field.extract_model_invalid'
                )
            payload["extract_model"] = extract_model_value

        payload.update(kwargs)

        response = self.http_client.post(
            f"{API_PREFIX}/category/fields/add", json_data=payload
        )

        return FieldAddResponse.from_dict(response["result"])

    def get_config(
        self, workspace_id: str, category_id: str, field_id: str
    ) -> FieldConfigResponse:
        """
        获取字段高级配置

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            field_id: 字段 ID

        Returns:
            FieldConfigResponse: 字段配置响应

        Examples:
            >>> config = client.category.fields.get_config(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     field_id="789"
            ... )
            >>> print(config.config)
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")
        self._validate_id(field_id, "字段 ID")

        params = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "field_id": field_id,
        }

        response = self.http_client.get(
            f"{API_PREFIX}/category/fields/config", params=params
        )

        return FieldConfigResponse.from_dict(response["result"])

    def update(
        self,
        workspace_id: str,
        category_id: str,
        field_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        table_id: Optional[str] = None,
        extract_model: Optional[Union[ExtractModel, str]] = None,
        **kwargs,
    ) -> None:
        """
        更新字段

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            field_id: 字段 ID
            name: 新的字段名称（可选）
            description: 新的描述（可选）
            table_id: 字段所属表格id（可选）
            extract_model: 字段级别抽取模型（ExtractModel.Model_1/Model_2/Model_3，可选）
            **kwargs: 其他要更新的字段配置参数，如：
                - prompt: 语义抽取提示词
                - use_prompt: 是否使用语义提示词
                - alias: 字段别名列表
                - transform_settings: 转换配置（字典）

        Examples:
            >>> from docflow import FieldType, ExtractModel
            >>> # 更新字段基本信息
            >>> client.category.fields.update(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     field_id="789",
            ...     name="更新后的字段名",
            ...     extract_model=ExtractModel.Model_2
            ... )
            >>>
            >>> # 更新字段转换配置
            >>> client.category.fields.update(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     field_id="789",
            ...     transform_settings={
            ...         "type": FieldType.DATETIME.value,
            ...         "datetime_settings": {"format": "yyyy-MM-dd"}
            ...     }
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")
        self._validate_id(field_id, "字段 ID")

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "field_id": field_id,
        }

        if name is not None:
            if not name:
                raise ValidationError(
                "字段名称不能为空",
                i18n_key='error.field.name_empty'
            )
            payload["name"] = name

        if description is not None:
            payload["description"] = description

        if table_id is not None:
            payload["table_id"] = table_id

        if extract_model is not None:
            # 支持 ExtractModel 枚举和 str 类型
            extract_model_value = extract_model.value if isinstance(extract_model, ExtractModel) else extract_model
            if extract_model_value not in ("Model 1", "Model 2", "Model 3"):
                raise ValidationError(
                    "extract_model 必须是 ExtractModel.Model_1/Model_2/Model_3 或对应的字符串",
                    i18n_key='error.field.extract_model_invalid'
                )
            payload["extract_model"] = extract_model_value

        payload.update(kwargs)

        self.http_client.post(
            f"{API_PREFIX}/category/fields/update", json_data=payload
        )

    def delete(
        self, workspace_id: str, category_id: str, field_ids: List[str], table_id: Optional[str] = None
    ) -> None:
        """
        批量删除字段

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            field_ids: 要删除的字段 ID 列表

        Examples:
            >>> client.category.fields.delete(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     field_ids=["789", "101"]
            ...     table_id="498",
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        if not field_ids:
            raise ValidationError(
                "field_ids 不能为空",
                i18n_key='error.field.delete_list_empty'
            )

        for field_id in field_ids:
            self._validate_id(field_id, "字段 ID")

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "field_ids": field_ids,
        }

        if table_id is not None:
            payload["table_id"] = table_id

        self.http_client.post(
            f"{API_PREFIX}/category/fields/delete", json_data=payload
        )


class CategorySampleResource(BaseResource):
    """
    类别样本操作

    Examples:
        >>> # 上传样本
        >>> sample = client.category.samples.upload(
        ...     workspace_id="123",
        ...     category_id="456",
        ...     file="/path/to/sample.pdf"
        ... )

        >>> # 下载样本
        >>> file_data = client.category.samples.download(
        ...     workspace_id="123",
        ...     category_id="456",
        ...     sample_id="789",
        ...     save_path="/path/to/save"
        ... )
    """

    def upload(
        self, workspace_id: str, category_id: str, file: Union[str, BinaryIO]
    ) -> SampleUploadResponse:
        """
        上传样本文件

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            file: 文件路径或文件对象

        Returns:
            SampleUploadResponse: 包含上传的样本 ID

        Examples:
            >>> # 使用文件路径
            >>> sample = client.category.samples.upload(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     file="/path/to/sample.pdf"
            ... )

            >>> # 使用文件对象
            >>> with open("/path/to/sample.pdf", "rb") as f:
            ...     sample = client.category.samples.upload(
            ...         workspace_id="123",
            ...         category_id="456",
            ...         file=f
            ...     )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        data = {"workspace_id": workspace_id, "category_id": category_id}

        # 准备文件
        files = [FileHandler.prepare_file(file, field_name="file")]

        response = self.http_client.request(
            method="POST",
            path=f"{API_PREFIX}/category/sample/upload",
            files=files,
            data=data,
        )

        return SampleUploadResponse.from_dict(response["result"])

    def list(
        self,
        workspace_id: str,
        category_id: str,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> SampleListResponse:
        """
        获取样本列表

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            page: 页码，从 1 开始，默认 1
            page_size: 每页数量，默认 20，最大 100

        Returns:
            SampleListResponse: 样本列表响应

        Examples:
            >>> samples = client.category.samples.list(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     page=1,
            ...     page_size=20
            ... )
            >>> for sample in samples.samples:
            ...     print(f"{sample.sample_id}: {sample.file_name}")
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")
        self._validate_page_params(page, page_size)

        params = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "page": page,
            "page_size": page_size,
        }

        response = self.http_client.get(
            f"{API_PREFIX}/category/sample/list", params=params
        )

        return SampleListResponse.from_dict(response["result"])

    def download(
        self,
        workspace_id: str,
        category_id: str,
        sample_id: str,
        save_path: Optional[str] = None,
    ) -> Union[bytes, Tuple[bytes, str]]:
        """
        下载样本文件

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            sample_id: 样本 ID
            save_path: 保存目录路径（可选）。如果提供，文件将保存到该目录，文件名从响应头获取

        Returns:
            Union[bytes, Tuple[bytes, str]]:
                - 如果提供了 save_path: 返回文件字节数据
                - 如果未提供 save_path: 返回 (文件字节数据, 文件名) 元组

        Examples:
            >>> # 下载并保存到指定目录
            >>> client.category.samples.download(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     sample_id="789",
            ...     save_path="/path/to/directory"
            ... )
            >>> # 文件将保存为 /path/to/directory/原始文件名.ext

            >>> # 下载到内存并获取文件名
            >>> file_data, filename = client.category.samples.download(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     sample_id="789"
            ... )
            >>> print(f"Downloaded: {filename}")
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")
        self._validate_id(sample_id, "样本 ID")

        params = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "sample_id": sample_id,
        }

        # 使用特殊的下载方法（返回 bytes 而不是 JSON）
        url = f"{self.http_client.base_url}{API_PREFIX}/category/sample/download"
        headers = self.http_client._build_headers()

        response = self.http_client.session.get(
            url,
            params=params,
            headers=headers,
            timeout=self.http_client.config.timeout,
            stream=True,
        )

        response.raise_for_status()

        # 从响应头中提取文件名
        # 如果提取失败，会先检查响应体是否包含业务错误
        filename = self._extract_filename_from_headers(response.headers, response)

        file_data = response.content

        # 如果提供了保存路径，保存文件
        if save_path:
            # save_path 是目录路径，使用提取的文件名
            full_path = os.path.join(save_path, filename)
            with open(full_path, "wb") as f:
                f.write(file_data)
            return file_data
        else:
            # 未提供路径，返回数据和文件名
            return file_data, filename

    def _extract_filename_from_headers(self, headers: Dict[str, str], response) -> str:
        """
        从响应头 Content-Disposition 中提取文件名并解码

        Args:
            headers: 响应头字典
            response: HTTP 响应对象（用于检查业务错误）

        Returns:
            str: 解码后的文件名

        Raises:
            APIError: 响应体中包含业务错误
            ValidationError: 响应头中缺少 Content-Disposition 或无法提取文件名

        Examples:
            Content-Disposition: attachment; filename="%E6%9C%BA%E6%89%93%E5%8F%91%E7%A5%A8.jpeg"; filename*=UTF-8''%E6%9C%BA%E6%89%93%E5%8F%91%E7%A5%A8.jpeg
            -> 机打发票.jpeg
        """
        content_disposition = headers.get('Content-Disposition', '')

        if not content_disposition:
            # 在抛出异常前，先检查响应体是否包含业务错误
            self._check_response_body_error(response)

            raise ValidationError(
                "响应头中缺少 Content-Disposition，无法获取文件名",
                i18n_key='error.sample.missing_content_disposition'
            )

        # 优先使用 filename* (RFC 5987)，支持 UTF-8 编码
        # 格式: filename*=UTF-8''%E6%9C%BA%E6%89%93%E5%8F%91%E7%A5%A8.jpeg
        filename_star_match = re.search(r"filename\*=UTF-8''([^;]+)", content_disposition)
        if filename_star_match:
            encoded_filename = filename_star_match.group(1).strip()
            try:
                # URL decode
                return unquote(encoded_filename)
            except Exception:
                pass

        # 其次使用 filename
        # 格式: filename="%E6%9C%BA%E6%89%93%E5%8F%91%E7%A5%A8.jpeg" 或 filename="file.pdf"
        filename_match = re.search(r'filename="?([^";]+)"?', content_disposition)
        if filename_match:
            encoded_filename = filename_match.group(1).strip().strip('"')
            try:
                # URL decode
                return unquote(encoded_filename)
            except Exception:
                # 如果解码失败，返回原始值
                return encoded_filename

        # 如果都没有，先检查响应体是否包含业务错误
        self._check_response_body_error(response)

        # 如果不是业务错误，抛出文件名提取失败的异常
        raise ValidationError(
            "无法从 Content-Disposition 中提取文件名",
            i18n_key='error.sample.cannot_extract_filename'
        )

    def _check_response_body_error(self, response):
        """
        检查响应体是否包含业务错误

        Args:
            response: HTTP 响应对象

        Raises:
            APIError: 响应体中 code != 200
        """
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
        except (ValueError, KeyError):
            # 如果不是 JSON 响应或缺少必要字段，忽略
            pass

    def _decode_msg(self, msg: str) -> str:
        """
        解码 UTF-8 编码的错误消息

        Args:
            msg: 可能是 UTF-8 编码序列的字符串

        Returns:
            str: 解码后的字符串
        """
        if not msg:
            return msg

        try:
            # 尝试将 latin-1 编码的字符串转换为 utf-8
            return msg.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
            # 如果解码失败，说明消息本身就是正常的字符串，直接返回
            return msg

    def delete(
        self, workspace_id: str, category_id: str, sample_ids: List[str]
    ) -> None:
        """
        批量删除样本

        Args:
            workspace_id: 工作空间 ID
            category_id: 类别 ID
            sample_ids: 要删除的样本 ID 列表

        Examples:
            >>> client.category.samples.delete(
            ...     workspace_id="123",
            ...     category_id="456",
            ...     sample_ids=["789", "101"]
            ... )
        """
        # 参数校验
        self._validate_workspace_id(workspace_id)
        self._validate_id(category_id, "类别 ID")

        if not sample_ids:
            raise ValidationError(
                "sample_ids 不能为空",
                i18n_key='error.sample.delete_list_empty'
            )

        for sample_id in sample_ids:
            self._validate_id(sample_id, "样本 ID")

        payload = {
            "workspace_id": workspace_id,
            "category_id": category_id,
            "sample_ids": sample_ids,
        }

        self.http_client.post(
            f"{API_PREFIX}/category/sample/delete", json_data=payload
        )
