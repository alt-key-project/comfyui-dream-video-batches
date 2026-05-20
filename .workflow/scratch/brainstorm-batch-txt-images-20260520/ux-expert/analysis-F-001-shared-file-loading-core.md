# F-001: Shared File Loading Core -- UX Impact Analysis

## Overview

共享核心 (`core/file_loader.py`) 对终端用户完全不可见——用户不会在节点列表中看到它，也不会在参数面板中操作它。但其接口设计通过参数命名、排序逻辑、错误传播路径直接影响所有基于它的用户可见节点。本分析确保共享核心的 UX 间接影响被充分考量。

## 1. Parameter Naming Convention

### 1.1 Inheritance from ForEachFilename

共享核心 MUST 继承现有 `DVB_ForEachFilename` 的参数命名风格，确保用户在 BatchLoadText 节点中看到的 `directory` 和 `pattern` 参数与 ForEachFilename 中的同名参数行为一致：

| Parameter | ForEachFilename Default | BatchLoadText Default | Consistency |
|-----------|------------------------|----------------------|-------------|
| `directory` | `comfy_paths.input_directory` | `comfy_paths.input_directory` | MUST match |
| `pattern` | `"*.jpg"` | `"*.txt"` | SHOULD follow pattern, default differs by file type |

- `directory` 参数命名 MUST 使用 "directory" 而非 "dir"、"path"、"folder"，以与 ForEachFilename 保持一致
- `directory` 参数类型 MUST 为 STRING（单行文本输入），与 ForEachFilename 一致，尽管 ComfyUI 支持 folder_paths 类型，但切换类型会破坏现有用户的路径输入习惯
- `pattern` 参数命名 MUST 使用 "pattern" 而非 "glob"、"filter"、"wildcard"，保持术语一致性

### 1.2 New Parameters Not in ForEachFilename

共享核心引入的新参数 MUST 遵循现有 DVB 参数命名风格：

- `encoding`：MUST 使用小写单一词汇，与 Python codecs 模块标准命名一致；默认值 MUST 为 `"utf-8"`；参数类型 SHOULD 为下拉列表（`["utf-8", "gbk", "latin-1", "utf-16", "ascii"]`），降低用户记忆负担。不允许使用自由文本输入——自由文本输入中一个拼写错误就会导致整个批量加载失败
- `max_files`：MUST 使用 snake_case 命名（与 ComfyUI/DVB 惯例一致），默认值 SHOULD 为 `16`（对应常见视频帧批量大小）；如果设置为 0 则 SHOULD 表示无限制

## 2. Sorting Behavior UX

共享核心对文件的排序行为 SHOULD 使用自然排序（sorted() 默认），与 ForEachFilename 的 `list_files_in_directory` 保持一致的 `alphabetic_index` 逻辑。排序策略 MUST NOT 暴露为用户的可见参数——它属于内部实现细节，用户默认期望得到的就是字典序排列。如果未来需要自定义排序，SHOULD 通过新增独立排序节点实现，而非在加载器中增加排序选项。

## 3. Error Propagation UX

共享核心的错误信息通过 `on_node_error()` 传播到用户界面。错误消息模板 MUST 遵循现有格式：`"Failure in [NodeName]: <message>"`。消息文本 SHOULD 包含：

- 出错的具体文件路径（如果适用）
- 可操作的建议（如 "检查目录是否存在" 而非仅 "目录不存在"）
- 不要暴露 Python traceback 或内部变量名

## 4. Interface Contract for Downstream Nodes

共享核心 SHALL 提供以下不暴露给用户但对下游节点关键的接口约定：

- 文件扫描结果 MUST 按文件名自然排序
- 状态追踪 MUST 复用 ForEachState，不可引入新的状态存储机制
- 编码错误处理 MUST 使用 `errors="replace"` 策略，静默替换无效字节，不中断加载流程

## 5. Constraint: User-Visible vs Internal

以下内容 MUST NOT 出现在任何用户可见节点的参数面板中：
- `statefile` 路径
- `ForEachState` 引用
- 内部排序算法名称
- 文件系统遍历实现细节

这些内容属于共享核心的实现细节，由开发者在 `core/file_loader.py` 内部管理。
