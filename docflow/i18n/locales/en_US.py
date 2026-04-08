"""
English (US) Translation
"""

TRANSLATIONS = {
    # General errors
    'error.unknown': 'Unknown error',
    'error.network': 'Network error',
    'error.timeout': 'Request timeout',
    'error.connection_failed': 'Network connection failed',

    # Authentication errors
    'error.auth.failed': 'Authentication failed, please check app_id and secret_code',
    'error.auth.invalid_credentials': 'Invalid credentials',
    'error.auth.missing_credentials': 'app_id and secret_code are required',

    # Permission errors
    'error.permission.denied': 'Permission denied',
    'error.permission.forbidden': 'Forbidden',

    # Resource errors
    'error.resource.not_found': 'Resource not found',
    'error.resource.already_exists': 'Resource already exists',

    # Validation errors
    'error.validation.failed': 'Validation failed',
    'error.validation.empty': '{field} cannot be empty',
    'error.validation.too_long': '{field} cannot exceed {max_length} characters',
    'error.validation.invalid_format': '{field} format is invalid',
    'error.validation.invalid_value': '{field} value is invalid',
    'error.validation.out_of_range': '{field} must be between {min} and {max}',

    # Workspace related
    'error.workspace.name_empty': 'Workspace name cannot be empty',
    'error.workspace.name_too_long': 'Workspace name cannot exceed {max_length} characters',
    'error.workspace.id_empty': 'Workspace ID cannot be empty',
    'error.workspace.id_invalid': 'Workspace ID format is invalid',
    'error.workspace.not_found': 'Workspace not found',
    'error.workspace.auth_scope_invalid': 'auth_scope must be 0 or 1',
    'error.workspace.delete_list_empty': 'workspace_ids cannot be empty',
    'error.workspace.page_invalid': 'Page number must be greater than or equal to 1',
    'error.workspace.page_size_invalid': 'Page size must be between 1 and 100',
    'error.workspace.callback_retry_time_invalid': 'Callback retry time must be between 1 and 3',

    # Category related
    'error.category.name_invalid': 'Category name cannot be empty and must not exceed 50 characters',
    'error.category.extract_model_invalid': 'extract_model must be ExtractModel.Model_1(\'Model 1\') or ExtractModel.Model_2(\'Model 2\') or ExtractModel.Model_3(\'Model 3\')',
    'error.category.sample_files_empty': 'At least one sample file is required',
    'error.category.fields_empty': 'At least one field configuration is required',
    'error.category.prompt_too_long': 'Category prompt must not exceed 150 characters',
    'error.category.enabled_invalid': 'enabled must be EnabledStatus.ALL/DISABLED/ENABLED/OTHER or corresponding string value',
    'error.category.enabled_flag_invalid': 'enabled must be EnabledFlag.DISABLED(0) or EnabledFlag.ENABLED(1)',
    'error.category.delete_list_empty': 'category_ids cannot be empty',
    'error.category.id_empty': 'Category ID cannot be empty',
    'error.category.id_invalid': 'Category ID must be a numeric string',

    # Table related
    'error.table.name_empty': 'Table name cannot be empty',
    'error.table.delete_list_empty': 'table_ids cannot be empty',

    # Field related
    'error.field.name_empty': 'Field name cannot be empty',
    'error.field.delete_list_empty': 'field_ids cannot be empty',

    # Sample related
    'error.sample.delete_list_empty': 'sample_ids cannot be empty',
    'error.sample.missing_content_disposition': 'Content-Disposition header is missing, cannot retrieve filename',
    'error.sample.cannot_extract_filename': 'Cannot extract filename from Content-Disposition header',

    # Review task related
    'error.review_task.name_empty': 'Task name cannot be empty',
    'error.review_task.name_too_long': 'Task name cannot exceed {max_length} characters',
    'error.review_task.id_empty': 'Review task ID cannot be empty',
    'error.review_task.id_invalid': 'Review task ID must be a numeric string',
    'error.review_task.delete_list_empty': 'task_ids cannot be empty',
    'error.review_task.repo_id_empty': 'Review rule repository ID cannot be empty',
    'error.review_task.repo_id_invalid': 'Review rule repository ID must be a numeric string',
    'error.review_task.rule_id_empty': 'Review rule ID cannot be empty',
    'error.review_task.rule_id_invalid': 'Review rule ID must be a numeric string',

    # File upload related
    'error.file.upload_source_required': 'Either file_path or file_urls must be provided',
    'error.file.upload_source_conflict': 'file_path and file_urls cannot be provided at the same time',
    'error.file.urls_empty': 'file_urls cannot be an empty list',
    'error.file.urls_too_many': 'file_urls supports a maximum of {max_count} URLs',

    # API errors
    'error.api.request_failed': 'API request failed',
    'error.api.response_parse_failed': 'Failed to parse response',
    'error.api.invalid_response': 'Invalid response format',

    # HTTP status codes
    'error.http.400': 'Bad request',
    'error.http.401': 'Unauthorized',
    'error.http.403': 'Forbidden',
    'error.http.404': 'Not found',
    'error.http.423': 'Locked',
    'error.http.429': 'Too many requests',
    'error.http.500': 'Internal server error',
    'error.http.502': 'Bad gateway',
    'error.http.503': 'Service unavailable',
    'error.http.504': 'Gateway timeout',
    'error.http.900': 'Business error',

    # Retry related
    'retry.attempt': 'Retrying... (attempt {count})',
    'retry.failed': 'Retry failed, maximum retry attempts reached',
    'retry.success': 'Retry successful',

    # Configuration related
    'config.language_changed': 'Language changed to: {language}',
    'config.language_not_supported': 'Language not supported: {language}',

    # Client related
    'client.initialized': 'SDK client initialized successfully',
    'client.closed': 'SDK client closed',

    # Logging related
    'log.request_sent': 'Sending request: {method} {url}',
    'log.request_completed': 'Request completed: {method} {url}, status: {status_code}, time: {elapsed}s',
    'log.retry_warning': 'Request failed, retrying: {method} {url}',
}
