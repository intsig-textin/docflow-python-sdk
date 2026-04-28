# Changelog

本文档记录 Docflow Python SDK 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.3] - 2026-04-28

### Added

- ✨ **审核模型选择** (`ReviewModel` 枚举)
  - 新增 `ReviewModel` 枚举类型，支持选择审核模型
    - `DEEPSEEK_R1 = "1"`: deepseek-r1
    - `QWQ_32B = "2"`: qwq-32b
    - `QWEN3_MAX = "3"`: qwen3-max
    - `ORM_O1 = "5"`: ORM-O1
  - `client.review.submit_task()` 新增可选参数 `model`，支持指定审核模型
  - `client.review.get_task_result()` 新增可选参数 `model`，支持指定审核模型

---

## [1.0.0] - 2026-03-17

### Added

#### 核心功能

- ✨ **工作空间管理模块** (`WorkspaceResource`)
  - 创建工作空间：`client.workspace.create()` - 支持公开/私有权限设置
  - 列表查询：`client.workspace.list()` - 支持分页查询
  - 详情查询：`client.workspace.get()` - 获取工作空间详细信息
  - 更新工作空间：`client.workspace.update()` - 修改名称和权限
  - 批量删除：`client.workspace.delete()` - 按 ID 列表删除
  - 迭代器：`client.workspace.iter()` - 自动分页遍历所有工作空间

- ✨ **类别管理模块** (`CategoryResource`)
  - 创建类别：`client.category.create()` - 支持 LLM/VLM 提取模型
  - 列表查询：`client.category.list()` - 支持分页和状态筛选
  - 详情查询：`client.category.get()` - 获取类别完整配置
  - 更新类别：`client.category.update()` - 修改类别信息
  - 批量删除：`client.category.delete()` - 按 ID 列表删除
  - 迭代器：`client.category.iter()` - 自动分页遍历所有类别

- ✨ **字段管理功能** (`FieldContext`)
  - 列表查询：`cat.fields.list()` - 获取字段列表
  - 新增字段：`cat.fields.add()` - 添加单个字段
  - 高级配置：`cat.fields.get_config()` - 获取字段高级配置
  - 更新字段：`cat.fields.update()` - 修改字段信息
  - 批量删除：`cat.fields.delete()` - 按 ID 列表删除

- ✨ **表格管理功能** (`TableContext`)
  - 列表查询：`cat.tables.list()` - 获取表格列表
  - 新增表格：`cat.tables.add()` - 添加表格及其字段
  - 更新表格：`cat.tables.update()` - 修改表格信息
  - 批量删除：`cat.tables.delete()` - 按 ID 列表删除

- ✨ **样本管理功能** (`SampleContext`)
  - 上传样本：`cat.samples.upload()` - 支持文件路径和文件对象
  - 列表查询：`cat.samples.list()` - 支持分页查询
  - 下载样本：`cat.samples.download()` - 支持保存到文件或返回字节流
    - 自动从 Content-Disposition 头提取文件名
    - 支持 RFC 5987 格式和标准格式
    - 自动 URL 解码国际化文件名（如中文）
  - 批量删除：`cat.samples.delete()` - 按 ID 列表删除

- ✨ **文件处理模块** (`FileResource`)
  - 文件上传：`client.file.upload()` - 异步上传文件
  - 同步上传：`client.file.upload_sync()` - 同步上传并等待处理完成
  - 文件查询：`client.file.fetch()` - 获取文件处理结果列表
  - 迭代器：`client.file.iter()` - 自动分页遍历所有文件
  - 文件更新：`client.file.update()` - 更新单个文件数据
  - 批量更新：`client.file.batch_update()` - 批量更新多个文件
  - 文件删除：`client.file.delete()` - 按文件 ID、批次号或时间范围删除
  - 字段抽取：`client.file.extract_fields()` - 抽取特定字段和表格
  - 重新处理：`client.file.retry()` - 重新处理文件
  - 类别修改：`client.file.amend_category()` - 修改文件所属类别

