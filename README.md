# Docflow Python SDK

Docflow Python SDK，提供简洁易用的 API 接口，方便 Python 开发者快速集成Docflow的功能。

## 📋 功能特性

- ✅ **工作空间管理**：创建、查询、更新、删除工作空间
- ✅ **类别管理**：创建、查询、更新、删除文件类别（支持文件上传）
- ✅ **字段管理**：类别字段的增删改查及配置管理
- ✅ **表格管理**：类别表格的增删改查
- ✅ **样本管理**：样本文件的上传、下载、删除
- ✅ **类型安全**：完整的类型注解，支持 IDE 自动补全
- ✅ **枚举类型**：提供完整的枚举定义，避免参数传错
- ✅ **异常处理**：完善的异常体系，便于错误处理
- ✅ **国际化（i18n）**：多语言错误消息支持
  - 支持中文（zh_CN）和英文（en_US）
  - 可动态切换语言
  - 支持参数化消息
- ✅ **智能重试**：基于 urllib3.util.retry.Retry 的灵活重试机制
  - 可配置重试状态码（默认：423, 429, 500, 503, 504, 900）
  - 可配置重试方法（默认：GET, POST, PUT, DELETE）
  - 可配置退避因子（默认：1.0，指数退避策略）
  - 可配置最大重试次数（默认：3次）
- ✅ **连接池**：高效的 HTTP 连接复用（10 连接池，20 最大连接）
- ✅ **易于使用**：符合 Python 习惯的 API 设计
- ✅ **链式调用**：支持上下文绑定，减少重复参数传递（代码量减少 70%）
- ✅ **自动分页**：提供迭代器自动处理分页逻辑，内存高效
- ✅ **环境变量支持**：from_env() 方法自动加载配置

## 📦 安装

### 使用 pip 安装（推荐）

```bash
pip install docflow-sdk
```

### 从 GitHub 安装

```bash
pip install git+https://github.com/intsig-textin/docflow-python-sdk.git
```

### 从源码安装

```bash
git clone https://github.com/intsig-textin/docflow-python-sdk.git
cd docflow-python-sdk
pip install -e .
```

## 🚀 快速开始

> 💡 **想快速体验完整流程？** 查看 [费用报销场景快速开始指南](examples/QUICKSTART.md)，5分钟完成从创建空间到智能审核的端到端流程！

### 1. 初始化客户端

```python
from docflow import DocflowClient, AuthScope  # 导入枚举类型

# 方式 1: 最简洁（使用默认 base_url）
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    enterprise_id="12345"  # 可选，用于工作空间操作
    # base_url 默认为 "https://docflow.textin.com"
)

# 方式 2: 从环境变量加载
client = DocflowClient.from_env()
# 需要设置环境变量：
# export DOCFLOW_APP_ID="your-app-id"
# export DOCFLOW_SECRET_CODE="your-secret-code"
# export DOCFLOW_BASE_URL="https://docflow.textin.com"  # 可选
# export DOCFLOW_ENTERPRISE_ID="12345"  # 可选，用于工作空间操作

# 方式 3: 自定义 base_url
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    base_url="https://custom.api.com",
    enterprise_id="12345"  # 可选
)
```

### 2. 工作空间操作

#### 创建工作空间

```python
# 使用 AuthScope 枚举避免参数传错
workspace = client.workspace.create(
    name="我的工作空间",
    auth_scope=AuthScope.PUBLIC  # 使用枚举而非数字1
)
print(f"创建的工作空间ID: {workspace.workspace_id}")
```

#### 获取工作空间列表

```python
workspaces = client.workspace.list(
    page=1,
    page_size=20
)

for ws in workspaces.workspaces:
    print(f"{ws.workspace_id}: {ws.name}")
```

#### 获取工作空间详情

```python
detail = client.workspace.get(workspace_id="123")
print(f"工作空间名称: {detail.name}")
print(f"企业ID: {detail.enterprise_id}")
```

#### 更新工作空间

```python
client.workspace.update(
    workspace_id="123",
    name="新的工作空间名称",
    auth_scope=0
)
```

#### 删除工作空间

```python
client.workspace.delete(workspace_ids=["123", "456"])
```

### 3. 类别操作

#### 创建类别（带文件上传）

