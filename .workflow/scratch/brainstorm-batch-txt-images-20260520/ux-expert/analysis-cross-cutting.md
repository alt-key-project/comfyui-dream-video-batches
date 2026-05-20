# UX Expert: Cross-Cutting Concerns Analysis

## Overview

本分析覆盖批量文本加载功能与现有 DVB 工作流的 UX 交互面，包括与 ForEachFilename 生态的差异对比、新旧用户的使用路径设计、以及跨节点一致性约束。

## 1. ForEachFilename vs BatchLoadText -- UX Paradigm Comparison

两个节点都解决"批量文件处理"问题，但工作流模型完全不同。

### 1.1 ForEachFilename: 迭代式 (Iterator Pattern)

- 用户连接 ForEachFilename -> 处理节点 -> ForEachCheckpoint 形成回环
- 每次执行只加载一个文件，通过 ForEachState JSON 文件追踪进度
- 适合：每帧需要独立处理、处理节点有状态依赖、内存敏感的场景
- UX 成本：3 个节点 + 2 条连线 + 理解回环概念

### 1.2 BatchLoadText: 一次性 (Eager Pattern)

- 用户连接 BatchLoadText -> N 个处理节点（每个 STRING 端口接一个下游节点）
- 一次执行加载所有文件内容到内存
- 适合：需要同时看到所有文本内容、下游处理无状态、文件数量可控的场景（16-100 个）
- UX 成本：1 个节点 + N 条连线

### 1.3 When to Use Which

| 场景 | 推荐节点 | 判断依据 |
|------|---------|---------|
| 逐帧 prompt 动画（16 帧） | BatchLoadText | 文件数少，需要同时访问所有 prompt |
| 大量视频帧处理（200+ 帧） | ForEachFilename | 迭代模式内存友好，避免一次性占用 |
| 需要按文件名序号与图像帧配对 | BatchLoadText | 自然排序 + 固定端口索引与帧号天然对齐 |
| 需要动态跳过某些文件 | ForEachFilename | 回环中可插入条件分支节点 |

SHOULD 在节点注释/文档中提供 "When to use BatchLoadText vs ForEachFilename" 的对比说明。MAY 在节点 DESCRIPTION 字段中给出简短提示。

## 2. New User Onboarding Path

### 2.1 Discovery

新用户最可能的发现路径：
1. 在节点菜单 DVB/io 下看到 "Batch Load Text [DVB]"
2. 与已有的 "Load Image From Path [DVB]" 并列，用户自然推测这是文本版本

SHOULD 确保两个加载节点在分类菜单中相邻排列，形成"文件加载"的心智分组。

### 2.2 First Use

新用户的首次使用路径：
1. 拖入 BatchLoadText 节点
2. 看到 directory 默认值已指向 ComfyUI input 目录
3. 将 pattern 从 "*.txt" 调整为具体模式（如 "prompts/*.txt"）
4. 选择 encoding（默认 utf-8 已满足多数场景）
5. 如需更多端口，调整 max_files
6. 连接输出端口到下游 prompt 节点

首次使用的"时间到价值" (Time-to-Value) 应该在 30 秒以内——默认参数足够覆盖最常见场景（input 目录下的所有 .txt 文件）。

### 2.3 Error Recovery Path

最可能的首次错误场景：目录中无 .txt 文件。

错误恢复路径：
1. 看到错误 "未找到匹配 '*.txt' 的文件"
2. 错误消息提示当前目录的文件概况
3. 用户调整 pattern 或将 .txt 文件放入目录
4. 重新执行

这条路径 SHOULD 能让用户在 1-2 次尝试内解决问题。

## 3. Existing User Transition Path

### 3.1 ForEachFilename 用户迁移

当前使用 ForEachFilename 处理文本文件的用户面临两种选择：

**Option A: 继续使用 ForEachFilename** -- 已有的工作流无需修改，向后兼容 100% 保证。

**Option B: 迁移到 BatchLoadText** -- 如果满足以下条件：
- 文件数 <= 50
- 需要固定索引访问（如 text_3 对应 frame_3）
- 不需要逐帧条件判断

迁移成本：替换 1 个节点（ForEachFilename）+ 断开回环（移除 ForEachCheckpoint），用 BatchLoadText 和固定端口连接替代。预估迁移时间 < 2 分钟。

### 3.2 与 String Tokenizer 协同

已有 `DVB_StringTokenizer` 的用户可用以下模式处理聚合文本场景：
1. 如果文本文件以特定分隔符组织内容，可将多个文本文件内容输出后，使用 StringTokenizer 按帧拆分
2. 这种组合不是主要使用场景，但 SHOULD 在示例工作流中展示

## 4. Cross-Node Consistency Constraints

### 4.1 Naming Consistency Matrix

| UX Element | LoadImageFromPath | ForEachFilename | BatchLoadText (proposed) | Consistent? |
|-----------|-------------------|----------------|--------------------------|-------------|
| Icon | 🖼 | 🗘 | 📄 | Yes (emoji, semantic) |
| Category | IO | UTILS | IO | Yes (IO for loaders) |
| NODE_NAME style | "Load Image From Path" | "For Each Filename" | "Batch Load Text" | Yes (verb phrase) |
| directory param | (not present) | STRING, input_directory | STRING, input_directory | Yes (matches ForEachFilename) |
| pattern param | (not present) | STRING, "*.jpg" | STRING, "*.txt" | Yes (matches pattern, differs default) |
| Error function | (implicit) | on_node_error() | on_node_error() | Yes |
| SIGNATURE_SUFFIX | " [DVB]" | " [DVB]" | " [DVB]" | Yes (automatic) |

### 4.2 Config System Compatibility

节点 MUST 兼容现有 `DVB_Config` UI 配置项：
- `ui.top_category` -- 自动在 CATEGORY 前添加顶层类别
- `ui.prepend_icon_to_node` / `ui.append_icon_to_node` -- 图标显示位置由用户配置控制
- `ui.category_icons` -- 类别图标叠加

节点 MUST NOT 硬编码类别路径或图标显示位置。

### 4.3 node_list.json Registration

节点 MUST 通过 `_NODE_CLASSES` 列表注册（追加在 `__init__.py` 的列表末尾），MUST NOT 使用独立的注册机制。`update_node_index()` 会在启动时自动将新节点名加入 `node_list.json`。