- ✨ **审核规则管理模块** (`ReviewResource`)
  - **规则库管理**
    - 创建规则库：`client.review.create_repo()`
    - 列表查询：`client.review.list_repos()` - 支持分页
    - 详情查询：`client.review.get_repo()` - 获取规则库及其规则组、规则
    - 更新规则库：`client.review.update_repo()`
    - 删除规则库：`client.review.delete_repo()`
  - **规则组管理**
    - 创建规则组：`client.review.create_group()`
    - 更新规则组：`client.review.update_group()`
    - 删除规则组：`client.review.delete_group()`
  - **规则管理**
    - 创建规则：`client.review.create_rule()` - 支持自定义规则类型和配置
    - 更新规则：`client.review.update_rule()`
    - 删除规则：`client.review.delete_rule()`
  - **任务管理**
    - 提交任务：`client.review.submit_task()` - 创建审核任务
    - 删除任务：`client.review.delete_task()`
    - 获取结果：`client.review.get_task_result()` - 获取审核结果
    - 重新审核：`client.review.retry_task()` - 重试整个任务
    - 重试规则：`client.review.retry_task_rule()` - 重试特定规则

#### 上下文和链式调用

- ✨ **工作空间上下文** (`WorkspaceContext`)
  - 链式调用：`ws = client.workspace("workspace_id")`
  - 访问审核规则：`ws.review.create_repo()`
  - 访问类别：`ws.category("category_id")`

- ✨ **类别上下文** (`CategoryContext`)
  - 链式调用：`cat = client.workspace("ws_id").category("cat_id")`
  - 字段管理：`cat.fields.add()`, `cat.fields.list()`
  - 表格管理：`cat.tables.add()`, `cat.tables.list()`
  - 样本管理：`cat.samples.upload()`, `cat.samples.download()`

- ✨ **审核规则上下文** (`ReviewContext`)
  - 链式调用：`review = client.workspace("ws_id").review`
  - 继承所有 ReviewResource 方法
  - 自动绑定 workspace_id

#### 数据模型

- ✨ **工作空间模型**
  - `WorkspaceInfo`: 工作空间基本信息
  - `WorkspaceCreateResponse`: 创建响应（包含 workspace_id）
  - `WorkspaceListResponse`: 列表响应（包含分页信息）
  - `WorkspaceDetailResponse`: 详情响应

- ✨ **类别模型**
  - `CategoryInfo`: 类别基本信息
  - `CategoryCreateResponse`: 创建响应（包含 category_id）
  - `CategoryListResponse`: 列表响应（包含分页信息）

- ✨ **字段和表格模型**
  - `FieldInfo`: 字段信息
  - `FieldListResponse`: 字段列表响应
  - `FieldAddResponse`: 字段添加响应
  - `FieldConfigResponse`: 字段配置响应
  - `TableInfo`: 表格信息
  - `TableListResponse`: 表格列表响应
  - `TableAddResponse`: 表格添加响应

- ✨ **样本模型**
  - `SampleInfo`: 样本信息
  - `SampleUploadResponse`: 上传响应
  - `SampleListResponse`: 列表响应（包含分页信息）

- ✨ **文件模型**
  - `FileInfo`: 文件信息（包含识别状态、任务 ID 等）
  - `FileUploadResponse`: 上传响应（包含批次号和文件列表）
  - `FileFetchResponse`: 查询响应（包含分页信息）
  - `FileUpdateResponse`: 更新响应
  - `FileDeleteResponse`: 删除响应（包含删除数量）

- ✨ **审核规则模型**
  - `ReviewRule`: 审核规则
  - `ReviewGroup`: 规则组
  - `ReviewRepoInfo`: 规则库信息（包含嵌套的规则组和规则）
  - `ReviewRepoCreateResponse`: 规则库创建响应
  - `ReviewRepoListResponse`: 规则库列表响应
  - `ReviewGroupCreateResponse`: 规则组创建响应
  - `ReviewRuleCreateResponse`: 规则创建响应

- ✨ 所有模型支持 `from_dict()` 类方法
- ✨ 兼容 camelCase 和 snake_case 字段名

#### 国际化支持

- ✨ **多语言错误消息**
  - 支持中文（zh_CN）和英文（en_US）
  - 客户端初始化时指定语言：`DocflowClient(language='en_US')`
  - 动态切换语言：`client.set_language('en_US')`
  - 查询当前语言：`client.get_language()`
  - 列出可用语言：`client.get_available_languages()`
  - 支持参数化消息（如字段名、长度限制等）
  - 所有 ValidationError 和 APIError 都包含 i18n_key

