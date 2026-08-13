# Docflow Python SDK

[简体中文](README.md) | [English](README.en.md)

Docflow Python SDK provides a concise, Pythonic API for integrating Docflow document processing and review capabilities.

## 📋 Features

- Workspace, category, field, table, and sample management
- File upload, extraction, update, retry, category amendment, and deletion
- Review repository, rule group, rule, and task management
- Type annotations and enums for safer API calls
- Chinese (`zh_CN`) and English (`en_US`) error messages
- Configurable retries with exponential backoff
- HTTP connection pooling
- Context-bound chained calls that reduce repeated arguments
- Memory-efficient automatic pagination
- Configuration through environment variables
- Batch operations for fields, tables, and samples

## 📦 Installation

### Install from PyPI (recommended)

```bash
pip install docflow-sdk
```

### Install from GitHub

```bash
pip install git+https://github.com/intsig-textin/docflow-python-sdk.git
```

### Install from source

```bash
git clone https://github.com/intsig-textin/docflow-python-sdk.git
cd docflow-python-sdk
pip install -e .
```

## 🚀 Quick Start

> For an end-to-end expense reimbursement workflow, see the [Quick Start guide](examples/QUICKSTART.en.md).

### 1. Initialize the client

```python
from docflow import DocflowClient

# Use the default base URL.
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
)

# Or load configuration from environment variables.
client = DocflowClient.from_env()

# Or specify a custom endpoint.
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    base_url="https://custom.api.com/api",
)
```

The default endpoint is `https://docflow.textin.com/api`.

### 2. Manage workspaces

```python
from docflow import AuthScope

workspace = client.workspace.create(
    name="My Workspace",
    auth_scope=AuthScope.PUBLIC,
)

workspaces = client.workspace.list(page=1, page_size=20)
detail = client.workspace.get(workspace_id=workspace.workspace_id)

client.workspace.update(
    workspace_id=workspace.workspace_id,
    name="Updated Workspace",
    auth_scope=AuthScope.PRIVATE,
)

client.workspace.delete(workspace_ids=[workspace.workspace_id])
```

### 3. Manage categories

```python
from docflow import ExtractModel, FieldType

category = client.category.create(
    workspace_id="123",
    name="Invoices",
    extract_model=ExtractModel.Acgpt,
    sample_files=["/path/to/sample.pdf"],
    fields=[
        {"name": "Invoice Number", "description": "Unique invoice ID"},
        {
            "name": "Invoice Date",
            "transform_settings": {
                "type": FieldType.DATETIME.value,
                "datetime_settings": {"format": "yyyy-MM-dd"},
            },
        },
    ],
    tables=[
        {
            "name": "Line Items",
            "prompt": "Extract each line item",
            "extract_model": "Acgpt",
            "fields": [
                {"name": "Date"},
                {"name": "Type"},
                {"name": "Amount"},
            ],
        }
    ],
)
```

List, update, and delete categories through `client.category.list()`, `client.category.update()`, and `client.category.delete()`.

### 4. Manage fields, tables, and samples

```python
# Add a field.
field = client.category.fields.add(
    workspace_id="123",
    category_id="456",
    name="Tax Rate",
)

# Batch-add fields.
client.category.fields.batch_add(
    workspace_id="123",
    category_id="456",
    fields=[{"name": "Subtotal"}, {"name": "Total"}],
    with_detail=True,
)

# Batch-add tables with embedded fields.
client.category.tables.batch_add(
    workspace_id="123",
    category_id="456",
    tables=[
        {
            "name": "Details",
            "fields": [{"name": "Item"}, {"name": "Amount"}],
        }
    ],
    with_detail=True,
)

# Upload and download samples in batches.
client.category.samples.batch_upload(
    workspace_id="123",
    category_id="456",
    file_paths=["sample1.pdf", "sample2.pdf"],
)
client.category.samples.batch_download(
    workspace_id="123",
    category_id="456",
    sample_ids=["sample-1", "sample-2"],
    save_path="samples.zip",
)
```

### 5. Use chained contexts

Context-bound calls avoid repeatedly passing workspace and category IDs.

```python
ws = client.workspace("123")
cat = ws.category("456")

cat.fields.add(name="Field 1")
cat.fields.add(name="Field 2")
cat.tables.list()
cat.samples.list()

ws.update(name="Updated Workspace")
cat.update(name="Updated Category")
```

### 6. Iterate through paginated resources

```python
# Iterate lazily and stop whenever needed.
for file_info in client.file.iter(workspace_id="123"):
    print(file_info.id)

# Materialize all results.
all_workspaces = list(client.workspace.iter())

# Limit the number of pages.
categories = list(client.category.iter(workspace_id="123", max_pages=5))
```

### 7. Use enums

The SDK exposes enums including:

