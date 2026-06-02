"""
类别相关数据模型

完整对应后端 Java VO 类的 Python 数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


def _get_first(data: Dict[str, Any], *keys):
    """从字典中按优先级取值，正确处理 False/0 等 falsy 值"""
    for k in keys:
        if k in data:
            return data[k]
    return None


# ==================== 类别模型 ====================

@dataclass
class CategoryInfo:
    """
    类别信息

    """
    id: str  # 类别ID (注意：后端使用 id 而不是 category_id)
    name: str
    description: Optional[str] = None   # 分类描述
    category_prompt: Optional[str] = None  # 用于分类的提示词
    extract_model: Optional[str] = None  # 抽取模型：Model 1/Model 2/Model 3/mixed
    enabled: Optional[int] = None  # 启用状态：0-禁用，1-启用，2-草稿

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CategoryInfo":
        """从字典创建对象"""
        return cls(
            id=str(data.get("id") or data.get("category_id") or data.get("categoryId")),
            name=data.get("name"),
            description=data.get("description"),
            category_prompt=data.get("category_prompt") or data.get("categoryPrompt"),
            extract_model=data.get("extract_model") or data.get("extractModel"),
            enabled=data.get("enabled"),
        )


@dataclass
class CategoryCreateResponse:
    """
    创建类别响应

    对应后端: CategoryCreateRespVO
    """
    category_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CategoryCreateResponse":
        """从字典创建对象"""
        return cls(
            category_id=str(data.get("categoryId") or data.get("category_id"))
        )


@dataclass
class CategoryListResponse:
    """
    类别列表响应

    对应后端: CategoryRespVO
    """
    total: int
    page: int
    page_size: int
    categories: List[CategoryInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CategoryListResponse":
        """从字典创建对象"""
        categories_data = data.get("categories") or data.get("list") or []
        categories = [CategoryInfo.from_dict(c) for c in categories_data]

        return cls(
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("pageSize") or data.get("page_size", 20),
            categories=categories,
        )


# ==================== 表格相关模型 ====================

@dataclass
class TableInfo:
    """
    表格信息

    """
    id: str  # 表格ID
    name: str
    prompt: Optional[str] = None  # 表格语义抽取提示词
    collect_from_multi_table: Optional[bool] = None  # 多表合并
    extract_model: Optional[str] = None # 抽取模型

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableInfo":
        """从字典创建对象"""
        return cls(
            id=str(data.get("id") or data.get("table_id") or data.get("tableId")),
            name=data.get("name"),
            prompt=data.get("prompt"),
            collect_from_multi_table=data.get("collectFromMultiTable") or data.get("collect_from_multi_table"),
            extract_model=data.get("extractModel") or data.get("extract_model"),
        )


@dataclass
class TableListResponse:
    """
    表格列表响应

    对应后端: ListCategoryTablesResVO
    """
    tables: List[TableInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableListResponse":
        """从字典创建对象"""
        tables_data = data.get("tables") or []
        tables = [TableInfo.from_dict(t) for t in tables_data]
        return cls(tables=tables)


@dataclass
class TableAddResponse:
    """
    新增表格响应（支持 with_detail 扩展字段）

    对应后端: CategoryTableAddRespVO
    """
    table_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    collect_from_multi_table: Optional[bool] = None
    extract_model: Optional[str] = None
    fields: Optional[List["FieldInfo"]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableAddResponse":
        """从字典创建对象"""
        fields_data = data.get("fields")
        fields_list = None
        if fields_data:
            fields_list = [FieldInfo.from_dict(f) for f in fields_data]

        return cls(
            table_id=str(data.get("tableId") or data.get("table_id")),
            name=data.get("name"),
            description=data.get("description"),
            prompt=data.get("prompt"),
            collect_from_multi_table=_get_first(data, "collect_from_multi_table", "collectFromMultiTable"),
            extract_model=_get_first(data, "extract_model", "extractModel"),
            fields=fields_list,
        )


# ==================== 字段相关模型 ====================

@dataclass
class FieldInfo:
    """
    字段信息

    对应 OpenAPI CategoryField schema (CategoryFieldConfig + id)
    """
    id: str  # 字段ID
    name: str
    description: Optional[str] = None
    prompt: Optional[str] = None  # 语义抽取提示词
    use_prompt: Optional[bool] = None  # 是否使用语义提示词
    alias: Optional[List[str]] = None  # 字段别名列表
    identity: Optional[str] = None  # 导出字段名
    multi_value: Optional[bool] = None  # 是否多值抽取
    duplicate_value_distinct: Optional[bool] = None  # 是否重复值去重
    transform_settings: Optional[Dict[str, Any]] = None  # 转换配置
    extract_model: Optional[str] = None # 抽取模型

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldInfo":
        """从字典创建对象"""
        return cls(
            id=str(data.get("id") or data.get("field_id") or data.get("fieldId")),
            name=data.get("name"),
            description=data.get("description"),
            prompt=data.get("prompt"),
            use_prompt=data.get("use_prompt") or data.get("usePrompt"),
            alias=data.get("alias"),
            identity=data.get("identity"),
            multi_value=data.get("multi_value") or data.get("multiValue"),
            duplicate_value_distinct=data.get("duplicate_value_distinct") or data.get("duplicateValueDistinct"),
            transform_settings=data.get("transform_settings") or data.get("transformSettings"),
            extract_model = data.get("extract_model") or data.get("extractModel")
        )


@dataclass
class TableWithFields:
    """
    包含字段的表格信息

    对应后端: ListCategoryFieldsResVO.Table
    """
    id: str  # 表格ID
    name: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    collect_from_multi_table: Optional[bool] = None
    fields: List[FieldInfo] = field(default_factory=list)
    extract_model: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableWithFields":
        """从字典创建对象"""
        fields_data = data.get("fields") or []
        fields = [FieldInfo.from_dict(f) for f in fields_data]

        return cls(
            id=str(data.get("id") or data.get("table_id") or data.get("tableId")),
            name=data.get("name"),
            description=data.get("description"),
            prompt=data.get("prompt"),
            collect_from_multi_table=_get_first(data, "collect_from_multi_table", "collectFromMultiTable"),
            fields=fields,
            extract_model=_get_first(data, "extract_model", "extractModel"),
        )


@dataclass
class FieldListResponse:
    """
    字段列表响应

    对应后端: ListCategoryFieldsResVO

    注意：后端返回的字段列表包含两部分：
    1. fields: 普通字段列表
    2. tables: 表格及其字段列表
    """
    fields: List[FieldInfo] = field(default_factory=list)
    tables: List[TableWithFields] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldListResponse":
        """从字典创建对象"""
        fields_data = data.get("fields") or []
        fields = [FieldInfo.from_dict(f) for f in fields_data]

        tables_data = data.get("tables") or []
        tables = [TableWithFields.from_dict(t) for t in tables_data]

        return cls(fields=fields, tables=tables)


@dataclass
class FieldAddResponse:
    """
    新增字段响应（支持 with_detail 扩展字段）

    对应后端: CategoryFieldAddRespVO
    """
    field_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    use_prompt: Optional[bool] = None
    alias: Optional[List[str]] = None
    identity: Optional[str] = None
    multi_value: Optional[bool] = None
    duplicate_value_distinct: Optional[bool] = None
    transform_settings: Optional[Dict[str, Any]] = None
    extract_model: Optional[str] = None
    enabled: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldAddResponse":
        """从字典创建对象"""
        return cls(
            field_id=str(data.get("fieldId") or data.get("field_id")),
            name=data.get("name"),
            description=data.get("description"),
            prompt=data.get("prompt"),
            use_prompt=_get_first(data, "use_prompt", "usePrompt"),
            alias=data.get("alias"),
            identity=data.get("identity"),
            multi_value=_get_first(data, "multi_value", "multiValue"),
            duplicate_value_distinct=_get_first(data, "duplicate_value_distinct", "duplicateValueDistinct"),
            transform_settings=_get_first(data, "transform_settings", "transformSettings"),
            extract_model=_get_first(data, "extract_model", "extractModel"),
            enabled=data.get("enabled"),
        )


# ==================== 字段配置相关模型 ====================

@dataclass
class MismatchAction:
    """
    不匹配处理动作

    对应后端: CategoryFieldConfigRespVO.MismatchAction
    """
    mode: Optional[str] = None  # "default" 或 "warning"
    default_value: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["MismatchAction"]:
        """从字典创建对象"""
        if not data:
            return None
        return cls(
            mode=data.get("mode"),
            default_value=data.get("defaultValue") or data.get("default_value"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        if self.mode:
            result["mode"] = self.mode
        if self.default_value:
            result["default_value"] = self.default_value
        return result


@dataclass
class TextSettings:
    """文本类型转换配置"""
    strip: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["TextSettings"]:
        if not data:
            return None
        return cls(strip=data.get("strip"))

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.strip:
            result["strip"] = self.strip
        return result


@dataclass
class NumberSettings:
    """数字类型转换配置"""
    format: Optional[str] = None  # "normal", "percentage", "chinese_amount"
    unit_remove: Optional[List[str]] = None
    simplified_chinese: Optional[str] = None
    simplified_english: Optional[str] = None
    decimal_places: Optional[int] = None
    omit_trailing_zeros: Optional[bool] = None
    thousand_separator: Optional[bool] = None
    chinese_case: Optional[str] = None  # "upper" 或 "lower"

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["NumberSettings"]:
        if not data:
            return None
        return cls(
            format=data.get("format"),
            unit_remove=data.get("unitRemove") or data.get("unit_remove"),
            simplified_chinese=data.get("simplifiedChinese") or data.get("simplified_chinese"),
            simplified_english=data.get("simplifiedEnglish") or data.get("simplified_english"),
            decimal_places=data.get("decimalPlaces") or data.get("decimal_places"),
            omit_trailing_zeros=data.get("omitTrailingZeros") or data.get("omit_trailing_zeros"),
            thousand_separator=data.get("thousandSeparator") or data.get("thousand_separator"),
            chinese_case=data.get("chineseCase") or data.get("chinese_case"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.format:
            result["format"] = self.format
        if self.unit_remove:
            result["unit_remove"] = self.unit_remove
        if self.simplified_chinese:
            result["simplified_chinese"] = self.simplified_chinese
        if self.simplified_english:
            result["simplified_english"] = self.simplified_english
        if self.decimal_places is not None:
            result["decimal_places"] = self.decimal_places
        if self.omit_trailing_zeros is not None:
            result["omit_trailing_zeros"] = self.omit_trailing_zeros
        if self.thousand_separator is not None:
            result["thousand_separator"] = self.thousand_separator
        if self.chinese_case:
            result["chinese_case"] = self.chinese_case
        return result


@dataclass
class DatetimeSettings:
    """时间类型转换配置"""
    format: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["DatetimeSettings"]:
        if not data:
            return None
        return cls(format=data.get("format"))

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.format:
            result["format"] = self.format
        return result


@dataclass
class EnumerateSettings:
    """枚举类型转换配置"""
    items: Optional[List[str]] = None
    mismatch_action: Optional[MismatchAction] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["EnumerateSettings"]:
        if not data:
            return None
        return cls(
            items=data.get("items"),
            mismatch_action=MismatchAction.from_dict(
                data.get("mismatchAction") or data.get("mismatch_action")
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.items:
            result["items"] = self.items
        if self.mismatch_action:
            result["mismatch_action"] = self.mismatch_action.to_dict()
        return result


@dataclass
class RegexSettings:
    """正则类型转换配置"""
    match: Optional[str] = None
    replace: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["RegexSettings"]:
        if not data:
            return None
        return cls(
            match=data.get("match"),
            replace=data.get("replace"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.match:
            result["match"] = self.match
        if self.replace:
            result["replace"] = self.replace
        return result


@dataclass
class TransformSettings:
    """
    转换配置

    对应后端: CategoryFieldConfigRespVO.TransformSettings
    """
    type: Optional[str] = None  # "text", "number", "datetime", "enumerate", "regex"
    text_settings: Optional[TextSettings] = None
    number_settings: Optional[NumberSettings] = None
    datetime_settings: Optional[DatetimeSettings] = None
    enumerate_settings: Optional[EnumerateSettings] = None
    regex_settings: Optional[RegexSettings] = None
    mismatch_action: Optional[MismatchAction] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["TransformSettings"]:
        """从字典创建对象"""
        if not data:
            return None
        return cls(
            type=data.get("type"),
            text_settings=TextSettings.from_dict(
                data.get("textSettings") or data.get("text_settings")
            ),
            number_settings=NumberSettings.from_dict(
                data.get("numberSettings") or data.get("number_settings")
            ),
            datetime_settings=DatetimeSettings.from_dict(
                data.get("datetimeSettings") or data.get("datetime_settings")
            ),
            enumerate_settings=EnumerateSettings.from_dict(
                data.get("enumerateSettings") or data.get("enumerate_settings")
            ),
            regex_settings=RegexSettings.from_dict(
                data.get("regexSettings") or data.get("regex_settings")
            ),
            mismatch_action=MismatchAction.from_dict(
                data.get("mismatchAction") or data.get("mismatch_action")
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        if self.type:
            result["type"] = self.type
        if self.text_settings:
            result["text_settings"] = self.text_settings.to_dict()
        if self.number_settings:
            result["number_settings"] = self.number_settings.to_dict()
        if self.datetime_settings:
            result["datetime_settings"] = self.datetime_settings.to_dict()
        if self.enumerate_settings:
            result["enumerate_settings"] = self.enumerate_settings.to_dict()
        if self.regex_settings:
            result["regex_settings"] = self.regex_settings.to_dict()
        if self.mismatch_action:
            result["mismatch_action"] = self.mismatch_action.to_dict()
        return result


@dataclass
class FieldConfigResponse:
    """
    字段配置响应

    对应后端: CategoryFieldConfigRespVO
    """
    field_id: str
    field_name: str
    alias: Optional[List[str]] = None  # 字段别名列表
    identity: Optional[str] = None  # 导出字段名
    multi_value: Optional[bool] = None  # 是否多值抽取
    duplicate_value_distinct: Optional[bool] = None  # 是否重复值去重
    transform_settings: Optional[TransformSettings] = None  # 转换配置

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldConfigResponse":
        """从字典创建对象"""
        return cls(
            field_id=str(data.get("fieldId") or data.get("field_id")),
            field_name=data.get("fieldName") or data.get("field_name"),
            alias=data.get("alias"),
            identity=data.get("identity"),
            multi_value=data.get("multiValue") or data.get("multi_value"),
            duplicate_value_distinct=data.get("duplicateValueDistinct") or data.get("duplicate_value_distinct"),
            transform_settings=TransformSettings.from_dict(
                data.get("transformSettings") or data.get("transform_settings")
            ),
        )


# ==================== 样本相关模型 ====================

@dataclass
class SampleInfo:
    """
    样本信息

    对应后端: CategorySampleVO
    """
    sample_id: str
    file_name: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SampleInfo":
        """从字典创建对象"""
        return cls(
            sample_id=str(data.get("sampleId") or data.get("sample_id")),
            file_name=data.get("fileName") or data.get("file_name"),
        )


@dataclass
class SampleUploadResponse:
    """
    上传样本响应

    对应后端: CategorySampleUploadRespVO（单文件上传）
    """
    sample_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SampleUploadResponse":
        """从字典创建对象"""
        return cls(
            sample_id=str(data.get("sampleId") or data.get("sample_id"))
        )


@dataclass
class BatchSampleUploadResponse:
    """
    批量上传样本响应

    对应后端: CategorySampleUploadRespVO（批量上传，with_detail 时含 samples 列表）
    """
    samples: Optional[List["SampleInfo"]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchSampleUploadResponse":
        """从字典创建对象"""
        samples_data = data.get("samples")
        samples_list = None
        if samples_data:
            samples_list = [SampleInfo.from_dict(s) for s in samples_data]

        return cls(samples=samples_list)


@dataclass
class SampleListResponse:
    """
    样本列表响应

    对应后端: CategorySampleListRespVO
    """
    total: int
    page: int
    page_size: int
    samples: List[SampleInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SampleListResponse":
        """从字典创建对象"""
        samples_data = data.get("samples") or data.get("list") or []
        samples = [SampleInfo.from_dict(s) for s in samples_data]

        return cls(
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("pageSize") or data.get("page_size", 20),
            samples=samples,
        )


# ==================== 批量操作响应模型 ====================

@dataclass
class BatchFieldAddResponse:
    """批量新增字段响应"""
    fields: List[FieldAddResponse] = field(default_factory=list)

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "BatchFieldAddResponse":
        """从列表创建对象"""
        if not data:
            return cls(fields=[])
        return cls(fields=[FieldAddResponse.from_dict(f) for f in data])


@dataclass
class BatchTableAddResponse:
    """批量新增表格响应"""
    tables: List[TableAddResponse] = field(default_factory=list)

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "BatchTableAddResponse":
        """从列表创建对象"""
        if not data:
            return cls(tables=[])
        return cls(tables=[TableAddResponse.from_dict(t) for t in data])