- ✨ **i18n 模块** (`docflow/i18n/`)
  - 单例模式的 I18n 类
  - 语言包：`locales/zh_CN.py` 和 `locales/en_US.py`
  - 支持格式化参数：`t('error.validation.too_long', field='名称', max_length=50)`

#### 异常处理

- ✨ **完整的异常体系**
  - `DocflowException`: 基础异常类
  - `AuthenticationError`: 认证失败（401）
  - `ValidationError`: 参数校验失败（本地校验）
  - `ResourceNotFoundError`: 资源不存在（404）
  - `PermissionDeniedError`: 权限不足（403）
  - `APIError`: API 调用失败（包含状态码、错误消息、请求 ID）
  - `NetworkError`: 网络错误（连接超时、DNS 解析失败等）

- ✨ 所有异常都包含详细的错误信息和上下文
- ✨ 支持从 HTTP 状态码自动创建对应异常

#### HTTP 客户端

- ✨ **智能重试机制**
  - 基于 urllib3.util.retry.Retry 实现
  - 默认最大重试次数：3 次
  - 指数退避策略：backoff_factor=1.0
  - 可重试状态码：423, 429, 500, 503, 504, 900
  - 可重试方法：GET, POST, PUT, DELETE, PATCH
  - 详细的重试日志（DEBUG 级别）
  - 重试统计接口：`client.http_client.get_retry_stats()`

- ✨ **连接池管理**
  - pool_connections=10
  - pool_maxsize=20
  - 自动连接复用

- ✨ **请求监控**
  - 请求耗时统计
  - 详细的请求/响应日志

- ✨ **超时控制**
  - 连接超时：10 秒
  - 读取超时：30 秒
  - 可通过参数自定义

#### 工具类

- ✨ **文件处理工具** (`FileHandler`)
  - 自动识别 MIME 类型
  - 文件大小校验（最大 100MB）
  - 支持多种输入方式：文件路径、文件对象、字节数据
  - 文件格式校验
  - 支持的格式：PDF, DOC, DOCX, XLS, XLSX, JPG, JPEG, PNG, BMP, TIFF, WEBP

#### 枚举类型

- ✨ **提取模型** (`ExtractModel`)
  - `LLM`: 大语言模型
  - `VLM`: 视觉语言模型

- ✨ **状态枚举**
  - `EnabledStatus`: 启用状态（ALL, DISABLED, ENABLED, OTHER）
  - `EnabledFlag`: 启用标志（DISABLED=0, ENABLED=1）
  - `AuthScope`: 权限范围（PRIVATE=0, PUBLIC=1）

- ✨ **字段类型** (`FieldType`)
  - TEXT, NUMBER, DATE, AMOUNT, CHECKBOX 等

- ✨ **不匹配处理** (`MismatchAction`)
  - FAIL: 失败
  - SKIP_ROW: 跳过该行
  - SKIP_COLUMN: 跳过该列

#### 认证和安全

- 🔒 支持通过 `app_id` 和 `secret_code` 进行认证
- 🔒 请求头使用 `x-ti-app-id` 和 `x-ti-secret-code`
- 🔒 支持从环境变量加载凭证：`DocflowClient.from_env()`
- 🔒 支持动态更新凭证：`client.set_credentials()`

#### 开发体验

- ✨ **类型注解支持**
  - 所有公开 API 都有完整的类型注解
  - 支持 IDE 自动补全和类型检查
  - 兼容 Python 3.8+

- ✨ **上下文管理器**
  - 支持 `with` 语句：`with DocflowClient(...) as client:`
  - 自动资源清理

- ✨ **参数校验**
  - 本地参数校验，快速失败
  - 详细的错误提示
  - 支持中英文错误消息

#### 测试

- ✨ **完整的单元测试套件**
  - 203 个测试用例，全部通过
  - 代码覆盖率：78.34%
  - 测试文件：
    - `tests/test_auth.py`: 认证测试（4 个）
    - `tests/test_client.py`: 客户端测试（14 个）
    - `tests/test_workspace.py`: 工作空间测试（19 个）
    - `tests/test_category.py`: 类别测试（41 个）
    - `tests/test_file.py`: 文件测试（25 个）
    - `tests/test_review.py`: 审核规则测试（37 个）
    - `tests/test_i18n.py`: 国际化测试（10 个）
    - `tests/test_models.py`: 模型测试（13 个）
    - `tests/test_enums.py`: 枚举测试（17 个）
    - `tests/test_exceptions.py`: 异常测试（12 个）
    - `tests/test_context.py`: 上下文测试（11 个）

