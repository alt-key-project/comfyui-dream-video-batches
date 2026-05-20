# F-001: Shared File Loading Core Design

## 1. Module Location and Rationale

`core/file_loader.py` — 位于 `core/` 包内，与 `core/utility.py`（ForEachState）、`core/batch_processing.py`（DVB_ImageBatchProcessor）同级。该位置符合项目约定：所有可复用的核心逻辑集中在 `core/` 包中，通过 `core/__init__.py` 统一导出。

该模块 MUST 保持零 ComfyUI 依赖——不导入任何 ComfyUI 特定模块（`nodes`、`folder_paths` 等），确保纯 Python 可测试性。

## 2. API Design

### 2.1 函数签名

```python
def discover_files(directory: str, pattern: str) -> list:
    """发现匹配 pattern 的文件，返回按文件名自然排序的绝对路径列表。"""

def read_text_file(filepath: str, encoding: str = "utf-8") -> str:
    """读取单个文本文件全部内容。失败时抛出异常（由调用方通过 on_node_error 处理）。"""

def load_text_files(directory: str, pattern: str, encoding: str = "utf-8") -> list:
    """组合发现与读取：发现文件 -> 排序 -> 逐个读取 -> 返回内容列表。"""
```

### 2.2 返回类型决策

`load_text_files` 返回 `List[str]`（Python 字符串列表），而非单个拼接字符串。理由：
- 保持每个文件内容的独立性和可追溯性
- 由调用方（节点层）决定是否需要拼接或保留列表结构
- 与 ComfyUI 的列表迭代语义兼容

### 2.3 排序策略

`discover_files` MUST 使用 `sorted(glob_results)` 进行自然字符串排序。这确保了：
- 与 `ForEachState.pop()` 内部 `sorted(self._data.keys())` 的行为一致
- 可预测的批处理顺序，便于调试和结果复现

## 3. 文件类型抽象

当前阶段仅实现文本文件加载，但 API 设计 SHOULD 预留扩展点：

| 扩展维度 | 当前实现 | 未来扩展 |
|---------|---------|---------|
| 文件发现 | `discover_files()` 通用，不限类型 | 同函数复用 |
| 内容读取 | `read_text_file()` | `read_image_file()` 返回 PIL.Image |
| 组合加载 | `load_text_files()` | `load_image_files()` 返回 List[DVB_Image] |
| 读取器注册 | 无（YAGNI） | `FileReaderRegistry` 按扩展名分发 |

当前阶段 MUST NOT 引入读取器注册表或抽象基类——遵循项目现有模式（DVB_Image 直接使用 PIL，无抽象层）。扩展点通过命名约定实现：`read_{type}_file()` / `load_{type}_files()`。

## 4. 与 ForEachState 的集成

### 4.1 集成层级

`core/file_loader.py` 的纯函数 MUST NOT 直接依赖 `ForEachState`。原因：
- ForEachState 是有副作用的 JSON 文件状态机——不适合作为底层 IO 函数的依赖
- 分离关注点：`file_loader` 负责 "如何发现和读取文件"，`ForEachState` 负责 "哪些文件已处理"

### 4.2 集成方式（由节点层负责）

```python
# 节点层伪代码 — 展示 ForEachState 在节点层的可选使用
state = ForEachState(statefile)
state.add_files_to_process(discover_files(directory, pattern))
# ... ForEachState.pop() 迭代 ...
content = read_text_file(filepath, encoding)
state.mark_done(os.path.basename(filepath))
```

对于 BatchLoadText（一次性加载所有文件），ForEachState 不是必需的——加载本身就是原子操作。但如果未来需要 "断点续传" 能力，MAY 在上述模式中引入 ForEachState。

## 5. 错误处理策略

分层错误处理：

| 层级 | 模块 | 策略 |
|-----|------|------|
| 文件发现 | `discover_files()` | 空结果不报错（返回 `[]`），由节点层决定行为 |
| 文件读取 | `read_text_file()` | 读取失败 MUST 抛出 `Exception`，携带 `filepath` 和原始错误信息 |
| 节点层 | `text_loaders.py` | 捕获异常，调用 `on_node_error(node_cls, message)` 格式化报告 |

### 5.1 编码错误处理

`read_text_file` SHOULD NOT 自动回退编码。如果用户指定的编码不匹配，MUST 抛出明确的 `UnicodeDecodeError` 信息，包含出错文件名和尝试的编码值，以便用户调整 `encoding` 参数。

## 6. 配置模型

该模块 MUST NOT 引入独立的配置参数。所有可配置参数（`encoding`）通过节点 INPUT_TYPES 暴露给用户，不通过 `DVB_Config` 或 `config.json` 管理。

## 7. 边界场景

| 场景 | 行为 |
|------|------|
| 空目录 / 无匹配文件 | `discover_files()` 返回 `[]`，节点层报告 "No files found matching pattern" |
| 二进制文件被匹配 | `read_text_file()` 在 UTF-8 解码时抛出 `UnicodeDecodeError` |
| 大文件（>100MB） | `read_text_file()` 全量读入内存；MUST 在节点层文档中标注内存风险 |
| 并发目录访问 | 无特殊处理——Python `open()` 的文件系统级锁足够 |
| 符号链接 / 递归 glob | `pattern` 参数支持 `**/*.txt` 格式，`glob(recursive=True)` 自动处理 |

## 8. 导出注册

`core/__init__.py` MUST 新增一行导入：

```python
from .file_loader import discover_files, read_text_file, load_text_files
```

新增行位置：在现有 `from .err import on_node_error, raise_error` 之后，遵循字母序排列。