```python
from docflow import ExtractModel, FieldType  # 导入枚举类型

# 定义字段配置
fields = [
    {
        "name": "发票号码",
        "description": "发票唯一标识"
    },
    {
        "name": "开票日期",
        "transform_settings": {
            "type": FieldType.DATETIME.value,  # 使用 FieldType 枚举指定转换类型
            "datetime_settings": {
                "format": "yyyy-MM-dd"
            }
        }
    }
]

# 定义表格配置
tables = [
    {"name": "商品明细表", "description": "商品信息"}
]

# 创建类别（使用 ExtractModel 枚举）
category = client.category.create(
    workspace_id="123",
    name="发票类别",
    extract_model=ExtractModel.LLM,  # 使用枚举而非字符串 "llm"
    sample_files=[
        "/path/to/sample1.pdf",
        "/path/to/sample2.pdf"
    ],
    fields=fields,
    tables=tables,
    category_prompt="这是发票类别"
)
print(f"类别ID: {category.category_id}")
```

#### 获取类别列表

```python
# 使用 EnabledStatus 枚举查询
categories = client.category.list(
    workspace_id="123",
    page=1,
    page_size=20,
    enabled=EnabledStatus.ENABLED  # 使用枚举
)

for cat in categories.categories:
    print(f"{cat.category_id}: {cat.name}")
```

#### 字段管理

```python
# 新增字段
field = client.category.fields.add(
    workspace_id="123",
    category_id="456",
    name="税率"
)

# 获取字段列表
fields = client.category.fields.list(
    workspace_id="123",
    category_id="456"
)

# 更新字段
client.category.fields.update(
    workspace_id="123",
    category_id="456",
    field_id="789",
    name="税率(%)",
    required=True
)

# 删除字段
client.category.fields.delete(
    workspace_id="123",
    category_id="456",
    field_ids=["789"]
)
```

#### 样本管理

```python
# 上传样本
sample = client.category.samples.upload(
    workspace_id="123",
    category_id="456",
    file="/path/to/sample.pdf"
)

# 获取样本列表
samples = client.category.samples.list(
    workspace_id="123",
    category_id="456"
)

# 下载样本
client.category.samples.download(
    workspace_id="123",
    category_id="456",
    sample_id="789",
    save_path="/path/to/save.pdf"
)
```

📖 **更多 API 使用示例**：查看 [examples 目录](examples/README.md) 获取完整的使用示例，包括文件处理、审核规则和完整业务流程

### 4. 链式调用（减少 70% 重复代码）

通过上下文绑定，无需重复传递 `workspace_id` 和 `category_id`：

```python
# 传统方式（冗长，需要重复传递参数）
client.category.fields.add(workspace_id="123", category_id="456", name="字段1")
client.category.fields.add(workspace_id="123", category_id="456", name="字段2")
client.category.tables.add(workspace_id="123", category_id="456", name="表格1")

# 链式调用方式（简洁，代码量减少 70%）
ws = client.workspace("123")
cat = ws.category("456")

# 简化的字段操作
cat.fields.add(name="字段1")
cat.fields.add(name="字段2")
cat.tables.add(name="表格1")

# 工作空间操作
ws.get()                      # 获取详情
ws.update(name="新名称")       # 更新
ws.delete()                   # 删除

# 类别操作
cat.update(name="新名称")      # 更新类别
cat.fields.list()             # 获取字段列表
cat.tables.list()             # 获取表格列表
cat.samples.upload(file="sample.pdf")  # 上传样本
```

### 5. 自动分页迭代器

使用迭代器自动处理分页，无需手动循环：

```python
# 传统方式（手动分页）
all_workspaces = []
page = 1
while True:
    response = client.workspace.list(page=page, page_size=100)
    all_workspaces.extend(response.workspaces)
    if page >= response.total // response.page_size + 1:
        break
    page += 1

# 迭代器方式（自动分页）
# 方式 1: 直接遍历（内存高效，支持随时中断）
for workspace in client.workspace.iter():
    print(f"{workspace.workspace_id}: {workspace.name}")
    if some_condition:
        break  # 可以随时中断

# 方式 2: 转换为列表（获取所有数据）
all_workspaces = list(client.workspace.iter())

# 方式 3: 限制最大页数（防止数据过大）
for workspace in client.workspace.iter(max_pages=5):
    print(workspace.name)

# 类别迭代器
for category in client.category.iter(workspace_id="123"):
    print(f"{category.category_id}: {category.name}")

# 获取所有未启用的类别
disabled_categories = list(
    client.category.iter(workspace_id="123", enabled=EnabledStatus.DISABLED)
)
```

