# Cross-Cutting Concerns: Batch Text File Loader

## 1. Data Flow

### 1.1 完整数据流图

```
User Parameters (directory, pattern, encoding)
        │
        ▼
┌─────────────────────────────────┐
│  DVB_BatchLoadText.load()       │  ◄── text_loaders.py
│  - 参数验证                      │
│  - 调用共享核心                   │
│  - 错误报告 (on_node_error)       │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  core/file_loader.py             │
│                                  │
│  discover_files(dir, pattern)    │  ◄── glob.glob() + sorted()
│         │                        │
│         ▼                        │
│  read_text_file(fp, encoding)    │  ◄── open(fp, encoding=enc)
│         │                        │
│         ▼                        │
│  load_text_files(dir, pat, enc)  │  ◄── 组合上述两步
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Return: List[str]               │
│  ["content1", "content2", ...]   │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  ComfyUI Execution Engine        │
│  - 检测到 list 输出               │
│  - 对下游节点执行 N 次迭代调用     │
│  - 每次传递一个字符串元素          │
└─────────────────────────────────┘
```

### 1.2 数据不流经 ForEachState

与 `DVB_ForEachFilename` 的关键区别：BatchLoadText 的数据流不经过 ForEachState。ForEachFilename 的数据流是 `ForEachState.pop() → 单个 filepath → STRING 输出`，而 BatchLoadText 的数据流是 `glob → 全部文件 → 批量读取 → List[STRING] 输出`。两者使用相同的底层原语（ForEachState vs discover_files），但在工作流模式上互斥：一个是迭代模式，一个是批量模式。

## 2. Isolation from Existing Nodes

### 2.1 隔离矩阵

| 现有模块 | 影响评估 | 隔离策略 |
|---------|---------|---------|
| `DVB_ForEachFilename` | 零影响——不共享状态、不修改代码 | 新建 text_loaders.py，独立文件 |
| `DVB_ForEachCheckpoint` | 零影响 | DVB_BatchLoadText 不输出 FOREACH 类型 |
| `DVB_LoadImageFromPath` | 零影响 | 不同文件、不同 CATEGORY（同为 IO 但不冲突） |
| `ForEachState` (core/utility.py) | 零修改 | 不在 file_loader 中使用，仅在节点层可选使用 |
| `__init__.py` `_NODE_CLASSES` | 追加一行 | 列表末尾追加，不修改现有条目 |
| `core/__init__.py` | 追加一行导入 | 不影响现有导入链 |

### 2.2 命名空间隔离

- 新节点类名 `DVB_BatchLoadText` MUST 不与任何现有类名冲突
- 新模块名 `text_loaders.py` MUST 不与现有模块名冲突（现有：`loaders.py`）
- `core/file_loader.py` 的函数名 `discover_files`、`read_text_file`、`load_text_files` MUST 不与 `core/` 现有导出冲突

### 2.3 共享核心的导入不会产生循环依赖

```
core/__init__.py  →  core/file_loader.py    (单向)
core/__init__.py  →  core/utility.py          (单向，现有)
text_loaders.py   →  core (通过 __init__.py)   (单向，遵循现有模式)
__init__.py       →  text_loaders.py           (单向，遵循现有模式)
```

箭头方向均为单向，无循环依赖风险。

## 3. Memory Considerations

### 3.1 风险评估

| 场景 | 文件数 | 单文件大小 | 总内存占用 | 风险等级 |
|------|-------|-----------|-----------|---------|
| 典型 | 10 | 1KB | ~10KB | 安全 |
| 大批量 | 1000 | 10KB | ~10MB | 安全 |
| 大文件 | 10 | 10MB | ~100MB | 注意 |
| 极端 | 100 | 100MB | ~10GB | 危险 |

### 3.2 缓解措施

`load_text_files()` 当前实现 MUST 全量加载所有文件到内存（`[read_text_file(f) for f in files]`）。针对高风险场景，SHOULD 在文档化时标注以下建议：

- **模式选择**：大批量文件场景 SHOULD 优先使用 `DVB_ForEachFilename`（逐文件迭代，内存占用仅为单文件大小）
- **大文件处理**：超大文本文件 SHOULD 考虑预处理（拆分、流式生成摘要）
- **模式限制**：如果单文件 > 1GB，MUST NOT 使用 BatchLoadText；应使用外部预处理

### 3.3 未来优化路径（当前不实现）

`load_text_files` MAY 在未来版本添加 `max_total_size_mb` 参数，在总大小超限时提前报错而非 OOM：
```python
def load_text_files(directory, pattern, encoding="utf-8", max_size_mb=None):
    total = 0
    for f in files:
        total += os.path.getsize(f)
    if max_size_mb and total > max_size_mb * 1024 * 1024:
        raise Exception(f"Total file size {total} exceeds limit {max_size_mb}MB")
```

## 4. Consistency with Existing Patterns

### 4.1 遵循的模式

| 模式 | 来源 | 应用 |
|------|------|------|
| `NODE_NAME` + `CATEGORY` + `RETURN_TYPES` + `FUNCTION` | DVB_LoadImageFromPath | DVB_BatchLoadText 类结构 |
| `required` + `optional` INPUT_TYPES | DVB_StringBuilder | encoding 作为 optional |
| `on_node_error(cls, msg)` | DVB_ForEachFilename | 所有错误报告 |
| `folder_paths.input_directory` 默认值 | DVB_ForEachFilename | directory 默认值 |
| `_NODE_CLASSES` 列表注册 | __init__.py | 节点注册 |
| `from .core import *` 导入模式 | 所有现有节点模块 | text_loaders.py 导入 |

### 4.2 故意偏离的模式

| 现有模式 | 偏离方式 | 理由 |
|---------|---------|------|
| DVB_ForEachFilename 的 `id` (COMBO) 参数 | 不包含 | Batch 模式不需要迭代状态标识 |
| DVB_LoadImageFromPath 的 `IS_CHANGED` | 不实现 | 文本文件适合每次重读（见 F-003 分析） |
| DVB_ForEachFilename 的 FOREACH 输出 | 不输出 FOREACH | Batch 是一次性操作，不需要 Checkpoint |

## 5. Testing Implications

### 5.1 可测试性

`core/file_loader.py` 的纯函数设计使其可以在不启动 ComfyUI 的情况下进行单元测试：

```python
# 测试 discover_files
files = discover_files("/tmp/test_data", "*.txt")
assert all(f.endswith(".txt") for f in files)
assert files == sorted(files)

# 测试 read_text_file
content = read_text_file("/tmp/test_data/a.txt", "utf-8")
assert isinstance(content, str)
```

### 5.2 集成测试入口

节点层（`DVB_BatchLoadText.load()`）需要在 ComfyUI 环境中进行集成测试，因为依赖 `comfy_paths.input_directory` 和 ComfyUI 的执行上下文。

## 6. Backward Compatibility

| 检查项 | 状态 |
|--------|------|
| 现有节点注册不受影响 | 通过——仅在 `_NODE_CLASSES` 末尾追加 |
| 现有 workflow JSON 不受影响 | 通过——新节点不会出现在旧工作流中 |
| config.json 不新增字段 | 通过——encoding 通过 INPUT_TYPES 暴露 |
| node_list.json 自动更新 | 通过——`update_node_index()` 自动处理 |
