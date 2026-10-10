"""
工作空间相关数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict


@dataclass
class WorkspaceInfo:
    """工作空间信息"""

    workspace_id: str
    name: str
    auth_scope: Optional[int] = None
    description: Optional[str] = None
    manage_account_id: Optional[str] = None
    manage_account_name: Optional[str] = None
    callback_url: Optional[str] = None
    callback_retry_time: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceInfo":
        """从字典创建对象"""
        manage_account_id = data.get("manage_account_id", data.get("manageAccountId"))
        return cls(
            workspace_id=str(data.get("workspace_id", data.get("workspaceId", ""))),
            name=data.get("name", ""),
            auth_scope=data.get("auth_scope", data.get("authScope")),
            description=data.get("description"),
            manage_account_id=str(manage_account_id) if manage_account_id is not None else None,
            manage_account_name=data.get("manage_account_name", data.get("manageAccountName")),
            callback_url=data.get("callback_url", data.get("callbackUrl")),
            callback_retry_time=data.get("callback_retry_time", data.get("callbackRetryTime")),
        )


@dataclass
class WorkspaceCreateResponse:
    """创建工作空间响应"""

    workspace_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceCreateResponse":
        """从字典创建对象"""
        return cls(
            workspace_id=str(data.get("workspace_id", data.get("workspaceId", "")))
        )


@dataclass
class WorkspaceListResponse:
    """工作空间列表响应"""

    total: int
    page: int
    page_size: int
    workspaces: List[WorkspaceInfo]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceListResponse":
        """从字典创建对象"""
        workspaces_data = data.get("workspaces", data.get("list", []))
        workspaces = [WorkspaceInfo.from_dict(ws) for ws in workspaces_data]

        return cls(
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", data.get("pageSize", 20)),
            workspaces=workspaces,
        )


@dataclass
class WorkspaceDetailResponse:
    """工作空间详情响应"""

    workspace_id: str
    name: str
    auth_scope: Optional[int] = None
    description: Optional[str] = None
    manage_account_id: Optional[str] = None
    manage_account_name: Optional[str] = None
    callback_url: Optional[str] = None
    callback_retry_time: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceDetailResponse":
        """从字典创建对象"""
        manage_account_id = data.get("manage_account_id", data.get("manageAccountId"))
        return cls(
            workspace_id=str(data.get("workspace_id", data.get("workspaceId", ""))),
            name=data.get("name", ""),
            auth_scope=data.get("auth_scope", data.get("authScope")),
            description=data.get("description"),
            manage_account_id=str(manage_account_id) if manage_account_id is not None else None,
            manage_account_name=data.get("manage_account_name", data.get("manageAccountName")),
            callback_url=data.get("callback_url", data.get("callbackUrl")),
            callback_retry_time=data.get("callback_retry_time", data.get("callbackRetryTime")),
        )


@dataclass
class SplitConfigResponse:
    """工作空间或类别的拆套配置。"""

    workspace_id: str
    scope: str
    rule_mode: str
    rule_order: List[str] = field(default_factory=list)
    constraint: str = "none"
    llm_prompt_mode: str = "default"
    category_id: Optional[str] = None
    llm_prompt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SplitConfigResponse":
        """从 API 的 snake_case 响应构造配置模型。"""
        category_id = data.get("category_id")
        return cls(
            workspace_id=str(data.get("workspace_id", "")),
            scope=data.get("scope", ""),
            category_id=str(category_id) if category_id is not None else None,
            rule_mode=data.get("rule_mode", ""),
            rule_order=list(data.get("rule_order") or []),
            constraint=data.get("constraint", "none"),
            llm_prompt_mode=data.get("llm_prompt_mode", "default"),
            llm_prompt=data.get("llm_prompt"),
        )
