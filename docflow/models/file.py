"""
文件处理相关数据模型
"""
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
from .._constants import DEFAULT_PAGE, MAX_PAGE_SIZE


@dataclass
class FileInfo:
    """文件信息"""
    id: str
    name: str
    format: str
    task_id: Optional[str] = None
    category: Optional[str] = None
    recognition_status: Optional[int] = None
    verification_status: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    task_detail_url: Optional[str] = None
    document: Optional[Dict[str, Any]] = None
    task_type: Optional[str] = None
    batch_number: Optional[str] = None
    pages: Optional[List[Dict[str, Any]]] = None
    failure_causes: Optional[List[str]] = None
    duration_ms: Optional[int] = None
    total_page_num: Optional[int] = None


@dataclass
class FileUploadResponse:
    """文件上传响应"""
    batch_number: str
    files: List[FileInfo] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.files, list):
            self.files = [
                FileInfo(**f) if isinstance(f, dict) else f
                for f in self.files
            ]


@dataclass
class FileFetchResponse:
    """文件查询响应"""
    files: List[FileInfo] = field(default_factory=list)
    total: int = 0
    page: int = DEFAULT_PAGE
    page_size: int = MAX_PAGE_SIZE

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.files, list):
            self.files = [
                FileInfo(**f) if isinstance(f, dict) else f
                for f in self.files
            ]


@dataclass
class FileUpdateInfo:
    """文件更新信息"""
    workspace_id: str
    id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileUpdateInfo":
        """从字典创建对象"""
        return cls(
            workspace_id=data.get("workspace_id", ""),
            id=data.get("id") or data.get("file_id", "")
        )



@dataclass
class FileUpdateResponse:
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
class FileDeleteResponse:
    """文件删除响应"""
    deleted_count: int = 0
