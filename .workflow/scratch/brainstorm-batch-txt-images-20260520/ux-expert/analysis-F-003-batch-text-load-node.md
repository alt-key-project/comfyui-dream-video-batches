# F-003: Batch Text Load Node -- UX Design Analysis

## Overview

DVB_BatchLoadText 是用户直接交互的批量文本加载节点。本分析覆盖节点元数据、参数面板、输出端口、错误消息和边界行为，每个决策均以现有 DVB 节点 UX 模式为参照基准。

## 1. Node Identity

### 1.1 Node Name

**Recommendation**: `"Batch Load Text"`

Rationale: 延续 DVB 节点 3-4 词动词短语模式（"Load Image From Path"、"For Each Filename"、"String Builder"），`_SIGNATURE_SUFFIX = " [DVB]"` 自动追加后节点显示名为 "Batch Load Text [DVB]"。

备选方案（已否决）：
- "Load Text Files" -- 未体现"批量"语义，与 "Load Image From Path"（单文件）可能造成混淆
- "Batch Text Loader" -- "Loader" 后缀与现有节点风格不一致（现有节点使用祈使动词而非名词形式）

### 1.2 Icon

**Recommendation**: `📄` (document/page)

Rationale: 现有 `DVB_LoadImageFromPath` 使用 🖼 (frame with picture) 代表图像，📄 (document) 代表文本形成语义对称。两者均为静态文档图标，用户可直观区分"加载图像"与"加载文本"。

备选方案（已否决）：
- 📝 (memo) -- 暗示编辑/写入操作，与只读加载语义冲突
- 📥 (inbox tray) -- 未在现有节点中出现，引入新图标语义增加认知负荷
- 📃 (page with curl) -- 与 📄 语义相近但视觉噪声更大

### 1.3 Category

**Recommendation**: `NodeCategories.IO`

Rationale: `DVB_LoadImageFromPath` 已经归类于 `NodeCategories.IO`，文本加载同样是 I/O 操作。归类于 IO 而非 UTILS 能帮助用户在节点菜单中快速定位所有文件加载节点。在 DVB 顶层类别下，显示为 "DVB/io"。

备选方案（已否决）：
- `NodeCategories.UTILS` -- 文本加载是核心功能而非辅助工具，分类于 UTILS 会降低可发现性

## 2. Parameter Panel Design

### 2.1 Parameter Layout

参数 MUST 按使用频率降序排列：

| # | Parameter | Type | Default | Description |
|---|-----------|------|---------|-------------|
| 1 | `directory` | STRING (multiline: False) | `comfy_paths.input_directory` | 文本文件所在目录路径 |
| 2 | `pattern` | STRING (multiline: False) | `"*.txt"` | 文件名 glob 匹配模式 |
| 3 | `encoding` | dropdown | `"utf-8"` | 文本文件编码 |
| 4 | `max_files` | INT | `16` | 最大加载文件数量（0 = 无限制） |

### 2.2 Parameter Details

**`directory` (STRING, 位置 1)**：
- MUST 使用 `multiline: False`（单行输入），与 ForEachFilename 的 directory 参数保持一致
- SHOULD 默认值为 `comfy_paths.input_directory`（ComfyUI 标准输入目录），降低首次使用者的配置门槛
- 如果未来 ComfyUI 版本提供 folder_paths widget 且 DVB 项目整体迁移，SHOULD 跟随迁移，但不提前单独切换

**`pattern` (STRING, 位置 2)**：
- 默认值 MUST 为 `"*.txt"`，与 ForEachFilename 的 `"*.jpg"` 形成文件类型对称
- 通配符语法 MUST 遵循 Python glob 标准（`*`, `?`, `[]`），与 ForEachFilename 行为一致
- pattern 参数 MUST NOT 接受正则表达式——glob 语法足够覆盖用户场景，正则表达式增加学习成本且可能导致意外行为

**`encoding` (dropdown, 位置 3)**：
- MUST 使用下拉选择而非自由文本输入——一个拼写错误即可导致整个批量加载失败
- 下拉选项 SHOULD 包含：`utf-8`, `gbk`, `latin-1`, `utf-16`, `ascii`, `shift_jis`, `euc-kr`
- `utf-8` MUST 为默认值——这是现代文本文件的事实标准
- `gbk` SHOULD 出现在列表前 3 位——ComfyUI 中文用户群体大，GBK 编码的遗留文本文件较为常见

