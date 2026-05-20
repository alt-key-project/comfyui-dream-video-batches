# UX Expert Analysis: Batch Text Loader

## Role Perspective Overview

作为 UX 专家，本分析从 ComfyUI 节点使用者的实际工作流体验出发，评估批量文本加载功能的设计。核心关注点包括：节点可发现性、参数面板直觉性、错误信息可操作性、以及与现有 DVB 节点生态的一致性。分析基于对现有 DVB 节点 UX 模式的梳理（命名规范、分类体系、图标语言、参数风格、错误处理），确保新增节点在用户心智模型中自然融入。

ComfyUI 用户群体以视觉创作者为主，多数不具备编程背景。因此，每个参数的命名、默认值和排列顺序 MUST 降低认知负荷，避免暴露内部实现细节。

## Feature Point Index

| Feature | Analysis File | Key Decisions |
|---------|--------------|---------------|
| F-001 Shared File Loading Core | [analysis-F-001-shared-file-loading-core.md](./analysis-F-001-shared-file-loading-core.md) | 参数命名继承 ForEachFilename 风格；共享核心接口对用户不可见 |
| F-003 Batch Text Load Node | [analysis-F-003-batch-text-load-node.md](./analysis-F-003-batch-text-load-node.md) | 节点名 "Batch Load Text [DVB]"；图标 📄；类别 DVB/io；固定 N 端口输出 |

## Cross-Cutting Concerns

See [analysis-cross-cutting.md](./analysis-cross-cutting.md)

## Key Recommendations

1. **节点命名 MUST 遵循现有 3-4 词模式** — "Batch Load Text" 与 "Load Image From Path"、"For Each Filename" 保持一致的简洁动词短语风格
2. **参数顺序 SHOULD 按使用频率降序排列** — directory（必填高频）> pattern（常改中频）> encoding（少改低频）> max_files（可选安全阀）
3. **输出端口 SHOULD 采用固定 N 端口模型** — 以 max_files 参数控制输出端口数量，避免 ComfyUI 动态端口的技术限制影响用户工作流
4. **错误信息 MUST 包含可操作建议** — 不只是报告 "目录不存在"，而应提示 "请检查路径是否正确" 或 "支持的编码格式列表"
5. **图标 SHOULD 使用 📄 表示文本文件加载** — 与 🖼 表示图像加载形成语义对称，延续 emoji 图标体系
