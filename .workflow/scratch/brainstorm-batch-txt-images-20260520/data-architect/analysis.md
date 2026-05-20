# Data Architect Analysis — Index

## Role Overview

从数据架构师角度，核心关注点在于：文件扫描结果的数据结构如何与现有 ForEachState、FrameSet 体系兼容；文本内容在内存中的表示和生命周期；以及数据模型能否在避免破坏现有图像管线的前提下支持未来扩展。

## Feature-Point Index

| Feature | Key Decisions |
|---------|--------------|
| F-001 Shared File Loading Core | FileEntry 数据类、三种排序策略、encoding 数据流、ForEachState schema 扩展 |
| F-003 Batch Text Load Node | 单一聚合 STRING 输出、大文本 lazy load 策略、max_files 截断机制 |

## Cross-Cutting Concerns

- ForEachState schema 向后兼容扩展（{filepath: bool} → {filepath: {done, encoding, size}}）
- FileScanner 类型无关抽象
- FrameSet 与文本数据隔离

## Key Recommendations

1. 引入 `FileEntry` 数据类封装文件路径、名称、序号和可选元数据
2. 文件扫描模块独立化为类型无关的 `FileScanner`
3. 输出采用单一聚合 STRING，分隔符可自定义
4. 大文件 MUST 延迟读取，超过 max_files MUST 截断
