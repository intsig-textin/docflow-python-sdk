# Docflow SDK Examples

[简体中文](README.md) | [English](README.en.md)

This directory contains detailed Docflow Python SDK examples covering the primary features and practical workflows.

> New users should start with the [expense reimbursement quick-start guide](QUICKSTART.en.md) for a complete end-to-end workflow.

## 📁 Files

### Recommended starting point

| English | 中文版 | Description | Recommendation |
|---------|--------|-------------|----------------|
| [quick_start_en.py](quick_start_en.py) | [quick_start.py](quick_start.py) | Expense reimbursement quick start | ⭐⭐⭐⭐⭐ |

This example creates a workspace, configures categories, uploads files, reads extraction results, configures review rules, and reads review results. It normally takes about 2–3 minutes, excluding service-side processing time.

### Examples

| English | 中文版 | Description | Coverage |
|---------|--------|-------------|----------|
| [quick_start_en.py](quick_start_en.py) | [quick_start.py](quick_start.py) | Quick file-processing workflow | 1 workflow |
| [file_examples_en.py](file_examples_en.py) | [file_examples.py](file_examples.py) | Complete file resource examples | 17 examples |
| [review_examples_en.py](review_examples_en.py) | [review_examples.py](review_examples.py) | Complete review resource examples | 22 examples |
| [complete_workflow_example_en.py](complete_workflow_example_en.py) | [complete_workflow_example.py](complete_workflow_example.py) | End-to-end business workflows | 3 scenarios |
| [split_config_example_en.py](split_config_example_en.py) | [split_config_example.py](split_config_example.py) | Read and safely update split configuration | 1 example |

## 🚀 Getting Started

### 1. Configure environment variables

```bash
export DOCFLOW_APP_ID="your-app-id"
export DOCFLOW_SECRET_CODE="your-secret-code"
export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
```

If your application loads a local `.env` file, keep it out of version control:

```python
from dotenv import load_dotenv
import os

load_dotenv()

client = DocflowClient(
    base_url=os.getenv("DOCFLOW_BASE_URL"),
    app_id=os.getenv("DOCFLOW_APP_ID"),
    secret_code=os.getenv("DOCFLOW_SECRET_CODE"),
)
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Run an example

```bash
python examples/quick_start_en.py
python examples/file_examples_en.py
python examples/review_examples_en.py
python examples/complete_workflow_example_en.py
python examples/split_config_example_en.py
```

## 📖 Example Details

### Quick start (`quick_start_en.py`)

Implements an expense reimbursement workflow. See the [Quick Start guide](QUICKSTART.en.md).

### File processing (`file_examples_en.py`)

- Basic operations: local, URL, synchronous, and parameterized uploads
- Queries: lists, filters, individual files, and automatic pagination
- Updates: single and batch result updates
- Advanced operations: extra fields, table fields, retry, and category amendment
- Deletion and a complete file workflow

### Review rules (`review_examples_en.py`)

- Review repositories: create, list, fetch, update, and delete
- Rule groups: create, update, and delete
- Rules: regular rules, field references, table-field references, updates, and deletion
- Tasks: submit by file or batch, fetch results, retry tasks or rules, and delete tasks
- Complete and chained review workflows

### Complete workflows (`complete_workflow_example_en.py`)

The three scenarios demonstrate:

1. Batch invoice processing: create a workspace and invoice category, upload files, query results, and correct data.
2. Invoice review: create a rule repository, configure rules, submit a review, query results, and handle failures.
3. Chained calls: simplify workspace, category, and review operations with bound contexts.

## 💡 Best Practices

### Error handling

```python
try:
    response = client.file.upload(
        workspace_id="123",
        file_path="/path/to/file.pdf",
    )
    print(f"Upload succeeded: {response.files[0].id}")
except ValidationError as exc:
    print(f"Invalid input: {exc}")
except APIError as exc:
    print(f"API error: {exc}")
```

### Prefer enums

```python
from docflow import AuthScope, ExtractModel, FieldType

extract_model = ExtractModel.Acgpt
field_type = FieldType.DATETIME
auth_scope = AuthScope.PUBLIC
```

### Use chained contexts

```python
ws = client.workspace("123")
cat = ws.category("456")

cat.fields.add(name="Field 1")
cat.fields.add(name="Field 2")
```

### Use automatic pagination

```python
for file_info in client.file.iter(workspace_id="123"):
    process(file_info)

all_files = list(client.file.iter(workspace_id="123"))
```

### Prefer batch operations

Use batch field, table, sample, and file methods when processing multiple items. This reduces network round trips while preserving consistent server-side behavior.

## 🤝 Contributing 

When adding an example, update both `README.md` and `README.en.md`. Never commit credentials or sample documents containing sensitive data.

## 📄 License

See [LICENSE](../LICENSE) for license information.