- ✨ **集成测试项目** (`docflow-sdk-test/`)
  - 43 个真实 API 集成测试
  - 涵盖所有主要接口
  - 支持真实环境测试

#### 文档

- ✨ **完整的用户文档**
  - README.md: 快速开始和基本用法
  - examples/QUICKSTART.md: 详细的快速开始指南
  - docs/user-manual.md: 完整的用户手册（11 章）
    - 第 1 章：安装和配置
    - 第 2 章：客户端初始化
    - 第 3 章：工作空间管理
    - 第 4 章：类别管理
    - 第 5 章：字段管理
    - 第 6 章：表格管理
    - 第 7 章：样本管理
    - 第 8 章：上下文和链式调用
    - 第 9 章：国际化支持
    - 第 10 章：文件处理
    - 第 11 章：审核规则管理
  - docs/category_api_guide.md: 类别 API 使用指南

- ✨ **丰富的示例代码**
  - `examples/basic_usage.py`: 基础用法
  - `examples/workspace_example.py`: 工作空间管理
  - `examples/category_example.py`: 类别管理完整示例
  - `examples/file_example.py`: 文件处理示例
  - `examples/review_example.py`: 审核规则管理示例
  - `examples/i18n_example.py`: 国际化示例
  - `examples/retry_example.py`: 重试机制示例
  - `examples/error_handling.py`: 错误处理示例

- ✨ **API 参考文档**
  - 所有方法都有详细的 docstring
  - 包含参数说明、返回值、异常和使用示例

#### 配置和常量

- ✨ **集中的常量管理** (`_constants.py`)
  - API 版本和前缀
  - 默认配置（URL, 超时, 重试等）
  - HTTP 配置（可重试状态码、方法）
  - 分页配置
  - 文件限制
  - 语言配置

- ✨ **项目配置**
  - `pyproject.toml`: 现代化的 Python 项目配置
  - 集成 Black（代码格式化）
  - 集成 Ruff（代码检查）
  - 集成 MyPy（类型检查）
  - 集成 Pytest（测试）
  - 集成 Coverage（覆盖率）

#### 依赖管理

- ✨ **精简的依赖**
  - `requests>=2.28.0`: HTTP 请求
  - `urllib3>=1.26.0,<2.0.0`: 连接池和重试
  - `python-dotenv>=0.20.0`: 环境变量管理
  - `typing-extensions>=4.0.0`: 类型注解支持（Python<3.11）

- ✨ **开发依赖**
  - pytest, pytest-cov, pytest-mock: 测试框架
  - requests-mock: HTTP mock
  - black, ruff: 代码质量工具
  - mypy, types-requests: 类型检查

### Changed

- ✨ 认证方式从 `api_key` 改为 `app_id` + `secret_code`
- ✨ 请求头从 `X-API-Key` 改为 `x-ti-app-id` + `x-ti-secret-code`
- ✨ 默认 API 地址：`https://docflow.textin.com/api`
- ✨ API 前缀：`/app-api/sip/platform/v2`
- ✨ 模型目录从覆盖率测试中排除

### Fixed

- 🐛 修复样本下载时文件名提取问题（支持 RFC 5987 格式和 URL 解码）
- 🐛 修复业务错误优先级（业务错误优先于参数校验错误）
- 🐛 修复文件删除响应字段名（`count` -> `deleted_count`）
- 🐛 修复 UTF-8 编码的错误消息解码问题

### Security

- 🔒 使用环境变量存储敏感凭证
- 🔒 支持 `.env` 文件加载配置
- 🔒 请求日志中隐藏敏感信息

---

## 版本说明

### 版本格式

版本号格式：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型

- `Added`: 新增功能
- `Changed`: 功能变更
- `Deprecated`: 即将废弃的功能
- `Removed`: 已移除的功能
- `Fixed`: Bug 修复
- `Security`: 安全相关

[1.0.0]: https://github.com/intsig-textin/docflow-python-sdk/releases/tag/v1.0.0
