# Guidance Specification: Batch Text File Loader

## 1. Project Positioning & Goals

**What**: 为 ComfyUI Dream Video Batches 节点包新增批量文本文件加载能力——用户指定目录和 glob 模式，一键加载所有匹配的文本文件内容。

**Core Value**: 简化 AnimateDiff / Stable Video Diffusion 工作流中的批量文本处理（如逐帧 prompt 加载），避免手动连接多个单文件加载节点。

**Primary Goals**:
- 提供 BatchLoadText 节点，从目录批量加载 `.txt` 文件
- 构建共享文件加载核心，为未来批量图像加载预留扩展点
- 100% 向后兼容——现有节点和行为不受影响

## 2. Concepts & Terminology

| Term | Definition | Category |
|------|------------|----------|
| Batch Loader | 从目录中按 glob 模式匹配并批量加载多个文件的节点 | core |
| ForEachState | 现有 JSON 文件状态追踪机制，记录批处理进度 | technical |
| Glob Pattern | 文件路径通配符匹配（如 `*.txt`, `prompt_*.txt`） | technical |
| File Sorting | 按操作系统默认文件名排序（`sorted()` 自然排序） | technical |
| STRING List | ComfyUI STRING 类型的列表输出，每个元素对应一个文件内容 | technical |
| Encoding Parameter | 用户可指定的文本编码（默认 UTF-8），按标准库 codec 名称 | technical |

## 3. Non-Goals (Out of Scope)

- **视频文件直接加载** — 不处理 .mp4/.avi 等视频格式帧提取
- **远程 URL 加载** — 不支持 HTTP/HTTPS 远程文件获取
- **文本高级预处理** — 不对 txt 内容做语义分析、模板解析、格式化处理；原样输出文件内容
- **图像+文本混合配对** — 同一任务中不同时加载图像和文本，各自独立操作

## 4. System Architect Decisions

### 4.1 Architecture Strategy

**CONFIRMED**: 采用「独立节点 + 共享核心」架构。

- 新增 `core/file_loader.py` 作为共享文件加载基础设施，MUST 包含文件扫描、排序、状态管理逻辑
- 新增 `text_loaders.py` 作为批量文本加载节点模块
- 现有 `loaders.py` (DVB_LoadImageFromPath) MUST NOT 被修改
- 现有 `utility.py` (ForEachFilename/ForEachCheckpoint) MUST NOT 被修改
- `ForEachState` 机制 SHOULD 被复用（而非重新实现状态追踪）

### 4.2 State Tracking

**CONFIRMED**: 复用现有 `ForEachState` JSON 状态追踪机制。

- `ForEachState.__init__(filepath)`, `.add_files_to_process(files)`, `.pop()`, `.mark_done(filename)` 直接可用
- 无需新增状态存储抽象

### 4.3 Backward Compatibility

**CONFIRMED**: 纯增量添加策略。

- `__init__.py` 中 `_NODE_CLASSES` 列表仅追加新类，MUST NOT 修改或删除已有条目
- 新节点使用独立的 NODE_NAME 和 CATEGORY

## 5. Data Architect Decisions

### 5.1 Text Output Data Model

**CONFIRMED**: 纯文本输出，不绑定 FrameSet。

- 批量文本加载节点 RETURN_TYPES MUST 为 `("STRING",)` 或 `("STRING", "STRING", ...)`
- 每个文件的内容作为一个独立 STRING 输出
- 不需要创建 FrameSet（因为没有图像数据）

### 5.2 Image+Text Mixing

**CONFIRMED**: 不支持同时混合加载图像和文本。

- 共享核心 (`file_loader.py`) SHALL 设计为类型无关，但每个节点实例只处理一种文件类型
- 如需同时加载图像和文本，用户 SHOULD 使用两个独立节点

### 5.3 Encoding Strategy

**CONFIRMED**: UTF-8 默认 + 用户可指定编码。

- `encoding` 参数默认值 MUST 为 `"utf-8"`
- 用户 SHOULD 能从节点参数面板选择编码（如 `utf-8`, `gbk`, `latin-1`）
- 编码错误时 SHOULD 使用 `errors="replace"` 策略，避免整个加载失败

## 6. UX Expert Decisions

### 6.1 User Workflow

**CONFIRMED**: 一键式加载节点。

- 用户输入：`directory` (STRING) + `pattern` (STRING, default: `"*.txt"`) + `encoding` (STRING, default: `"utf-8"`)
- 节点执行：扫描 → 排序 → 逐文件读取内容 → 输出 STRING 列表
- 输出端口数量 SHOULD 根据实际加载文件数动态或固定（如输出前 N 个文本）

### 6.2 Parameter Complexity

**CONFIRMED**: ForEachFilename 风格参数面板。

