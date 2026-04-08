"""
中文（简体）翻译
"""

TRANSLATIONS = {
    # 通用错误
    'error.unknown': '未知错误',
    'error.network': '网络错误',
    'error.timeout': '请求超时',
    'error.connection_failed': '网络连接失败',

    # 认证错误
    'error.auth.failed': '认证失败，请检查 app_id 和 secret_code',
    'error.auth.invalid_credentials': '无效的认证凭证',
    'error.auth.missing_credentials': '必须提供 app_id 和 secret_code',

    # 权限错误
    'error.permission.denied': '权限不足',
    'error.permission.forbidden': '禁止访问',

    # 资源错误
    'error.resource.not_found': '资源不存在',
    'error.resource.already_exists': '资源已存在',

    # 参数校验错误
    'error.validation.failed': '参数校验失败',
    'error.validation.empty': '{field} 不能为空',
    'error.validation.too_long': '{field} 长度不能超过 {max_length} 个字符',
    'error.validation.invalid_format': '{field} 格式错误',
    'error.validation.invalid_value': '{field} 值无效',
    'error.validation.out_of_range': '{field} 必须在 {min} 到 {max} 之间',

    # 工作空间相关
    'error.workspace.name_empty': '工作空间名称不能为空',
    'error.workspace.name_too_long': '工作空间名称不能超过 {max_length} 个字符',
    'error.workspace.description_too_long': '工作空间描述不能超过 {max_length} 个字符',
    'error.workspace.id_empty': '工作空间 ID 不能为空',
    'error.workspace.id_invalid': '工作空间 ID 格式错误',
    'error.workspace.not_found': '工作空间不存在',
    'error.workspace.auth_scope_invalid': 'auth_scope 只能是 0 或 1',
    'error.workspace.delete_list_empty': 'workspace_ids 不能为空',
    'error.workspace.page_invalid': '页码必须大于等于 1',
    'error.workspace.page_size_invalid': '每页数量必须在 1-100 之间',
    'error.workspace.callback_retry_time_invalid': '回调重试次数必须在 1-3 之间',

    # 类别相关
    'error.category.name_invalid': '类别名称不能为空且最大长度为 50 字符',
    'error.category.extract_model_invalid': 'extract_model 必须是 ExtractModel.Model_1(\'Model 1\') 或 ExtractModel.Model_2(\'Model 2\') 或 ExtractModel.Model_3(\'Model 3\')',
    'error.category.sample_files_empty': '至少需要提供一个样本文件',
    'error.category.fields_empty': '至少需要提供一个字段配置',
    'error.category.prompt_too_long': '类别提示最大长度为 150 字符',
    'error.category.enabled_invalid': 'enabled 必须是 EnabledStatus.ALL/DISABLED/ENABLED/OTHER 或对应的字符串值',
    'error.category.enabled_flag_invalid': 'enabled 只能是 EnabledFlag.DISABLED(0) 或 EnabledFlag.ENABLED(1)',
    'error.category.delete_list_empty': 'category_ids 不能为空',
    'error.category.id_empty': '类别 ID 不能为空',
    'error.category.id_invalid': '类别 ID 必须是数字字符串',
    
    # 表格相关
    'error.table.name_empty': '表格名称不能为空',
    'error.table.delete_list_empty': 'table_ids 不能为空',

    # 字段相关
    'error.field.name_empty': '字段名称不能为空',
    'error.field.delete_list_empty': 'field_ids 不能为空',

    # 样本相关
    'error.sample.delete_list_empty': 'sample_ids 不能为空',
    'error.sample.missing_content_disposition': '响应头中缺少 Content-Disposition，无法获取文件名',
    'error.sample.cannot_extract_filename': '无法从 Content-Disposition 中提取文件名',

    # 审核任务相关
    'error.review_task.name_empty': '任务名称不能为空',
    'error.review_task.name_too_long': '任务名称不能超过 {max_length} 个字符',
    'error.review_task.id_empty': '审核任务 ID 不能为空',
    'error.review_task.id_invalid': '审核任务 ID 必须是数字字符串',
    'error.review_task.delete_list_empty': 'task_ids 不能为空',
    'error.review_task.repo_id_empty': '审核规则库 ID 不能为空',
    'error.review_task.repo_id_invalid': '审核规则库 ID 必须是数字字符串',
    'error.review_task.rule_id_empty': '审核规则 ID 不能为空',
    'error.review_task.rule_id_invalid': '审核规则 ID 必须是数字字符串',

    # 文件上传相关
    'error.file.upload_source_required': 'file_path 和 file_urls 必须提供其中之一',
    'error.file.upload_source_conflict': 'file_path 和 file_urls 不能同时提供',
    'error.file.urls_empty': 'file_urls 不能为空列表',
    'error.file.urls_too_many': 'file_urls 最多支持 {max_count} 个 URL',

    # API 错误
    'error.api.request_failed': 'API 请求失败',
    'error.api.response_parse_failed': '响应解析失败',
    'error.api.invalid_response': '无效的响应格式',

    # HTTP 状态码相关
    'error.http.400': '请求参数错误',
    'error.http.401': '未授权，认证失败',
    'error.http.403': '禁止访问，权限不足',
    'error.http.404': '请求的资源不存在',
    'error.http.423': '资源被锁定',
    'error.http.429': '请求过多，请稍后再试',
    'error.http.500': '服务器内部错误',
    'error.http.502': '网关错误',
    'error.http.503': '服务暂时不可用',
    'error.http.504': '网关超时',
    'error.http.900': '业务错误',

    # 重试相关
    'retry.attempt': '正在重试... (第 {count} 次)',
    'retry.failed': '重试失败，已达到最大重试次数',
    'retry.success': '重试成功',

    # 配置相关
    'config.language_changed': '语言已切换为: {language}',
    'config.language_not_supported': '不支持的语言: {language}',

    # 客户端相关
    'client.initialized': 'SDK 客户端初始化成功',
    'client.closed': 'SDK 客户端已关闭',

    # 日志相关
    'log.request_sent': '发送请求: {method} {url}',
    'log.request_completed': '请求完成: {method} {url}, 状态码: {status_code}, 耗时: {elapsed}s',
    'log.retry_warning': '请求失败，准备重试: {method} {url}',
}
