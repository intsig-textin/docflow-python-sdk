"""English examples for the Docflow file resource.

Set DOCFLOW_APP_ID, DOCFLOW_SECRET_CODE, and optionally DOCFLOW_BASE_URL
before running this module. Replace placeholder IDs and file paths with values
from your own workspace.
"""

import os
import time

from dotenv import load_dotenv

from docflow import DocflowClient


def setup_client():
    """Create a client from environment variables."""
    load_dotenv()
    return DocflowClient.from_env()


client = setup_client()
WORKSPACE_ID = os.getenv("DOCFLOW_WORKSPACE_ID", "123")


def example_upload_local_file():
    """Example 1: upload a local file asynchronously."""
    print("\n=== Example 1: Upload a local file ===")
    response = client.file.upload(
        workspace_id=WORKSPACE_ID,
        category="Invoice",
        file_path="/path/to/invoice.pdf",
    )
    print(f"Batch number: {response.batch_number}")
    for file_info in response.files:
        print(f"Uploaded {file_info.name}; task ID: {file_info.task_id}")


def example_upload_from_url():
    """Example 2: upload one or more files from URLs."""
    print("\n=== Example 2: Upload files from URLs ===")
    response = client.file.upload(
        workspace_id=WORKSPACE_ID,
        category="Contract",
        file_urls=[
            "https://example.com/contract1.pdf",
            "https://example.com/contract2.pdf",
        ],
        batch_number="202607220001",
    )
    print(f"Created batch {response.batch_number} with {len(response.files)} files")


def example_upload_sync():
    """Example 3: upload a file and wait for processing."""
    print("\n=== Example 3: Upload synchronously ===")
    result = client.file.upload_sync(
        workspace_id=WORKSPACE_ID,
        category="Invoice",
        file_path="/path/to/invoice.pdf",
        with_task_detail_url=True,
    )
    for file_info in result.files:
        print(f"{file_info.name}: status={file_info.recognition_status}")
        if file_info.task_detail_url:
            print(f"Task details: {file_info.task_detail_url}")


def example_upload_with_parser_params():
    """Example 4: configure parsing options during upload."""
    print("\n=== Example 4: Upload with parser options ===")
    response = client.file.upload(
        workspace_id=WORKSPACE_ID,
        file_path="/path/to/paper.pdf",
        parser_remove_watermark=1,
        parser_crop_dewarp=1,
        parser_apply_merge=1,
        parser_formula_level=1,
        parser_table_text_split_mode=1,
        parser_dpi=144,
        parser_parse_mode="auto",
    )
    print(f"Upload accepted; batch number: {response.batch_number}")


def example_fetch_files():
    """Example 5: fetch a page of processed files."""
    print("\n=== Example 5: Fetch files ===")
    response = client.file.fetch(
        workspace_id=WORKSPACE_ID,
        page=1,
        page_size=20,
        with_document=False,
        with_task_detail_url=True,
    )
    print(f"Total files: {response.total}")
    for file_info in response.files:
        print(f"{file_info.id}: {file_info.name} ({file_info.recognition_status})")


def example_fetch_with_filters():
    """Example 6: query files with filters."""
    print("\n=== Example 6: Fetch files with filters ===")
    response = client.file.fetch(
        workspace_id=WORKSPACE_ID,
        batch_number="202607220001",
        category="Invoice",
        recognition_status=1,
        page=1,
        page_size=100,
    )
    print(f"Matched files: {response.total}")


def example_fetch_by_file_id():
    """Example 7: fetch one file by ID."""
    print("\n=== Example 7: Fetch a file by ID ===")
    response = client.file.fetch(
        workspace_id=WORKSPACE_ID,
        file_id="789012",
        with_document=True,
    )
    if response.files:
        print(f"File: {response.files[0].name}")


def example_fetch_by_task_id_with_images():
    """Fetch page images and translated values for one task."""
    response = client.file.fetch(
        workspace_id=WORKSPACE_ID,
        task_id="1978297791713619968",  # Keep Snowflake IDs as strings.
        with_image_url=True,
    )
    for file_info in response.files:
        for page in file_info.pages or []:
            print(page.get("image_url"))  # Image URLs are valid for 30 days.
        # Existing table names remain tableName; translations use translated_table_name.
        for table in (file_info.data or {}).get("tables", []):
            print(table.get("tableName"), table.get("translated_table_name"))


def example_translate_file():
    """Translate recognition results."""
    result = client.file.translate(
        task_id="1978297791713619968",
        source_language="",  # Omit or send an empty string for auto detection.
        target_language="en",
    )
    print(len(result.fields), len(result.tables), len(result.stamps), len(result.handwritings))


def example_iterate_files():
    """Example 8: iterate through every result page lazily."""
    print("\n=== Example 8: Iterate through files ===")
    for file_info in client.file.iter(
        workspace_id=WORKSPACE_ID,
        page_size=100,
        max_pages=5,
    ):
        print(f"{file_info.id}: {file_info.name}")