- `ExtractModel`: `Auto`, `Acgpt`, `Acgpt_VL`, and `DF_M1`
- `AuthScope`: workspace access scope
- `EnabledStatus`: query-time enabled status
- `EnabledFlag`: update-time enabled flag
- `FieldType`: field transformation type
- `MismatchAction`: behavior for mismatched field values
- `ReviewModel`: review model selection

Legacy `ExtractModel.Model_1`, `Model_2`, and `Model_3` values remain available as deprecated compatibility aliases.

### 8. Handle errors

```python
from docflow import APIError, AuthenticationError, DocflowError, ValidationError

try:
    client.workspace.get(workspace_id="123")
except ValidationError as exc:
    print(f"Invalid input: {exc}")
except AuthenticationError as exc:
    print(f"Authentication failed: {exc}")
except APIError as exc:
    print(f"API request failed: {exc}")
except DocflowError as exc:
    print(f"Docflow error: {exc}")
```

### 9. Use the client as a context manager

```python
with DocflowClient(app_id="your-app-id", secret_code="your-secret-code") as client:
    workspaces = client.workspace.list()
```

## 📖 API Overview

### `DocflowClient`

Important constructor parameters include `app_id`, `secret_code`, `base_url`, `language`, timeout settings, and retry settings. Use `from_env()` to read supported environment variables.

Primary resources:

- `client.workspace`: workspace operations
- `client.category`: category, field, table, and sample operations
- `client.file`: file processing operations
- `client.review`: review configuration and task operations

### Fetch page images and translate recognition results

```python
# Keep Snowflake task IDs as strings. image_url values are valid for 30 days.
files = client.file.fetch(
    workspace_id="123",
    task_id="1978297791713619968",
    with_image_url=True,
)

# Omit source_language or send an empty string for automatic detection.
translations = client.file.translate(
    task_id="1978297791713619968",
    source_language="",
    target_language="en",
)

# Disable translated-result display without deleting stored translations.
client.file.translate(
    task_id="1978297791713619968",
    target_language="en",
    open_translate=0,
)
```

Existing `/file/fetch` fields remain compatible: table names still use `tableName`, while new
translation fields use the `translated_*` naming convention. Translation responses contain
`fields`, `tables`, `stamps`, and `handwritings`.

### `WorkspaceResource`

- `create()`: create a workspace
- `list()`: list workspaces with pagination
- `get()`: fetch workspace details
- `update()`: update workspace metadata and access scope
- `delete()`: delete one or more workspaces
- `iter()`: iterate through all pages

## 🔧 Configuration

### Environment variables

```bash
export DOCFLOW_APP_ID="your-app-id"
export DOCFLOW_SECRET_CODE="your-secret-code"
export DOCFLOW_BASE_URL="https://docflow.textin.com/api"
```

To load a local `.env` file in your application, install `python-dotenv` and call `load_dotenv()` before creating the client. Do not commit credentials or `.env` files.

## 🌍 Internationalization

Supported error-message languages:

- Simplified Chinese: `zh_CN` (default)
- English: `en_US`

```python
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    language="en_US",
)

client.set_language("zh_CN")
print(client.get_language())
print(client.get_available_languages())
```

## 🔄 Retry Behavior

By default, the SDK retries status codes `423`, `429`, `500`, `503`, `504`, and `900` for `GET`, `POST`, `PUT`, `DELETE`, and `PATCH` requests. The default maximum retry count is 3 and the default backoff factor is 1.0.

```python
# Custom retry count and timeout.
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    max_retries=5,
    timeout=60,
)

# Disable retries.
client = DocflowClient(
    app_id="your-app-id",
    secret_code="your-secret-code",
    max_retries=0,
)
```

Validation, authentication, and other non-transient client errors are not retried.

## 🧪 Run the Examples

```bash
export DOCFLOW_APP_ID="your-app-id"
export DOCFLOW_SECRET_CODE="your-secret-code"

python examples/quick_start.py
python examples/complete_workflow_example.py
python examples/file_examples.py
python examples/review_examples.py
```

See the [examples guide](examples/README.en.md) for details.

## 🔒 Security Recommendations

- Keep credentials in environment variables or a secrets manager.
- Never hard-code or commit API keys and tokens.
- Use HTTPS endpoints.
- Rotate credentials regularly.
- Avoid logging credentials or sensitive document content.

## 🚀 Publishing a New Version

1. Update the version in `pyproject.toml`, `docflow/__init__.py`, and `setup.py`.
2. Add release notes to `CHANGELOG.md` and `CHANGELOG.en.md`.
3. Commit and push the changes.
4. Create and push a version tag, for example `git tag -a v1.1.0 -m "Release v1.1.0"`.

Keep all version declarations synchronized and follow semantic versioning.

## 🤝 Contributing

Issues and pull requests are welcome. Please include tests and update both language versions of affected documentation.

## 📄 License

See [LICENSE](LICENSE) for license information.
