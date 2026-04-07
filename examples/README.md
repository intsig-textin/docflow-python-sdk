# Docflow SDK 示例代码

本目录包含 Docflow Python SDK 的详细使用示例,涵盖所有主要功能和实际业务场景。

> 🚀 **新手推荐**：如果您是第一次使用，建议先查看 [快速开始指南 - 费用报销场景](QUICKSTART.md)，快速体验完整的端到端流程！

## 📁 文件说明

### 快速开始

| 文件 | 说明 | 推荐指数 |
|------|------|---------|
| [quick_start.py](quick_start.py) | 🌟 费用报销场景快速开始 | ⭐⭐⭐⭐⭐ |

**适合人群**：第一次使用 DocFlow SDK 的用户  
**包含内容**：创建空间 → 配置类别 → 上传文件 → 抽取结果 → 配置审核 → 审核结果  
**运行时间**：约 2-3 分钟  

### 基础示例

| 文件 | 说明 | 包含示例数量 |
|------|------|--------------|
| [quick_start.py](quick_start.py) | 文件处理流程快速启动示例 | 1个 |
| [review_examples.py](review_examples.py) | 审核规则资源完整示例 | 22个 |
| [complete_workflow_example.py](complete_workflow_example.py) | 端到端业务流程示例 | 3个场景 |
| [file_examples.py](file_examples.py) | 文件处理资源完整示例 | 17个 |
| [review_examples.py](review_examples.py) | 审核规则资源完整示例 | 22个 |
| [complete_workflow_example.py](complete_workflow_example.py) | 端到端业务流程示例 | 3个场景 |

## 🚀 快速开始

### 1. 设置环境变量

运行示例前,需要先配置环境变量:

```bash
export DOCFLOW_APP_ID="your-app-id"
export DOCFLOW_SECRET_CODE="your-secret-code"
export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
```

或者创建 `.env` 文件:

```ini
DOCFLOW_APP_ID=your-app-id
DOCFLOW_SECRET_CODE=your-secret-code
DOCFLOW_BASE_URL=https://docflow.textin.com/api
```

### 2. 安装依赖

```bash
pip install -e .
```

### 3. 运行示例

```bash
# 运行快速启动示例
python examples/quick_start.py

# 运行文件处理示例
python examples/file_examples.py

# 运行审核规则示例
python examples/review_examples.py

# 运行完整工作流程示例
python examples/complete_workflow_example.py
```

## 📖 示例详解

### 快速启动示例 (quick_start.py)

费用报销场景快速开始指南，参考 [快速启动指南](QUICKSTART.md)

### 文件处理示例 (file_examples.py)

涵盖文件资源的所有操作:

**基础功能 (4个示例)**
- 示例1: 上传本地文件(异步)
- 示例2: 通过URL上传文件
- 示例3: 同步上传并等待处理完成
- 示例4: 上传时配置解析参数

**查询功能 (4个示例)**
- 示例5: 查询文件列表
- 示例6: 使用过滤条件查询
- 示例7: 查询特定文件
- 示例8: 迭代所有文件(自动分页)

**更新功能 (2个示例)**
- 示例9: 更新文件处理结果
- 示例10: 批量更新多个文件

**高级功能 (5个示例)**
- 示例11: 抽取额外字段
- 示例12: 抽取表格字段
- 示例13: 重新处理文件
- 示例14: 修改文件类别
- 示例15: 修改拆分任务的类别

**删除与流程 (2个示例)**
- 示例16: 删除文件
- 示例17: 完整工作流程

### 审核规则示例 (review_examples.py)

涵盖审核规则资源的所有操作:

**规则库管理 (5个示例)**
- 示例1: 创建审核规则库
- 示例2: 获取审核规则库列表
- 示例3: 获取审核规则库详情
- 示例4: 更新审核规则库
- 示例5: 删除审核规则库

**规则组管理 (3个示例)**
- 示例6: 创建审核规则组
- 示例7: 更新审核规则组
- 示例8: 删除审核规则组

**规则管理 (5个示例)**
- 示例9: 创建审核规则
- 示例10: 创建带引用字段的审核规则
- 示例11: 创建引用表格字段的审核规则
- 示例12: 更新审核规则
- 示例13: 删除审核规则

**任务管理 (7个示例)**
- 示例14: 提交审核任务
- 示例15: 按批次提交审核任务
- 示例16: 获取审核任务结果
- 示例17: 简化的审核结果查询
- 示例18: 重新执行审核任务
- 示例19: 重新执行任务中的某条规则
- 示例20: 删除审核任务

**完整流程 (2个示例)**
- 示例21: 完整的审核工作流程
- 示例22: 使用链式调用进行审核操作

### 完整工作流程示例 (complete_workflow_example.py)

展示三个端到端的业务场景:

**场景1: 发票批量处理流程**
1. 创建工作空间
2. 创建发票类别(含字段和表格)
3. 批量上传发票文件
4. 查询处理结果
5. 数据验证和修正

**场景2: 发票审核流程**
1. 创建审核规则库
2. 配置审核规则
3. 提交审核任务
4. 查询审核结果
5. 处理审核不通过的文件

**场景3: 使用链式调用优化代码**
展示如何使用链式调用来:
- 简化工作空间操作
- 简化类别操作
- 简化审核规则操作

## 💡 最佳实践

### 1. 错误处理

所有示例都包含适当的错误处理:

```python
try:
    response = client.file.upload(
        workspace_id="123",
        file_path="/path/to/file.pdf"
    )
    print(f"上传成功: {response.files[0].id}")
except ValidationError as e:
    print(f"参数错误: {e}")
except APIError as e:
    print(f"API错误: {e}")
```

### 2. 使用枚举类型

推荐使用枚举类型而非硬编码字符串:

```python
from docflow import ExtractModel, FieldType, AuthScope

# ✅ 推荐
extract_model=ExtractModel.Model_1
field_type=FieldType.DATETIME

# ❌ 不推荐
extract_model="Model 1"
field_type="datetime"
```

### 3. 链式调用

使用链式调用减少重复代码:

```python
# 传统方式
client.category.fields.add(workspace_id="123", category_id="456", name="字段1")
client.category.fields.add(workspace_id="123", category_id="456", name="字段2")

# 链式调用
ws = client.workspace("123")
cat = ws.category("456")
cat.fields.add(name="字段1")
cat.fields.add(name="字段2")
```

### 4. 自动分页

使用迭代器自动处理分页:

```python
# 内存高效的方式
for file in client.file.iter(workspace_id="123"):
    process(file)
    if should_stop:
        break  # 可以随时中断

# 或转换为列表
all_files = list(client.file.iter(workspace_id="123", max_pages=10))
```

### 5. 批量操作

批量处理可以提高效率:

```python
# 批量更新
updates = [
    {"workspace_id": "123", "file_id": "456", "data": {...}},
    {"workspace_id": "123", "file_id": "789", "data": {...}},
]
client.file.batch_update(updates=updates)
```

## 🤝 贡献

欢迎提交更多示例! 如果你有好的使用场景,请提交 Pull Request。

## 📄 许可证

MIT License