### 6. 枚举类型（避免参数传错）

SDK 提供完整的枚举类型定义，使用枚举可以获得 IDE 自动补全和类型检查，避免因参数拼写错误导致 API 调用失败。

#### 6.1 可用的枚举类型

```python
from docflow import (
    ExtractModel,      # 提取模型类型
    EnabledStatus,     # 启用状态（查询用）
    EnabledFlag,       # 启用标志（更新用）
    AuthScope,         # 权限范围
    FieldType,         # 字段类型
)

# ExtractModel - 提取模型
ExtractModel.LLM  # "llm" - 大语言模型
ExtractModel.VLM  # "vlm" - 视觉语言模型

# AuthScope - 权限范围
AuthScope.PRIVATE  # 0 - 私有权限
AuthScope.PUBLIC   # 1 - 公共权限

# EnabledStatus - 启用状态（查询用）
EnabledStatus.ALL       # "all" - 全部
EnabledStatus.DISABLED  # "0"   - 未启用
EnabledStatus.ENABLED   # "1"   - 已启用（默认）
EnabledStatus.OTHER     # "2"   - 其他状态

# EnabledFlag - 启用标志（更新用）
EnabledFlag.DISABLED  # 0 - 未启用
EnabledFlag.ENABLED   # 1 - 已启用

# FieldType - 字段转换类型（用于 transform_settings.type）
FieldType.DATETIME   # "datetime"   - 日期时间类型转换
FieldType.ENUMERATE  # "enumerate"  - 枚举类型转换
FieldType.REGEX      # "regex"      - 正则表达式类型转换

# MismatchAction - 字段值不匹配时的处理模式
MismatchAction.DEFAULT  # "default"  - 使用默认值
MismatchAction.WARNING  # "warning"  - 显示警告
```

#### 6.2 使用示例

```python
from docflow import (
    DocflowClient,
    AuthScope,
    ExtractModel,
    FieldType,
    MismatchAction,
    EnabledStatus,
    EnabledFlag,
)

client = DocflowClient.from_env()

# 使用枚举创建工作空间
workspace = client.workspace.create(
    name="我的工作空间",
    auth_scope=AuthScope.PUBLIC  # ✅ 类型安全
)

# 使用枚举创建类别
category = client.category.create(
    workspace_id="123",
    name="发票类别",
    extract_model=ExtractModel.LLM,  # ✅ 避免拼写错误
    sample_files=["/path/to/sample.pdf"],
    fields=[
        {
            "name": "发票号码",
            "description": "发票唯一标识"
        },
        {
            "name": "开票日期",
            "transform_settings": {
                "type": FieldType.DATETIME.value,  # ✅ 使用 FieldType 枚举
                "datetime_settings": {
                    "format": "yyyy-MM-dd"
                }
            }
        },
        {
            "name": "发票类型",
            "transform_settings": {
                "type": FieldType.ENUMERATE.value,
                "enumerate_settings": {
                    "items": ["增值税专用发票", "增值税普通发票"]
                },
                "mismatch_action": {
                    "mode": MismatchAction.WARNING.value  # ✅ 使用枚举
                }
            }
        }
    ]
)

# 使用枚举查询类别
categories = client.category.list(
    workspace_id="123",
    enabled=EnabledStatus.ENABLED  # ✅ 清晰明确
)

# 使用枚举更新类别
client.category.update(
    workspace_id="123",
    category_id="456",
    enabled=EnabledFlag.ENABLED  # ✅ 类型安全
)

# 添加字段
client.category.fields.add(
    workspace_id="123",
    category_id="456",
    name="联系电话"
)
```

#### 6.3 向后兼容

所有枚举类型都向后兼容，仍然支持原有的字符串和数字参数：

```python
# ✅ 新代码（推荐）
extract_model=ExtractModel.LLM
auth_scope=AuthScope.PUBLIC
transform_settings={"type": FieldType.DATETIME.value}

# ✅ 旧代码（仍然支持）
extract_model="llm"
auth_scope=1
transform_settings={"type": "datetime"}
```

### 7. 异常处理

