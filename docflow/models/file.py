"""
文件处理相关数据模型
"""
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
from .._constants import DEFAULT_PAGE, MAX_PAGE_SIZE
from ._base import ForwardCompatibleModel


@dataclass
class FileInfo(ForwardCompatibleModel):
    """文件信息"""
    id: str
    name: str
    format: str
    task_id: Optional[str] = None
    category: Optional[str] = None
    recognition_status: Optional[int] = None
    verification_status: Optional[int] = None
    data: Optional[Dict[str, Any]] = None  # 抽取结果（字段/表格）。字段/表格项含 extractModel(实际命中模型)、configModel(配置模型，Auto 场景为 "Auto")、hitModelReason(命中原因)
    task_detail_url: Optional[str] = None
    document: Optional[Dict[str, Any]] = None
    task_type: Optional[str] = None
    batch_number: Optional[str] = None
    pages: Optional[List[Dict[str, Any]]] = None
    failure_causes: Optional[str] = None
    duration_ms: Optional[int] = None
    total_page_num: Optional[int] = None
    parsedDetail: Optional[Dict[str, Any]] = None
    child_files: Optional[List[Dict[str, Any]]] = None
    parser_params: Optional[Dict[str, Any]] = None


@dataclass
class FileUploadResponse(ForwardCompatibleModel):
    """文件上传响应"""
    batch_number: str
    files: List[FileInfo] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.files, list):
            self.files = [
                FileInfo.from_dict(f) if isinstance(f, dict) else f
                for f in self.files
            ]


@dataclass
class FileFetchResponse(ForwardCompatibleModel):
    """文件查询响应"""
    files: List[FileInfo] = field(default_factory=list)
    total: int = 0
    page: int = DEFAULT_PAGE
    page_size: int = MAX_PAGE_SIZE

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.files, list):
            self.files = [
                FileInfo.from_dict(f) if isinstance(f, dict) else f
                for f in self.files
            ]


@dataclass
class FileTranslateField(ForwardCompatibleModel):
    """普通字段或表格单元格翻译结果"""
    key: Optional[str] = None
    translated_key: Optional[str] = None
    index: Optional[int] = None
    value: Optional[str] = None


@dataclass
class FileTranslateTableHeader(ForwardCompatibleModel):
    """表头翻译结果"""
    key: Optional[str] = None
    translated_key: Optional[str] = None


@dataclass
class FileTranslateTable(ForwardCompatibleModel):
    """表格翻译结果"""
    table_name: Optional[str] = None
    translated_table_name: Optional[str] = None
    items: List[List[FileTranslateField]] = field(default_factory=list)
    item_headers: List[FileTranslateTableHeader] = field(default_factory=list)

    def __post_init__(self):
        """将嵌套表格结果转换为可访问的数据模型"""
        self.items = [
            [
                FileTranslateField.from_dict(item) if isinstance(item, dict) else item
                for item in (row or [])
            ]
            for row in (self.items or [])
        ]
        self.item_headers = [
            FileTranslateTableHeader.from_dict(item) if isinstance(item, dict) else item
            for item in (self.item_headers or [])
        ]


@dataclass
class FileTranslateStamp(ForwardCompatibleModel):
    """印章翻译结果"""
    key: Optional[str] = None
    page: Optional[int] = None
    index: Optional[int] = None
    stamp_prefix: Optional[str] = None
    type_key: Optional[str] = None
    type: Optional[str] = None
    color_key: Optional[str] = None
    color: Optional[str] = None
    stamp_shape_key: Optional[str] = None
    stamp_shape: Optional[str] = None
    value_key: Optional[str] = None
    value: Optional[str] = None


@dataclass
class FileTranslateHandwriting(ForwardCompatibleModel):
    """手写体翻译结果"""
    key: Optional[str] = None
    page: Optional[int] = None
    index: Optional[int] = None
    handwriting_prefix: Optional[str] = None
    text: Optional[str] = None


@dataclass
class FileTranslateResponse(ForwardCompatibleModel):
    """文件翻译响应"""
    fields: List[FileTranslateField] = field(default_factory=list)
    tables: List[FileTranslateTable] = field(default_factory=list)
    stamps: List[FileTranslateStamp] = field(default_factory=list)
    handwritings: List[FileTranslateHandwriting] = field(default_factory=list)

    def __post_init__(self):
        """将四类翻译结果转换为对应的数据模型"""
        self.fields = [
            FileTranslateField.from_dict(item) if isinstance(item, dict) else item
            for item in (self.fields or [])
        ]
        self.tables = [
            FileTranslateTable.from_dict(item) if isinstance(item, dict) else item
            for item in (self.tables or [])
        ]
        self.stamps = [
            FileTranslateStamp.from_dict(item) if isinstance(item, dict) else item
            for item in (self.stamps or [])
        ]
        self.handwritings = [
            FileTranslateHandwriting.from_dict(item) if isinstance(item, dict) else item
            for item in (self.handwritings or [])
        ]


@dataclass
class FileUpdateInfo(ForwardCompatibleModel):
    """文件更新信息"""
    workspace_id: str
    id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileUpdateInfo":
        """从字典创建对象"""
        normalized_data = dict(data)
        normalized_data["workspace_id"] = data.get("workspace_id", "")
        normalized_data["id"] = data.get("id") or data.get("file_id", "")
        return super().from_dict(normalized_data)



@dataclass
class FileUpdateResponse(ForwardCompatibleModel):
    """文件更新响应"""
    files: List[FileUpdateInfo] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.files, list):
            self.files = [
                FileUpdateInfo.from_dict(f) if isinstance(f, dict) else f
                for f in self.files
            ]


@dataclass
class FileDeleteResponse(ForwardCompatibleModel):
    """文件删除响应"""
    deleted_count: int = 0
