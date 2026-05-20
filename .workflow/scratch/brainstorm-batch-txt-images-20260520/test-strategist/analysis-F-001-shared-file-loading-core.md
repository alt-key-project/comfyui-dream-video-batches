# F-001: Shared File Loading Core Test Strategy

## 1. 可测试性设计建议

### 1.1 核心函数纯度要求

`core/file_loader.py` 中的公开函数 SHOULD 设计为纯函数或近纯函数——接受输入参数、返回输出值、副作用仅限文件系统读写。以下是推荐函数签名和可测试性分析：

| 函数 | 签名建议 | 可脱离 ComfyUI 测试 | 副作用 |
|------|---------|---------------------|--------|
| `scan_files(directory, pattern, recursive=False)` | 返回 `List[str]` | 是 | 无 |
| `sort_files(file_list, sort_mode="natural")` | 返回 `List[str]` | 是 | 无 |
| `filter_by_extension(file_list, extensions)` | 返回 `List[str]` | 是 | 无 |
| `read_text_file(filepath, encoding="utf-8", errors="replace")` | 返回 `str` | 是 | 无 |
| `create_state(directory, state_id)` | 返回 `ForEachState` | 是 | 创建文件 |

关键原则：**MUST NOT** 在核心函数中直接引用 `comfy_paths` 或 ComfyUI 内部模块。所有 ComfyUI 上下文依赖 MUST 封装在节点类层面（`text_loaders.py`），而非 `file_loader.py`。

### 1.2 无 ComfyUI 验证路径

以下核心逻辑可直接在标准 Python 脚本中验证，无需启动 ComfyUI：

```python
# 验证 scan_files - 无需 ComfyUI
from core.file_loader import scan_files, sort_files
files = scan_files("/tmp/test-dir", "*.txt")
assert len(files) == expected_count
sorted_files = sort_files(files, sort_mode="natural")
assert sorted_files == expected_order
```

ForEachState 同样可独立测试，因为其仅依赖 JSON 文件读写：

```python
from core.utility import ForEachState
state = ForEachState("/tmp/test-state.json")
state.add_files_to_process(["a.txt", "b.txt"])
assert state.pop() is not None
state.mark_done("a.txt")
assert state.pop() is not None  # 返回 b.txt
assert state.pop() is None      # 全部完成
```

**建议**: 在 `file_loader.py` 同目录下放置一个 `file_loader_test.py`，以 `if __name__ == "__main__"` 块提供自验证脚本。这不是 pytest，而是开发阶段的快速冒烟测试。符合项目「不引入外部测试框架」的约束。

## 2. ForEachState 复用正确性验证

### 2.1 状态隔离测试矩阵

ForEachState 通过 JSON 文件路径区分不同状态实例。隔离风险点：两个不同节点使用相同 `id` + 相同 `directory` 时会产生状态冲突。

| 测试场景 | 节点 A (id) | 节点 B (id) | directory | 预期行为 |
|---------|------------|------------|-----------|---------|
| 不同 ID 不同目录 | "apple" | "banana" | /dir-a, /dir-b | 完全隔离，各自 statefile 独立 |
| 不同 ID 相同目录 | "apple" | "banana" | /same-dir | 隔离：statefile = foreach_apple.json vs foreach_banana.json |
| 相同 ID 相同目录 | "apple" | "apple" | /same-dir | SHOULD 共享状态（这是 ForEachFilename 的预期行为——同一循环多次迭代） |
| 空目录 | "apple" | N/A | /empty-dir | `pop()` MUST 返回 None；`add_files_to_process` 无文件时无操作 |

### 2.2 ForEachState 边界行为

以下行为 MUST 被验证：

- **并发写入**: 两个 ForEachState 实例指向同一 filepath 时，后写入者覆盖前者。这不是 bug，而是 ForEachState 的设计约束。测试 MUST 确认此行为文档化。
- **损坏 JSON 文件**: `__init__` 中的 `except` 块将 `self._data` 初始化为空 dict。测试 MUST 验证：当 statefile 存在但非合法 JSON 时，ForEachState 能正常初始化且不抛出异常。
- **相对路径处理**: `__init__` 使用 `os.path.abspath(filepath)` 存储绝对路径，但 `self._dir` 从 filepath 的 dirname 计算。测试 MUST 验证相对路径输入时的 `pop()` 返回值路径正确性。
- **文件名含特殊字符**: statefile 名来自 `id` 参数 (`_ID_SELETIONS` 列表中的值)，当前不包含特殊字符。但若未来扩展 `id` 来源，MUST 验证特殊字符不导致文件系统错误。

### 2.3 与现有 ForEachFilename 的隔离验证

新增 `DVB_BatchLoadText` 使用 ForEachState 时，其 `id` 参数 MUST 与 DVB_ForEachFilename 使用相同的 `_ID_SELETIONS` 列表（或独立列表）。测试 MUST 验证：

- 同时运行 ForEachFilename(id="apple") 和 BatchLoadText(id="apple") 不互相干扰，当且仅当两者的 directory 参数不同。
- 若两者 directory 相同且 id 相同，statefile 共享是设计行为而非 bug，但 MUST 被明确文档化。

## 3. 可测试性设计清单

以下设计特征 MUST 在 `file_loader.py` 实现时具备：

1. **依赖注入**: 文件系统访问通过参数传入，MUST NOT 硬编码路径。
2. **单一职责**: 扫描、排序、过滤、读取各自独立函数，MUST NOT 合并为一个巨型函数。
3. **无隐式状态**: 除 ForEachState 外，MUST NOT 引入全局/模块级可变状态。
4. **类型提示**: 函数签名 SHOULD 包含 Python type hints，降低测试维护成本。
5. **错误传播**: 所有文件操作异常 MUST 通过 `on_node_error()` 或标准异常机制向上传播，MUST NOT 静默吞没。
