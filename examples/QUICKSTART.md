# 快速开始 - 费用报销场景

本指南将带你快速体验 DocFlow SDK 的核心功能，完成一个端到端的费用报销单据处理和审核流程。

## 🎯 场景说明

在费用报销业务中，财务人员需要处理大量不同类型的报销单据：

- **报销申请单**（XLS 格式）- 记录申请人、出差目的、费用明细
- **酒店水单**（图片）- 记录入住日期、离店日期及消费明细
- **支付记录**（图片）- 记录交易流水号、交易金额、收付款方信息

通过 DocFlow，您可以自动完成：
1. ✅ 文档分类识别
2. ✅ 结构化信息抽取
3. ✅ 智能规则审核

## 📋 准备工作

### 1. 安装 SDK

```bash
pip install docflow-sdk
```

### 2. 获取认证信息

登录 [TextIn 控制台](https://www.textin.com/console/dashboard/setting)，获取：

- `x-ti-app-id`
- `x-ti-secret-code`
### 3. 准备样本文件

下载示例样本文件或使用您自己的报销单据，放置在 `sample_files/` 目录下：

```
sample_files/
├── 报销申请单.XLS
├── sample_hotel_receipt.png
└── sample_payment_record.pdf
```

**示例文件下载**：可从项目仓库的 `examples/sample_files/` 目录获取示例文件。

### 4. 配置环境变量

```bash
export DOCFLOW_APP_ID="your-app-id"
export DOCFLOW_SECRET_CODE="your-secret-code"
export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
```

或创建 `.env` 文件：

```ini
DOCFLOW_APP_ID=your-app-id
DOCFLOW_SECRET_CODE=your-secret-code
DOCFLOW_BASE_URL=https://docflow.textin.com/api
```

加载`.env` 配置：

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

## 🚀 运行示例

```bash
cd examples
python quick_start.py
```

## 📊 示例输出

运行成功后，将看到如下输出：

```
======================================================================
  DocFlow SDK 快速开始 - 费用报销场景
======================================================================

[步骤1] 创建工作空间
  ✓ 工作空间创建成功: 123456

[步骤2] 配置文件类别
  [2.1] 创建报销申请单类别...
    ✓ 报销申请单类别ID: 789001
  [2.2] 创建酒店水单类别...
    ✓ 酒店水单类别ID: 789002
    添加表格字段...
    ✓ 添加了 4 个表格字段
  [2.3] 创建支付记录类别...
    ✓ 支付记录类别ID: 789003

  配置完成，类别ID汇总：
    报销申请单: 789001
    酒店水单:   789002
    支付记录:   789003

[步骤3] 上传待处理文件
  ✓ 报销申请单.XLS -> batch_number: 2024...
  ✓ sample_hotel_receipt.png -> batch_number: 2024...
  ✓ sample_payment_record.pdf -> batch_number: 2024...

[步骤4] 获取抽取结果
  等待文件处理完成（可能需要10-30秒）...
  [1/3] ✓ 报销申请单.XLS 处理完成
  [2/3] ✓ sample_hotel_receipt.png 处理完成
  [3/3] ✓ sample_payment_record.pdf 处理完成

  抽取结果摘要：

  文件: 报销申请单.XLS
    类别: 报销申请单
    字段数: 12
      • 申请人: 张三
      • 出差目的: 商务沟通
      • 报销期间: 2024-12-18 至 2024-12-20
      ... 还有 9 个字段

  文件: sample_hotel_receipt.png
    类别: 酒店水单
    字段数: 3
      • 入住日期: 2024-12-18
      • 离店日期: 2024-12-20
      • 总金额: 1,288.00
    表格行数: 2

  文件: sample_payment_record.pdf
    类别: 支付记录
    字段数: 13
      • 交易流水号: 910220250309124124624054
      • 付款方户名: 张三
      • 交易金额: 1288.00
      ... 还有 10 个字段

[步骤5] 配置审核规则库
  [5.1] 创建规则库...
    ✓ 规则库ID: 456789
  [5.2] 创建规则组：报销申请单合规性检查
    ✓ 创建规则: 必填字段完整性校验
    ✓ 创建规则: 报销总金额校验
  [5.3] 创建规则组：差旅费用政策匹配审核
    ✓ 创建规则: 酒店明细合计金额校验
  [5.4] 创建规则组：跨文档交叉审核
    ✓ 创建规则: 跨文档金额匹配
    ✓ 创建规则: 付款人身份与申请人一致性

  规则库配置完成，共创建 3 个规则组、5 条审核规则

[步骤6] 提交审核任务
  ✓ 审核任务提交成功: 987654

[步骤7] 获取审核结果
  等待审核完成（可能需要10-30秒）...
  ✓ 审核完成

======================================================================
  审核结果汇总
======================================================================
任务状态: 审核通过
规则通过数: 5
规则不通过数: 0
规则错误数: 0

详细审核结果：

【报销申请单合规性检查】
  ✓ [🔴 高风险] 必填字段完整性校验
    申请人、费用发生日期、费用项目、申请付款金额均已填写，审核通过。

  ✓ [🔴 高风险] 报销总金额校验
    申请付款总金额 1288.00 等于行申请付款金额合计 1288.00，审核通过。

【差旅费用政策匹配审核】
  ✓ [🟡 中风险] 酒店明细合计金额校验
    明细行金额 644.00 + 644.00 = 1288.00，与总金额一致，审核通过。

【跨文档交叉审核】
  ✓ [🔴 高风险] 跨文档金额匹配
    报销申请单差旅费金额 1288.00 = 酒店水单总金额 1288.00 = 支付记录交易金额 1288.00，审核通过。

  ✓ [🟡 中风险] 付款人身份与申请人一致性
    支付记录付款方户名"张三"与报销申请单申请人"张三"一致，审核通过。

======================================================================
  示例运行完成
======================================================================
后续操作：
1. 访问 DocFlow Web 页面查看详细结果
   https://docflow.textin.com/api
2. 工作空间ID: 123456
3. 规则库ID: 456789
4. 审核任务ID: 987654

提示：工作空间、类别和规则库可以复用，后续只需上传新文件并提交审核任务即可。
```

## 💡 核心代码说明

### 初始化客户端



```python
from docflow import DocflowClient

# 从环境变量自动加载配置
client = DocflowClient.from_env()
```

若使用.env文件方式配置环境变量，需要dotenv依赖：

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

### 创建工作空间

```python
workspace = client.workspace.create(
    name="费用报销",
    auth_scope=1,  # 1=公开, 0=私有
    description="费用报销单据自动化处理空间"
)
workspace_id = workspace.workspace_id
```

### 配置文件类别

```python
from docflow import ExtractModel

category = client.category.create(
    workspace_id=workspace_id,
    name="报销申请单",
    extract_model=ExtractModel.Model_1,
    sample_files=["报销申请单.XLS"],
    fields=[
        {"name": "申请人"},
        {"name": "出差目的"},
        {"name": "费用金额"}
    ]
)
```

### 上传文件

```python
response = client.file.upload(
    workspace_id=workspace_id,
    category="报销申请单",
    file_path="报销申请单.XLS"
)
batch_number = response.batch_number
```

### 查询抽取结果

```python
result = client.file.fetch(
    workspace_id=workspace_id,
    batch_number=batch_number
)

for file in result.files:
    print(f"文件: {file.name}")
    print(f"类别: {file.category}")
    for field in file.data['fields']:
        print(f"  {field['name']}: {field['value']}")
```

### 配置审核规则

```python
# 创建规则库
repo = client.review.create_repo(
    workspace_id=workspace_id,
    name="费用报销审核规则库"
)

# 创建规则组
group = client.review.create_group(
    workspace_id=workspace_id,
    repo_id=repo.repo_id,
    name="合规性检查"
)

# 创建规则
client.review.create_rule(
    workspace_id=workspace_id,
    repo_id=int(repo.repo_id),
    group_id=group.group_id,
    name="必填字段完整性校验",
    prompt="检查申请人、金额等必填字段是否都已填写",
    category_ids=[category_id],
    risk_level=10  # 高风险
)
```

### 提交审核任务

```python
review_task = client.review.submit_task(
    workspace_id=workspace_id,
    name="费用报销审核",
    repo_id=repo.repo_id,
    extract_task_ids=[file.task_id for file in result.files]
)
```

### 获取审核结果

```python
review_result = client.review.get_task_result(
    workspace_id=workspace_id,
    task_id=review_task['task_id']
)

print(f"任务状态: {review_result['status']}")
print(f"规则通过数: {review_result['statistics']['pass_count']}")
```

## 🔄 业务流程图

```
┌─────────────┐
│ 1. 创建工作空间 │
└──────┬──────┘
       ↓
┌─────────────┐
│ 2. 配置类别   │ → 报销申请单、酒店水单、支付记录
└──────┬──────┘
       ↓
┌─────────────┐
│ 3. 上传文件   │ → 批量上传3份单据
└──────┬──────┘
       ↓
┌─────────────┐
│ 4. 获取抽取结果│ → 分类识别 + 字段抽取
└──────┬──────┘
       ↓
┌─────────────┐
│ 5. 配置审核规则│ → 3个规则组、5条规则
└──────┬──────┘
       ↓
┌─────────────┐
│ 6. 提交审核任务│ → 关联抽取任务
└──────┬──────┘
       ↓
┌─────────────┐
│ 7. 获取审核结果│ → 通过/不通过 + 详细依据
└─────────────┘
```

## 📚 下一步

- 📖 查看 [主文档](/README.md)
- 💻 浏览 [更多示例](README.md)
- 🌐 访问 [DocFlow Web 页面](https://docflow.textin.com/)

## ⚠️ 注意事项

1. **工作空间复用**：工作空间、类别和规则库只需配置一次，后续可持续复用
2. **异步处理**：文件上传和审核任务都是异步的，需要轮询等待结果
3. **样本文件**：创建类别时至少需要一个样本文件
4. **审核规则**：跨文档规则需要关联多个类别ID

## 📄 许可证

MIT License