- 参数数量控制在 3-4 个（directory, pattern, encoding, 可选的 max_files）
- MUST NOT 暴露内部实现细节（如 statefile 路径）

### 6.3 Error Handling

**CONFIRMED**: 遵循现有项目错误处理模式。

- 文件不存在或无匹配文件时 MUST 调用 `on_node_error()` 抛出异常
- 单个文件读取失败时 SHOULD 调用 `on_node_error()` 终止整个加载
- 编码错误使用 `errors="replace"` 静默替换，不中断加载

## 7. Test Strategist Decisions

### 7.1 Test Approach

**CONFIRMED**: ComfyUI 集成测试 + 现有风格。

- 测试方式：在 ComfyUI 中加载节点并运行，检查输出正确性
- 不引入 pytest 等外部测试框架
- 可在 `examples/` 目录中增加测试用工作流 JSON + 测试数据

### 7.2 Boundary Scenarios

以下场景 MUST 被测试覆盖：

- **大量文件** (200+): 确保状态追踪正确，内存不泄漏
- **特殊字符文件名**: Unicode 文件名（中文、emoji、空格）正确处理
- **非顺序命名**: `frame_001.txt, frame_005.txt, frame_100.txt` 等非连续命名，按文件名自然排序
- **空文件**: 内容为空字符串的 txt 文件
- **缺少文件**: 目录中无匹配文件时的错误提示

## 8. Cross-Role Integration

- **sys-arch ↔ data-arch**: `file_loader.py` 的接口设计需要同时满足文本加载（当前需求）和未来图像加载（预留）的抽象需求
- **sys-arch ↔ ux-expert**: 共享核心的接口不应泄露到用户可见的参数面板
- **data-arch ↔ ux-expert**: 输出 STRING 列表的节点输出端口命名需清晰（如 `text_1`, `text_2`, ... 或 `texts` 聚合输出）
- **test-strategist ↔ sys-arch**: ForEachState 复用后，测试需验证与现有 ForEachFilename 节点不产生状态冲突

## 9. Risks & Constraints

- **输出端口数量**: ComfyUI 节点输出端口是固定的，批量加载的文件数量是动态的。需要决定是固定 N 个输出端口还是使用聚合输出
- **ForEachState ID 隔离**: 批量加载节点和 ForEachFilename 节点使用不同 ID 时 MUST NOT 互相干扰
- **大文件性能**: 单个 txt 文件过大 (>10MB) 时的内存占用需评估

## 10. Feature Decomposition

| ID | Feature | Description | Priority | Dependencies |
|----|---------|-------------|----------|-------------|
| F-001 | Shared File Loading Core | `core/file_loader.py`: 文件扫描、排序、过滤、状态管理的基础设施 | MUST | ForEachState (existing) |
| F-003 | Batch Text Load Node | `text_loaders.py`: DVB_BatchLoadText 节点，目录+pattern+encoding → STRING 输出 | MUST | F-001 |

## 11. Appendix: Decision Tracking

| # | Role | Question | Decision | Rationale |
|---|------|----------|----------|-----------|
| 1 | sys-arch | 架构策略 | 独立节点 + 共享核心 | 最大化复用，最小化对现有代码的侵入 |
| 2 | sys-arch | 状态追踪 | 复用 ForEachState | 已有成熟机制，避免重复造轮子 |
| 3 | sys-arch | 向后兼容 | 纯增量添加 | 现有用户工作流零影响 |
| 4 | data-arch | 文本数据模型 | 纯文本输出（STRING 列表） | 用户确认不混合图像和文本 |
| 5 | data-arch | 混合加载 | 不支持 | 同一任务只处理一种文件类型 |
| 6 | data-arch | 编码策略 | UTF-8 默认 + 编码参数 | 国际化和灵活性平衡 |
| 7 | ux-expert | 工作流 | 一键式加载节点 | 最低学习成本 |
| 8 | ux-expert | 参数复杂度 | ForEachFilename 风格 | 与现有节点保持一致性 |
| 9 | ux-expert | 错误处理 | 遵循现有 on_node_error 模式 | 项目一致性 |
| 10 | test-strategist | 测试方式 | ComfyUI 集成测试 | 无外部框架依赖 |
| 11 | test-strategist | 边界场景 | 大量文件、特殊文件名、非顺序命名 | 用户明确的关注点 |
| 12 | conflict | 文本输出格式 | 纯文本输出（空帧方案被否决） | 用户确认不需要 FrameSet 包装 |
| 13 | feature | 功能范围 | 专注文本节点，暂不搞图像 | 用户明确限定范围 |

---

*Generated by /maestro-brainstorm auto mode at 2026-05-20*
*Roles: system-architect, data-architect, ux-expert, test-strategist*