def example_update_file():
    """Example 9: correct extracted fields for one file."""
    print("\n=== Example 9: Update a file ===")
    response = client.file.update(
        workspace_id=WORKSPACE_ID,
        file_id="789012",
        data={
            "fields": [
                {"name": "Invoice Number", "value": "INV-2026-001"},
                {"name": "Total Amount", "value": "1288.00"},
            ],
            "items": [],
        },
    )
    print(f"Updated files: {len(response.files)}")


def example_batch_update_files():
    """Example 10: update multiple files in one request."""
    print("\n=== Example 10: Batch-update files ===")
    updates = [
        {
            "workspace_id": WORKSPACE_ID,
            "file_id": "789012",
            "data": {"fields": [{"name": "Total Amount", "value": "1288.00"}]},
        },
        {
            "workspace_id": WORKSPACE_ID,
            "file_id": "789013",
            "data": {"fields": [{"name": "Total Amount", "value": "688.00"}]},
        },
    ]
    response = client.file.batch_update(updates=updates)
    print(f"Updated files: {len(response.files)}")


def example_extract_fields():
    """Example 11: extract additional fields from an existing task."""
    print("\n=== Example 11: Extract additional fields ===")
    result = client.file.extract_fields(
        workspace_id=WORKSPACE_ID,
        task_id="987654",
        fields=[
            {"key": "Purchase Order Number", "prompt": "Extract the purchase order number."},
            {"key": "Payment Terms", "prompt": "Extract the payment terms."},
        ],
    )
    print(f"Files returned: {len(result.files)}")


def example_extract_table_fields():
    """Example 12: extract a table and its columns."""
    print("\n=== Example 12: Extract table fields ===")
    result = client.file.extract_fields(
        workspace_id=WORKSPACE_ID,
        task_id="987654",
        tables=[{
            "name": "Line Items",
            "fields": [
                {"key": "Description"},
                {"key": "Quantity"},
                {"key": "Unit Price"},
                {"key": "Amount"},
            ],
        }],
    )
    print(f"Files returned: {len(result.files)}")


def example_retry_file():
    """Example 13: retry processing with optional parser settings."""
    print("\n=== Example 13: Retry a file ===")
    client.file.retry(
        workspace_id=WORKSPACE_ID,
        task_id="987654",
        parser_params={"remove_watermark": True, "formula_level": 1},
    )
    print("Retry submitted")


def example_amend_category():
    """Example 14: change the category of a processed file."""
    print("\n=== Example 14: Amend a category ===")
    client.file.amend_category(
        workspace_id=WORKSPACE_ID,
        task_id="987654",
        category="Contract",
    )
    print("Category amended")


def example_amend_category_with_split():
    """Example 15: assign categories to split document ranges."""
    print("\n=== Example 15: Amend split-task categories ===")
    client.file.amend_category(
        workspace_id=WORKSPACE_ID,
        task_id="987654",
        split_tasks=[
            {"category": "Invoice", "pages": [0, 1]},
            {"category": "Contract", "pages": [2, 3, 4]},
        ],
    )
    print("Split-task categories amended")


def example_delete_files():
    """Example 16: delete files by file ID, task ID, or batch number."""
    print("\n=== Example 16: Delete files ===")
    response = client.file.delete(
        workspace_id=WORKSPACE_ID,
        file_id=["789012", "789013"],
    )
    print(f"Deleted files: {response.deleted_count}")


def example_complete_workflow():
    """Example 17: upload, poll, inspect, and optionally retry files."""
    print("\n=== Example 17: Complete file workflow ===")
    paths = [
        "/path/to/invoice1.pdf",
        "/path/to/invoice2.pdf",
        "/path/to/invoice3.pdf",
    ]
    task_ids = []
    for path in paths:
        response = client.file.upload(
            workspace_id=WORKSPACE_ID,
            category="Invoice",
            file_path=path,
        )
        task_ids.extend(item.task_id for item in response.files if item.task_id)

    for attempt in range(12):
        response = client.file.fetch(workspace_id=WORKSPACE_ID, page_size=100)
        relevant = [item for item in response.files if item.task_id in task_ids]
        pending = [item for item in relevant if item.recognition_status in (0, 3, 4, 5)]
        print(f"Polling attempt {attempt + 1}: {len(pending)} files still processing")
        if not pending:
            break
        time.sleep(5)

    for item in relevant:
        if item.recognition_status == 2:
            print(f"Processing failed for {item.name}: {item.failure_causes}")
        else:
            print(f"Processing completed for {item.name}")


if __name__ == "__main__":
    print("Docflow file resource examples (English)")
    print("Run individual example functions after replacing placeholder values.")
    example_fetch_files()