```python
from docflow.exceptions import (
    APIError,
    ValidationError,
    ResourceNotFoundError,
    PermissionDeniedError
)

try:
    workspace = client.workspace.get(workspace_id="999")
except ResourceNotFoundError as e:
    print(f"工作空间不存在: {e}")
except PermissionDeniedError as e:
    print(f"权限不足: {e}")
except APIError as e:
    print(f"API错误 [{e.status_code}]: {e.message}")
```

### 8. 使用上下文管理器

```python
with DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    enterprise_id="12345"
) as client:
    workspaces = client.workspace.list()
    # 自动关闭连接
```

## 📖 API 文档

### DocflowClient

主客户端类，用于初始化 SDK 并访问各种资源。

#### 参数

- `base_url` (str): API 基础地址
- `app_id` (str): 应用ID（对应请求头 x-ti-app-id）
- `secret_code` (str): 密钥（对应请求头 x-ti-secret-code）
- `enterprise_id` (str, 可选): 企业ID（对应请求头 x-ti-enterprise-id），用于工作空间操作
- `timeout` (int, 可选): 请求超时时间（秒），默认 30
- `max_retries` (int, 可选): 最大重试次数，默认 3

#### 方法

- `set_credentials(app_id: str, secret_code: str)`: 更新认证凭证
- `close()`: 关闭客户端，释放资源

### WorkspaceResource

工作空间资源操作类，通过 `client.workspace` 访问。

#### 方法

##### create()

创建工作空间

**注意：** 企业ID通过请求头 `x-ti-enterprise-id` 传递，需要在初始化客户端时配置。

```python
def create(
    name: str,
    auth_scope: Union[AuthScope, int],
    description: Optional[str] = None,
    **kwargs
) -> WorkspaceCreateResponse
```

##### list()

获取工作空间列表

**注意：** 企业ID通过请求头 `x-ti-enterprise-id` 传递，需要在初始化客户端时配置。

```python
def list(
    page: int = 1,
    page_size: int = 20
) -> WorkspaceListResponse
```

##### get()

获取工作空间详情

```python
def get(workspace_id: str) -> WorkspaceDetailResponse
```

##### update()

更新工作空间

```python
def update(
    workspace_id: str,
    name: Optional[str] = None,
    auth_scope: Optional[int] = None,
    **kwargs
) -> None
```

##### delete()

批量删除工作空间

```python
def delete(workspace_ids: List[str]) -> None
```

## 🔧 配置

### 环境变量

可以使用环境变量配置 SDK：

```bash
export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
export DOCFLOW_APP_ID="your-app-id"
export DOCFLOW_SECRET_CODE="your-secret-code"
export DOCFLOW_ENTERPRISE_ID="12345"
```

### 使用 .env 文件

创建 `.env` 文件：

```env
DOCFLOW_BASE_URL=https://docflow.textin.com
DOCFLOW_APP_ID=your-app-id
DOCFLOW_SECRET_CODE=your-secret-code
DOCFLOW_ENTERPRISE_ID=12345
```

在代码中加载：

```python
from dotenv import load_dotenv
import os

load_dotenv()

client = DocflowClient(
    base_url=os.getenv("DOCFLOW_BASE_URL"),
    app_id=os.getenv("DOCFLOW_APP_ID"),
    secret_code=os.getenv("DOCFLOW_SECRET_CODE")
)
```

## 🌍 国际化（i18n）

SDK 支持多语言错误消息，方便全球化应用：

### 支持的语言

- **zh_CN**: 中文（简体）- 默认
- **en_US**: 英文（美国）

### 设置语言

#### 方式一：创建客户端时指定

```python
# 使用中文（默认）
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    language='zh_CN'
)

# 使用英文
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    language='en_US'
)
```

#### 方式二：动态切换语言

```python
client = DocflowClient(...)

# 切换到英文
client.set_language('en_US')

# 切换回中文
client.set_language('zh_CN')

# 获取当前语言
current_lang = client.get_language()  # 返回 'en_US' 或 'zh_CN'

# 获取所有可用语言
languages = client.get_available_languages()  # ['zh_CN', 'en_US']
```

#### 方式三：全局设置

```python
from docflow.i18n import set_language

# 设置全局语言（影响所有异常）
set_language('en_US')
```

### 错误消息示例

