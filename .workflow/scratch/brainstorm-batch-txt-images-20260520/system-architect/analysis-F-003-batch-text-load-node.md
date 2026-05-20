# F-003: Batch Text Load Node Design

## 1. Node Class Structure

### 1.1 Complete Class Skeleton

```python
# text_loaders.py
import os
import folder_paths as comfy_paths
from .categories import NodeCategories
from .core import discover_files, read_text_file, load_text_files, on_node_error

class DVB_BatchLoadText:
    NODE_NAME = "Batch Load Text"
    CATEGORY = NodeCategories.IO
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("texts",)
    FUNCTION = "load"
    ICON = "\U0001F4C4"  # 📄

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": comfy_paths.input_directory}),
                "pattern": ("STRING", {"default": "*.txt"}),
            },
            "optional": {
                "encoding": ("STRING", {"default": "utf-8"}),
            }
        }

    def load(self, directory: str, pattern: str, encoding: str = "utf-8"):
        ...
```

### 1.2 字段设计决策

| 字段 | 值 | 设计理由 |
|------|---|---------|
| `NODE_NAME` | `"Batch Load Text"` | 描述性名称，遵循现有 PascalCase 风格 |
| `CATEGORY` | `NodeCategories.IO` | 与 `DVB_LoadImageFromPath` 同为 IO 类别 |
| `RETURN_TYPES` | `("STRING",)` | STRING 类型；实际返回 Python list |
| `RETURN_NAMES` | `("texts",)` | 复数形式暗示列表语义 |
| `FUNCTION` | `"load"` | 动词，语义清晰 |
| `ICON` | `"\U0001F4C4"` | 文档图标，区别于图像的 🖼 |

## 2. INPUT_TYPES 参数设计

### 2.1 required 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `directory` | STRING | `comfy_paths.input_directory` | 遵循 ForEachFilename 的默认目录约定 |
| `pattern` | STRING | `"*.txt"` | 默认识别 `.txt` 文件；支持 `**/*.txt` 递归 |

### 2.2 optional 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `encoding` | STRING | `"utf-8"` | 用户可指定任意 Python 支持的编码 |

### 2.3 为何不包含 `id` 参数

`DVB_ForEachFilename` 的 `id` 参数用于生成唯一的 ForeachState JSON 文件名（`foreach_{id}.json`），以支持并行迭代循环。`DVB_BatchLoadText` 是一次性操作（读取所有匹配文件），不存在迭代状态复用需求，因此 MUST NOT 包含 `id` 参数。

## 3. Output Port Design — ComfyUI Fixed Port Constraint

### 3.1 问题陈述

ComfyUI 要求 `RETURN_TYPES` 在类注册时静态声明。但批量加载的文件数量是运行时动态决定的（可能 0、3、50 个文件）。无法为每个文件创建独立的输出端口。

### 3.2 解决方案：STRING 列表输出

`load()` 方法返回 `(texts_list,)`，其中 `texts_list` 是一个 Python `list` of `str`：

```python
def load(self, directory: str, pattern: str, encoding: str = "utf-8"):
    files = discover_files(directory, pattern)
    if not files:
        on_node_error(DVB_BatchLoadText,
            f"No files found matching '{pattern}' in {directory}")
    texts = [read_text_file(f, encoding) for f in files]
    return (texts,)
```

### 3.3 ComfyUI 列表迭代行为

当节点输出为 `list` 类型时，ComfyUI 的执行引擎会自动对下游节点执行列表迭代——下游节点会被调用 N 次（N = 列表长度），每次接收一个元素。这是 ComfyUI 内置的隐式批次处理机制。

| 场景 | ComfyUI 行为 |
|------|-------------|
| `["hello", "world"]` | 下游节点执行 2 次，分别接收 `"hello"` 和 `"world"` |
| `["single"]` | 下游节点执行 1 次 |
| `[]` (空列表) | 当前实现通过 `on_node_error` 提前终止；若改为返回空列表，下游节点执行 0 次 |

### 3.4 替代方案分析（已排除）

| 方案 | 排除原因 |
|------|---------|
| 拼接为单个字符串 | 丢失文件边界，下游无法区分文件内容来源 |
| N 个固定输出端口 | ComfyUI 不支持动态端口数 |
| FOREACH 迭代节点 | 与 `DVB_ForEachFilename` 功能重叠，不属于 Batch 语义 |

## 4. Node Registration in __init__.py

### 4.1 导入

```python
# __init__.py 文件顶部，在现有 from .loaders import * 之后追加
from .text_loaders import *
```

### 4.2 类注册

在 `_NODE_CLASSES` 列表末尾追加 `DVB_BatchLoadText`：

```python
_NODE_CLASSES = [
    # ... 现有条目保持不变 ...
    DVB_FrameSetSplitEnd,
    DVB_BatchLoadText,        # <--- 新增，位于列表末尾
]
```

### 4.3 注册保证

`__init__.py` 的 for 循环自动处理：
- `NODE_CLASS_MAPPINGS["Batch Load Text [DVB]"] = DVB_BatchLoadText`
- `NODE_DISPLAY_NAME_MAPPINGS` 同理
- `update_node_index()` 自动更新 `node_list.json`

MUST NOT 修改循环逻辑或任何现有注册代码。

## 5. Error Handling

### 5.1 空文件列表

```python
if not files:
    on_node_error(DVB_BatchLoadText,
        f"No files found matching '{pattern}' in {directory}")
```

遵循 `DVB_ForEachFilename` 的 "No more files to process" 错误模式，但更明确地告知用户未匹配到文件。

### 5.2 读取错误

`read_text_file()` 内部的 `open()` 失败（文件不存在、权限不足、编码错误）MUST 让异常向上传播至节点层，由节点层捕获并调用 `on_node_error()`：

```python
try:
    texts = [read_text_file(f, encoding) for f in files]
except Exception as e:
    on_node_error(DVB_BatchLoadText, f"Failed to read file: {e}")
```

### 5.3 为什么不是逐文件容错

逐文件容错（跳过失败文件，继续读取其余）SHOULD NOT 在初始实现中引入。理由：
- 保持与代码库现有错误处理模式一致（fail-fast）
- 用户不会在无意中错过部分数据
- 未来可基于用户反馈添加 `skip_on_error` 可选参数

## 6. IS_CHANGED 语义

`DVB_BatchLoadText` SHOULD NOT 实现 `IS_CHANGED` 类方法。理由：文本文件内容频繁变化（编辑、生成），不适合做哈希缓存。每次工作流执行都重新读取，保证数据新鲜度。对比 `DVB_LoadImageFromPath` 实现了 `IS_CHANGED`（基于文件哈希），但图像文件通常是静态资源，而文本文件可能是动态生成的中间产物。

## 7. File Structure

```
text_loaders.py          # 新建文件，位于包根目录
├── imports              # folder_paths, NodeCategories, core 函数
└── class DVB_BatchLoadText
    ├── NODE_NAME, CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION, ICON
    ├── INPUT_TYPES (classmethod)
    └── load (instance method)
```