**`max_files` (INT, 位置 4)**：
- 默认值 SHOULD 为 `16`——常见视频批处理帧数（16/24/30 帧），16 是批处理中最常见的帧数下限，能在安全性与实用性间取得平衡
- 范围 MUST 为 `min: 1, max: 500`——500 上限防止用户误操作大规模加载
- 值为 `0` SHOULD 表示不限制——高级用户明确需要的无限制模式
- `max_files` 同时控制输出端口数量——例如 max_files=4 时，节点输出 4 个 STRING 端口

## 3. Output Port Design

### 3.1 Port Naming

输出端口命名 MUST 使用 `text_1`, `text_2`, ..., `text_N` 模式。N 由 `max_files` 参数决定。

Rationale:
- `text_` 前缀与现有 DVB `RETURN_NAMES` 风格一致（小写、描述性、短名称）
- 数字索引从 1 开始（而非 0），符合非程序员用户的直觉计数习惯
- 端口数量由 max_files 参数决定，用户在参数面板调整最大文件数时同时影响输出端口数，行为可预测

### 3.2 Dynamic Output Resolution

由于 RETURN_TYPES 是类级别定义，动态端口需要实现策略。在 ComfyUI 的固定端口限制下，有以下方案：

**Recommended**: 编译时固定最大端口数（如 500 个 "STRING"），运行时仅前 N 个端口有实际数据（N = min(max_files, 实际匹配文件数)），其余端口输出空字符串 `""`。这是 ComfyUI 社区中处理动态输出最常用的模式，不需要魔改框架。

备选方案（已否决）：
- 聚合为单个 STRING 输出（如换行符连接）——用户需要用 StringTokenizer 二次拆分，违背"一键式"设计目标
- 每次执行只读一个文件（类似 ForEachFilename 的迭代模式）——需要用户手动连接回环，增加工作流复杂度

### 3.3 Underflow Handling

当实际匹配文件数 < max_files 时（例如 max_files=16 但目录中只有 3 个 .txt 文件）：
- `text_1` 至 `text_3` MUST 包含实际文件内容
- `text_4` 至 `text_16` MUST 输出空字符串 `""`
- 空端口 MAY 导致下游节点静默失败（如 prompt 节点收到空文本生成空白帧），这是 ComfyUI 生态的通病

## 4. Error Message Usability

所有错误 MUST 通过 `on_node_error()` 抛出，消息格式为 `"Failure in [Batch Load Text]: <具体消息>"`。

| Scenario | Error Message Template | Rationale |
|----------|----------------------|-----------|
| 目录不存在 | `"目录不存在: {path}。请检查路径拼写，或使用 ForEachFilename 节点先浏览目录结构。"` | 给出原因 + 操作建议 + 替代方案 |
| 目录存在但无匹配文件 | `"在 {dir} 中未找到匹配 '{pattern}' 的文件。当前目录包含 {file_count} 个文件，其中 {txt_count} 个 .txt 文件。请调整 pattern 参数。"` | 提供环境上下文，帮助用户定位问题 |
| 单个文件读取权限不足 | `"无法读取文件: {filepath}。请检查文件权限。"` | 定位具体文件，给出明确原因 |
| 编码错误（已由 errors="replace" 静默处理） | 不报错，但 SHOULD 在 ComfyUI 控制台输出形如 `[DVB] Warning: encoding replacement in {filepath} at byte offset {n}` 的警告 | 静默替换同时提供可追踪的调试信息 |
| 文件数超过 max_files | 不报错，加载前 max_files 个文件，其余静默跳过。控制台 SHOULD 输出 `[DVB] Info: {total} files found, loading first {max_files}` | 非错误行为，但给用户透明信息 |

## 5. IS_CHANGED Behavior

本节点 MUST NOT 实现 `IS_CHANGED` 返回 `float("NaN")`（强制每次重新执行）。对于批量加载节点，IS_CHANGED SHOULD 基于文件系统状态（如目录的修改时间或文件列表哈希）来判断是否需要重新加载——这能防止 ComfyUI 不必要的批量重新执行但又能保证文件变更后自动刷新。

如果实现复杂度允许，SHOULD 实现类似 `DVB_LoadImageFromPath` 的基于文件内容的哈希检测机制——当文件列表或任一文件内容变更时自动触发重新加载。
