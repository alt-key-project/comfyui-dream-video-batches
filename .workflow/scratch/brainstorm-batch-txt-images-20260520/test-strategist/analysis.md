# Test Strategist Analysis: Batch Text File Loader

## Role Perspective Overview

作为测试策略师，本分析关注「Shared File Loading Core (F-001)」和「Batch Text Load Node (F-003)」两个功能的验证策略。核心挑战在于：ComfyUI 自定义节点无传统单元测试框架，测试依赖 ComfyUI 运行时环境。因此测试策略聚焦于三个方向：(1) 核心逻辑的可测试性设计——使关键路径能在无 ComfyUI 条件下独立验证；(2) 集成测试场景矩阵——覆盖 guidance-specification 中确认的全部边界场景；(3) 回归安全网——确保现有 ForEachFilename / ForEachCheckpoint 行为和性能不受影响。

## Feature Point Index

| Feature | Analysis File | Key Decisions |
|---------|--------------|---------------|
| F-001 Shared File Loading Core | [analysis-F-001-shared-file-loading-core.md](./analysis-F-001-shared-file-loading-core.md) | ForEachState 纯函数测试、文件扫描逻辑脱离 ComfyUI 可验证、状态隔离正确性 |
| F-003 Batch Text Load Node | [analysis-F-003-batch-text-load-node.md](./analysis-F-003-batch-text-load-node.md) | 15 个测试场景（正常/边界/异常）、测试数据目录结构、examples/ 测试工作流设计 |

## Cross-Cutting Concerns

See [analysis-cross-cutting.md](./analysis-cross-cutting.md)

## Key Recommendations

1. **可测试性优先设计**: `core/file_loader.py` 的公开函数 MUST 接受文件系统路径和文件列表作为参数，而非依赖全局状态或 ComfyUI 内部机制。这使得核心逻辑可在标准 Python 解释器中直接验证。
2. **ForEachState 隔离验证**: ForEachState 自身是纯 JSON 文件操作类，MUST 验证以下隔离属性：不同 `id` 的 statefile 路径不重叠、并发写入场景下的数据一致性、空目录/无匹配文件时的 `pop()` 行为。
3. **测试数据标准化**: 在 `examples/test-data/` 下建立标准化的测试数据目录结构，覆盖正常、Unicode 文件名、非顺序命名、空文件、大文件等场景。
4. **回归基线**: 在新增代码前后，MUST 运行 `examples/` 中现有工作流（blend-example.json, transitions.json 等），验证无行为退化。
5. **性能基准定义**: 200 文件加载时间 SHOULD 控制在 5 秒以内（SSD 条件下），内存增长 SHOULD 不超过加载文件总大小的 3 倍。
