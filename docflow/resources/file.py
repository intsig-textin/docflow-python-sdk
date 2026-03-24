"""
文件处理资源类
"""
from typing import Optional, List, Dict, Any, Iterator, Union
from .base import BaseResource
from ..models.file import (
    FileUploadResponse,
    FileFetchResponse,
    FileUpdateResponse,
    FileDeleteResponse
)
from .._constants import DEFAULT_PAGE, MAX_PAGE_SIZE, API_PREFIX
from ..exceptions import ValidationError


class FileResource(BaseResource):
    """
    文件处理资源类

    提供文件上传、查询、更新、删除等功能
    """

    def upload(
        self,
        workspace_id: str,
        category: Optional[str] = None,
        file_path: Optional[str] = None,
        file_urls: Optional[List[str]] = None,
        batch_number: Optional[str] = None,
        auto_verify_vat: Optional[bool] = None,
        split_flag: Optional[bool] = None,
        crop_flag: Optional[bool] = None,
        target_process: Optional[str] = None,
        parser_remove_watermark: Optional[bool] = None,
        parser_crop_dewarp: Optional[bool] = None,
        parser_apply_merge: Optional[bool] = None,
        parser_formula_level: Optional[int] = None,
        parser_table_text_split_mode: Optional[str] = None,
    ) -> FileUploadResponse:
        """
        上传文件（异步）

        支持两种上传方式：
        1. 本地文件上传（multipart/form-data）：传入 file_path
        2. URL 上传（application/json）：传入 file_urls

        Args:
            workspace_id: 空间ID
            category: 文件类别
            file_path: 本地文件路径（可选，与 file_urls 二选一）
            file_urls: 文件URL列表（可选，与 file_path 二选一，最多10个）
            batch_number: 批次编号（可选）
            auto_verify_vat: 是否自动核验增值税发票
            split_flag: 是否启用文档拆分
            crop_flag: 是否启用多图切分
            target_process: 处理目标（recognition, classification）
            parser_remove_watermark: 是否移除水印
            parser_crop_dewarp: 是否裁剪和去畸变
            parser_apply_merge: 是否应用合并
            parser_formula_level: 公式识别级别
            parser_table_text_split_mode: 表格文字分割模式

        Returns:
            FileUploadResponse: 上传响应

        Raises:
            ValidationError: 参数校验失败

        Examples:
            >>> # 方式1：上传本地文件
            >>> response = client.file.upload(
            ...     workspace_id="123",
            ...     category="发票",
            ...     file_path="/path/to/invoice.pdf"
            ... )
            >>>
            >>> # 方式2：通过URL上传
            >>> response = client.file.upload(
            ...     workspace_id="123",
            ...     category="发票",
            ...     file_urls=["https://example.com/invoice.pdf"]
            ... )
        """
        # 参数校验：file_path 和 file_urls 必须二选一
        if file_path is None and file_urls is None:
            raise ValidationError(
                "file_path 和 file_urls 必须提供其中之一",
                i18n_key='error.file.upload_source_required'
            )

        if file_path is not None and file_urls is not None:
            raise ValidationError(
                "file_path 和 file_urls 不能同时提供",
                i18n_key='error.file.upload_source_conflict'
            )

        # 校验 file_urls
        if file_urls is not None:
            if not file_urls:
                raise ValidationError(
                    "file_urls 不能为空列表",
                    i18n_key='error.file.urls_empty'
                )
            if len(file_urls) > 10:
                raise ValidationError(
                    "file_urls 最多支持 10 个 URL",
                    i18n_key='error.file.urls_too_many',
                    max_count=10
                )

        params = {
            "workspace_id": workspace_id,
            "category": category,
        }

        # 添加可选参数
        if batch_number is not None:
            params["batch_number"] = batch_number
        if auto_verify_vat is not None:
            params["auto_verify_vat"] = auto_verify_vat
        if split_flag is not None:
            params["split_flag"] = split_flag
        if crop_flag is not None:
            params["crop_flag"] = crop_flag
        if target_process is not None:
            params["target_process"] = target_process
        if parser_remove_watermark is not None:
            params["parser_remove_watermark"] = parser_remove_watermark
        if parser_crop_dewarp is not None:
            params["parser_crop_dewarp"] = parser_crop_dewarp
        if parser_apply_merge is not None:
            params["parser_apply_merge"] = parser_apply_merge
        if parser_formula_level is not None:
            params["parser_formula_level"] = parser_formula_level
        if parser_table_text_split_mode is not None:
            params["parser_table_text_split_mode"] = parser_table_text_split_mode

        # 根据上传方式选择不同的请求方式
        if file_urls is not None:
            # 方式2：通过 URL 上传（application/json）
            response = self.http_client.post(
                f"{API_PREFIX}/file/upload",
                params=params,
                json_data={"urls": file_urls}
            )
        elif file_path is not None:
            # 方式1：本地文件上传（multipart/form-data）
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.http_client.post(
                    f"{API_PREFIX}/file/upload",
                    params=params,
                    files=files
                )
        else:
            # 这种情况不应该发生，因为前面已经校验过
            raise ValidationError(
                "file_path 和 file_urls 必须提供其中之一",
                i18n_key='error.file.upload_source_required'
            )

        return FileUploadResponse(**response['result'])

    def upload_sync(
        self,
        workspace_id: str,
        category: Optional[str] = None,
        file_path: Optional[str] = None,
        file_urls: Optional[List[str]] = None,
        batch_number: Optional[str] = None,
        auto_verify_vat: Optional[bool] = None,
        split_flag: Optional[bool] = None,
        crop_flag: Optional[bool] = None,
        target_process: Optional[str] = None,
        parser_remove_watermark: Optional[bool] = None,
        parser_crop_dewarp: Optional[bool] = None,
        parser_apply_merge: Optional[bool] = None,
        parser_formula_level: Optional[int] = None,
        parser_table_text_split_mode: Optional[str] = None,
        with_task_detail_url: Optional[bool] = None,
    ) -> FileFetchResponse:
        """
        同步上传文件（等待处理完成）

        支持两种上传方式：
        1. 本地文件上传（multipart/form-data）：传入 file_path
        2. URL 上传（application/json）：传入 file_urls

        Args:
            workspace_id: 空间ID
            category: 文件类别
            file_path: 本地文件路径（可选，与 file_urls 二选一）
            file_urls: 文件URL列表（可选，与 file_path 二选一，最多10个）
            batch_number: 批次编号（可选）
            auto_verify_vat: 是否自动核验增值税发票
            split_flag: 是否启用文档拆分
            crop_flag: 是否启用多图切分
            target_process: 处理目标（recognition, classification）
            parser_remove_watermark: 是否移除水印
            parser_crop_dewarp: 是否裁剪和去畸变
            parser_apply_merge: 是否应用合并
            parser_formula_level: 公式识别级别
            parser_table_text_split_mode: 表格文字分割模式
            with_task_detail_url: 是否返回任务详情页URL

        Returns:
            FileFetchResponse: 处理结果

        Raises:
            ValidationError: 参数校验失败

        Examples:
            >>> # 方式1：上传本地文件并等待处理
            >>> result = client.file.upload_sync(
            ...     workspace_id="123",
            ...     category="发票",
            ...     file_path="/path/to/invoice.pdf"
            ... )
            >>>
            >>> # 方式2：通过URL上传并等待处理
            >>> result = client.file.upload_sync(
            ...     workspace_id="123",
            ...     category="发票",
            ...     file_urls=["https://example.com/invoice.pdf"]
            ... )
        """
        # 参数校验：file_path 和 file_urls 必须二选一
        if file_path is None and file_urls is None:
            raise ValidationError(
                "file_path 和 file_urls 必须提供其中之一",
                i18n_key='error.file.upload_source_required'
            )

        if file_path is not None and file_urls is not None:
            raise ValidationError(
                "file_path 和 file_urls 不能同时提供",
                i18n_key='error.file.upload_source_conflict'
            )

        # 校验 file_urls
        if file_urls is not None:
            if not file_urls:
                raise ValidationError(
                    "file_urls 不能为空列表",
                    i18n_key='error.file.urls_empty'
                )
            if len(file_urls) > 10:
                raise ValidationError(
                    "file_urls 最多支持 10 个 URL",
                    i18n_key='error.file.urls_too_many',
                    max_count=10
                )

        params = {
            "workspace_id": workspace_id,
            "category": category,
        }

        # 添加可选参数
        if batch_number is not None:
            params["batch_number"] = batch_number
        if auto_verify_vat is not None:
            params["auto_verify_vat"] = auto_verify_vat
        if split_flag is not None:
            params["split_flag"] = split_flag
        if crop_flag is not None:
            params["crop_flag"] = crop_flag
        if target_process is not None:
            params["target_process"] = target_process
        if parser_remove_watermark is not None:
            params["parser_remove_watermark"] = parser_remove_watermark
        if parser_crop_dewarp is not None:
            params["parser_crop_dewarp"] = parser_crop_dewarp
        if parser_apply_merge is not None:
            params["parser_apply_merge"] = parser_apply_merge
        if parser_formula_level is not None:
            params["parser_formula_level"] = parser_formula_level
        if parser_table_text_split_mode is not None:
            params["parser_table_text_split_mode"] = parser_table_text_split_mode
        if with_task_detail_url is not None:
            params["with_task_detail_url"] = with_task_detail_url

        # 根据上传方式选择不同的请求方式
        if file_urls is not None:
            # 方式2：通过 URL 上传（application/json）
            response = self.http_client.post(
                f"{API_PREFIX}/file/upload/sync",
                params=params,
                json_data={"urls": file_urls}
            )
        elif file_path is not None:
            # 方式1：本地文件上传（multipart/form-data）
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.http_client.post(
                    f"{API_PREFIX}/file/upload/sync",
                    params=params,
                    files=files
                )
        else:
            # 这种情况不应该发生，因为前面已经校验过
            raise ValidationError(
                "file_path 和 file_urls 必须提供其中之一",
                i18n_key='error.file.upload_source_required'
            )

        return FileFetchResponse(**response['result'])

    def fetch(
        self,
        workspace_id: str,
        page: int = DEFAULT_PAGE,
        page_size: int = MAX_PAGE_SIZE,
        batch_number: Optional[str] = None,
        file_id: Optional[str] = None,
        category: Optional[str] = None,
        recognition_status: Optional[str] = None,
        verification_status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        with_document: bool = False,
        with_task_detail_url: bool = False,
    ) -> FileFetchResponse:
        """
        获取文件处理结果列表

        Args:
            workspace_id: 空间ID
            page: 页码，默认1
            page_size: 每页数量，默认1000
            batch_number: 批次编号
            file_id: 文件ID
            category: 文件类别
            recognition_status: 识别状态（success, failed, processing）
            verification_status: 核对状态（0:待核对 2:已确认 3:已拒绝 4:已删除 5:推迟处理）
            start_time: 开始时间（RFC3339格式）
            end_time: 结束时间（RFC3339格式）
            with_document: 是否返回文档的全部文字识别结果
            with_task_detail_url: 是否返回任务详情页URL

        Returns:
            FileFetchResponse: 文件列表
        """
        params = {
            "workspace_id": workspace_id,
            "page": page,
            "page_size": page_size,
            "with_document": with_document,
            "with_task_detail_url": with_task_detail_url,
        }

        # 添加可选过滤条件
        if batch_number is not None:
            params["batch_number"] = batch_number
        if file_id is not None:
            params["file_id"] = file_id
        if category is not None:
            params["category"] = category
        if recognition_status is not None:
            params["recognition_status"] = recognition_status
        if verification_status is not None:
            params["verification_status"] = verification_status
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time

        response = self.http_client.get(
            f"{API_PREFIX}/file/fetch",
            params=params
        )

        return FileFetchResponse(**response['result'])

    def iter(
        self,
        workspace_id: str,
        batch_number: Optional[str] = None,
        category: Optional[str] = None,
        recognition_status: Optional[str] = None,
        verification_status: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        with_document: bool = False,
        with_task_detail_url: bool = False,
        page_size: int = MAX_PAGE_SIZE,
        max_pages: Optional[int] = None,
    ) -> Iterator[Any]:
        """
        迭代获取所有文件

        Args:
            workspace_id: 空间ID
            batch_number: 批次编号
            category: 文件类别
            recognition_status: 识别状态
            verification_status: 核对状态
            start_time: 开始时间
            end_time: 结束时间
            with_document: 是否返回文档的全部文字识别结果
            with_task_detail_url: 是否返回任务详情页URL
            page_size: 每页数量
            max_pages: 最大页数（可选，用于限制）

        Yields:
            文件信息对象
        """
        page = 1
        while True:
            if max_pages and page > max_pages:
                break

            response = self.fetch(
                workspace_id=workspace_id,
                page=page,
                page_size=page_size,
                batch_number=batch_number,
                category=category,
                recognition_status=recognition_status,
                verification_status=verification_status,
                start_time=start_time,
                end_time=end_time,
                with_document=with_document,
                with_task_detail_url=with_task_detail_url,
            )

            if not response.files:
                break

            for file in response.files:
                yield file

            # 判断是否还有下一页
            if page * page_size >= response.total:
                break

            page += 1

    def update(
        self,
        workspace_id: str,
        file_id: str,
        data: Dict[str, Any],
    ) -> FileUpdateResponse:
        """
        更新文件处理结果

        Args:
            workspace_id: 空间ID
            file_id: 文件ID
            data: 更新的数据（包含 fields 和 items）

        Returns:
            FileUpdateResponse: 更新响应
        """
        payload = [{
            "workspace_id": workspace_id,
            "file_id": file_id,
            "data": data
        }]

        response = self.http_client.post(
            f"{API_PREFIX}/file/update",
            json_data=payload
        )

        return FileUpdateResponse(**response['result'])

    def batch_update(
        self,
        updates: List[Dict[str, Any]],
    ) -> FileUpdateResponse:
        """
        批量更新文件处理结果

        Args:
            updates: 更新列表，每项包含 workspace_id, file_id, data

        Returns:
            FileUpdateResponse: 更新响应
        """
        response = self.http_client.post(
            f"{API_PREFIX}/file/update",
            json_data=updates
        )

        return FileUpdateResponse(**response['result'])

    def delete(
        self,
        workspace_id: str,
        batch_number: Optional[List[str]] = None,
        task_id: Optional[List[str]] = None,
        file_id: Optional[List[str]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> FileDeleteResponse:
        """
        删除文件

        Args:
            workspace_id: 空间ID
            batch_number: 批次编号列表
            task_id: 任务ID列表
            file_id: 文件ID列表
            start_time: 开始时间（Unix时间戳）
            end_time: 结束时间（Unix时间戳）

        Returns:
            FileDeleteResponse: 删除响应
        """
        payload = {
            "workspace_id": workspace_id
        }

        if batch_number is not None:
            payload["batch_number"] = batch_number
        if task_id is not None:
            payload["task_id"] = task_id
        if file_id is not None:
            payload["file_id"] = file_id
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time

        response = self.http_client.post(
            f"{API_PREFIX}/file/delete",
            json_data=payload
        )

        return FileDeleteResponse(**response['result'])

    def extract_fields(
        self,
        workspace_id: str,
        task_id: str,
        fields: Optional[List[Dict[str, str]]] = None,
        tables: Optional[List[Dict[str, Any]]] = None,
    ) -> FileFetchResponse:
        """
        抽取特定字段

        Args:
            workspace_id: 空间ID
            task_id: 任务ID
            fields: 字段列表，每项包含 key（字段名称）和 prompt（字段提示）
            tables: 表格列表，每项包含 name（表格名称）和 fields（字段列表）

        Returns:
            FileFetchResponse: 抽取结果

        Examples:
            >>> # 抽取额外的字段
            >>> result = client.file.extract_fields(
            ...     workspace_id="123",
            ...     task_id="456",
            ...     fields=[
            ...         {"key": "发票代码", "prompt": "只保留年的部分"},
            ...         {"key": "发票号码"}
            ...     ]
            ... )
            >>>
            >>> # 抽取表格字段
            >>> result = client.file.extract_fields(
            ...     workspace_id="123",
            ...     task_id="456",
            ...     tables=[
            ...         {
            ...             "name": "货物明细",
            ...             "fields": [
            ...                 {"key": "货物名称"},
            ...                 {"key": "数量"}
            ...             ]
            ...         }
            ...     ]
            ... )
        """
        payload = {
            "workspace_id": workspace_id,
            "task_id": task_id
        }

        if fields is not None:
            payload["fields"] = fields
        if tables is not None:
            payload["tables"] = tables

        response = self.http_client.post(
            f"{API_PREFIX}/file/extract_fields",
            json_data=payload
        )

        return FileFetchResponse(**response['result'])

    def retry(
        self,
        workspace_id: str,
        task_id: str,
        parser_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        重新处理文件

        Args:
            workspace_id: 空间ID
            task_id: 任务ID
            parser_params: 解析参数
        """
        payload = {
            "workspace_id": workspace_id,
            "task_id": task_id
        }

        if parser_params is not None:
            payload["parser_params"] = parser_params

        self.http_client.post(
            f"{API_PREFIX}/file/retry",
            json_data=payload
        )

    def amend_category(
        self,
        workspace_id: str,
        task_id: str,
        category: Optional[str] = None,
        split_tasks: Optional[List[Dict[str, Any]]] = None,
        crop_tasks: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        修改文件类别

        Args:
            workspace_id: 空间ID
            task_id: 任务ID
            category: 新文件类别（普通任务）
            split_tasks: 文档拆分任务列表
            crop_tasks: 多图切分任务列表
        """
        payload = {
            "workspace_id": workspace_id,
            "task_id": task_id
        }

        if category is not None:
            payload["category"] = category
        if split_tasks is not None:
            payload["split_tasks"] = split_tasks
        if crop_tasks is not None:
            payload["crop_tasks"] = crop_tasks

        self.http_client.post(
            f"{API_PREFIX}/file/amend_category",
            json_data=payload
        )
