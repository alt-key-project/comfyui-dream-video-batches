# System Architect Analysis: Batch Text File Loader

## Role Perspective Overview

从系统架构师视角分析 Batch Text File Loader 功能。该功能为 comfyui-dream-video-batches 包新增文本文件批量加载能力，复用现有 ForEachState 状态追踪机制，遵循纯增量添加原则——不修改任何现有文件，所有新代码以独立模块形式注入。

核心架构决策：在 `core/file_loader.py` 中建立共享文件加载抽象层，将文件发现（glob 匹配）和文件读取（编码感知的文本 I/O）解耦为独立职责。节点层 `text_loaders.py` 调用共享核心，处理 ComfyUI 节点生命周期和错误报告。

## Feature Point Index

| Feature | Analysis File | Key Decisions |
|---------|--------------|---------------|
| F-001 Shared File Loading Core | [analysis-F-001-shared-file-loading-core.md](./analysis-F-001-shared-file-loading-core.md) | 纯函数 API 设计，文件发现与读取分离，utf-8 默认编码 |
| F-003 Batch Text Load Node | [analysis-F-003-batch-text-load-node.md](./analysis-F-003-batch-text-load-node.md) | STRING 列表输出（利用 ComfyUI 列表迭代），节点注册隔离 |

## Cross-Cutting Concerns

See [analysis-cross-cutting.md](./analysis-cross-cutting.md)

## Key Recommendations

1. **共享核心与节点层严格分离**：`core/file_loader.py` MUST 不依赖任何 ComfyUI 特定类型或节点类，仅提供纯 Python 函数。节点层负责类型适配和错误报告。

2. **输出策略利用 ComfyUI 列表语义**：`DVB_BatchLoadText` 的 STRING 输出 SHOULD 返回 Python 列表，利用 ComfyUI 原生的列表迭代机制，使下游节点每次处理单个文件内容。

3. **ForEachState 在共享核心中保持可选**：文件发现和读取函数 MUST 不直接依赖 ForEachState；节点层 MAY 选择性地使用 ForEachState 实现工作流状态追踪。

4. **编码参数设计为可选输入**：`encoding` SHOULD 作为节点的 optional 输入，默认值为 `"utf-8"`，遵循用户决策。

5. **排序一致性**：文件列表 MUST 使用 `sorted()` 自然排序，与 `ForEachState.pop()` 的 `sorted()` 行为一致，确保可预测的处理顺序。