```python
from docflow.exceptions import ValidationError, AuthenticationError

# 中文错误消息
set_language('zh_CN')
try:
    raise ValidationError(
        "字段太长",
        i18n_key='error.validation.too_long',
        field='工作空间名称',
        max_length=50
    )
except ValidationError as e:
    print(e)  # 输出: 工作空间名称 长度不能超过 50 个字符

# 英文错误消息
set_language('en_US')
try:
    raise AuthenticationError()
except AuthenticationError as e:
    print(e)  # 输出: Authentication failed, please check app_id and secret_code
```

## 🔄 重试机制

SDK 使用 `urllib3.util.retry.Retry` 实现智能重试功能：

### 自动重试的场景

以下 HTTP 状态码会自动触发重试：
- **423**: Locked (资源被锁定)
- **429**: Too Many Requests (请求过多，触发限流)
- **500**: Internal Server Error (服务器内部错误)
- **503**: Service Unavailable (服务不可用)
- **504**: Gateway Timeout (网关超时)
- **900**: 自定义业务错误码

### 重试策略

采用指数退避策略，重试间隔自动增长：
- 第 1 次重试: 立即（0秒）
- 第 2 次重试: 等待 2 秒
- 第 3 次重试: 等待 4 秒
- 第 4 次重试: 等待 8 秒

### 配置重试

SDK 支持灵活的重试配置，可以根据不同场景定制重试行为：

```python
from docflow import DocflowClient

# 默认配置
client = DocflowClient(
    base_url="https://docflow.textin.com",
    app_id="your-app-id",
    secret_code="your-secret-code"
)

# 自定义重试次数和超时
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    max_retries=5,  # 最大重试 5 次（默认 3）
    timeout=60      # 60 秒超时（默认 30）
)

# 自定义重试状态码
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    retry_status_codes=[429, 503],  # 只重试 429 和 503
)

# 自定义重试方法
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    retry_methods=["GET"],  # 只允许 GET 请求重试
)

# 自定义退避因子（影响重试间隔）
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    retry_backoff_factor=0.5,  # 更快的重试（默认 1.0）
)

# 禁用重试
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    max_retries=0  # 禁用重试
)

# 查看当前重试配置
print(f"最大重试次数: {client.config.max_retries}")
print(f"重试状态码: {client.config.retry_status_codes}")
print(f"重试方法: {client.config.retry_methods}")
print(f"退避因子: {client.config.retry_backoff_factor}")
```

**重试间隔计算公式**：

```
等待时间 = backoff_factor * (2 ** (重试次数 - 1))
```

示例：
- `backoff_factor=0.5`: 重试间隔 0.5s, 1s, 2s, 4s...
- `backoff_factor=1.0`: 重试间隔 1s, 2s, 4s, 8s... （默认）
- `backoff_factor=2.0`: 重试间隔 2s, 4s, 8s, 16s...

### 不会重试的情况

以下错误不会触发重试（需要修正代码或配置）：
- **401**: Unauthorized (认证失败)
- **403**: Forbidden (权限不足)
- **404**: Not Found (资源不存在)
- **400**: Bad Request (参数错误)

## 🧪 运行示例

```bash
# 设置环境变量
export DOCFLOW_BASE_URL="https://docflow.textin.com"
export DOCFLOW_APP_ID="your-app-id"
export DOCFLOW_SECRET_CODE="your-secret-code"
export DOCFLOW_ENTERPRISE_ID="12345"

# 运行快速开始示例（费用报销场景）
python examples/quick_start.py

# 运行工作流程示例（发票处理）
python examples/complete_workflow_example.py

# 运行文件处理示例
python examples/file_examples.py

# 运行审核规则示例
python examples/review_examples.py
```

## 📝 异常类型

SDK 提供以下异常类型：

- `DocflowException`: 基础异常类
- `AuthenticationError`: 认证失败异常
- `ValidationError`: 参数校验异常
- `ResourceNotFoundError`: 资源不存在异常
- `PermissionDeniedError`: 权限不足异常
- `APIError`: API 调用异常
- `NetworkError`: 网络异常

## 🔒 安全建议

1. **不要硬编码凭证**：使用环境变量或配置文件管理 app_id 和 secret_code
2. **使用 HTTPS**：确保 `base_url` 使用 HTTPS 协议
3. **定期更新凭证**：使用 `client.set_credentials()` 定期更新认证凭证
4. **妥善保管凭证**：不要将凭证提交到版本控制系统

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**版本**: 1.0.0
**最后更新**: 2026-03-06
