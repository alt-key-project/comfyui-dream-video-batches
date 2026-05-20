# Context: Phase 1 — Load Text From Path

**Date**: 2026-05-21
**Areas discussed**: 模块位置、编码选项、输出格式、错误处理、变化检测

## Decisions

### Decision 1: Module Location
- **Context**: DVB_LoadTextFromPath 类放在哪个文件
- **Options**:
  1. 新建 `text_loaders.py`
  2. 追加到现有 `loaders.py`
- **Chosen**: Option 1 — 新建 `text_loaders.py`
- **Reason**: 关注点分离。loaders.py 专注图像，text_loaders.py 专注文本。未来文本加载变体自然归入此文件。

### Decision 2: Encoding Options
- **Context**: encoding 下拉列表的选项范围
- **Options**:
  1. 基础编码集: ASCII, UTF-8, UTF-16, UTF-8-SIG
  2. 基础 + 中文编码: GBK, GB2312, GB18030
  3. 基础 + CJK 全量
  4. 自由输入
- **Chosen**: Option 1 — 基础编码集 + Latin-1
- **Reason**: 保持简洁。UTF-8 覆盖绝大多数场景，UTF-8-SIG 处理 BOM 文件，Latin-1 作为"永不失败"的降级选项。中文编码需求可通过后续版本追加。

### Decision 3: Output Format (from brainstorm)
- **Context**: 单文件加载的输出端口
- **Chosen**: 单一 STRING 输出 `("STRING",)` 命名为 `("text",)`
- **Reason**: 镜​像 DVB_LoadImageFromPath 的单一输出模式

### Decision 4: Change Detection (from brainstorm)
- **Context**: IS_CHANGED 实现方式
- **Chosen**: SHA256 文件哈希（镜像 DVB_LoadImageFromPath）
- **Reason**: 一致性。文件内容变化时重新执行，空路径返回空字符串

### Decision 5: Error Handling (from brainstorm)
- **Context**: 文件不存在或不可读
- **Chosen**: `on_node_error()` 抛出异常（镜像现有模式）
- **Reason**: 项目一致性。空路径则返回空字符串（优雅降级）

### Decision 6: Node Metadata (from brainstorm)
- **Context**: 节点名称、图标、分类
- **Chosen**: 
  - NODE_NAME: "Load Text From Path"
  - ICON: "📄"
  - CATEGORY: NodeCategories.IO
  - DISPLAY_NAME: "Load Text From Path [DVB]"

## Constraints

### Locked
- MUST 新建 `text_loaders.py` 模块
- MUST 使用 `NodeCategories.IO` 分类
- MUST 镜像 `DVB_LoadImageFromPath` 的结构（INPUT_TYPES, IS_CHANGED, FUNCTION）
- MUST 在 `__init__.py` 的 `_NODE_CLASSES` 末尾追加（不修改现有条目）
- MUST 不引入新依赖
- encoding 参数 MUST 为下拉列表，默认值 `"utf-8"`
- encoding 选项 MUST 包含: `["utf-8", "utf-16", "ascii", "utf-8-sig", "latin-1"]`
- RETURN_TYPES MUST 为 `("STRING",)`，RETURN_NAMES MUST 为 `("text",)`

### Free
- encoding 下拉列表的具体排序
- `ICON` 的 emoji 选择已定（📄），但可后续调整
- 是否添加 `max_file_size` 参数（建议不添加，保持简洁）

### Deferred
- 中文编码支持（GBK/GB2312） — 用户反馈后再加
- 批量文本加载变体 — ForEachFilename 已满足需求
- 文本内容预处理（trim、normalize） — 属于下游节点职责

## Code Context

**参考文件** (镜像模式):
- `loaders.py:9-38` — DVB_LoadImageFromPath（结构模板）
- `__init__.py:15-49` — _NODE_CLASSES 列表（注册点）
- `core/err.py:5-13` — on_node_error()（错误处理）

**目标新文件**:
- `text_loaders.py` — DVB_LoadTextFromPath 节点类

**关键接口**:
```python
class DVB_LoadTextFromPath:
    NODE_NAME = "Load Text From Path"
    ICON = "📄"
    CATEGORY = NodeCategories.IO
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "result"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_path": ("STRING", {"default": '', "multiline": False}),
                "encoding": (["utf-8", "utf-16", "ascii", "utf-8-sig", "latin-1"],)
            }
        }

    @classmethod
    def IS_CHANGED(cls, text_path, encoding, **kwargs):
        # SHA256 hash like DVB_LoadImageFromPath
        ...

    def result(self, text_path, encoding, **other):
        ...
```
