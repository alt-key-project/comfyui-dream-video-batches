# Project: comfyui-dream-video-batches

## What This Is

为 ComfyUI 提供视频批处理工具节点包，核心抽象是 FrameSet（带索引和帧率的图像序列）。服务于 AnimateDiff 和 Stable Video Diffusion 等 AI 视频生成工作流。

## Core Value

填补 ComfyUI 生态中缺失的稳定批处理节点——特别是文本文件的 for 循环处理能力。市面上图像批处理节点不少，但稳定可用的文本迭代节点几乎没有。

## Requirements

### Validated

<!-- 从现有代码库推断的已发布功能 -->

- FrameSet 核心数据模型（tensor + 帧率 + 索引）
- 图像批量处理器（DVB_ImageBatchProcessor + 回调模式）
- 相机动画系统（线性/正弦：平移、缩放、旋转）+ 2D 几何引擎
- 视频过渡效果（淡入淡出、渐变过渡）
- 表达式求值计算（30+ 数学函数）
- 输入控件（Text/String/Float/Int）
- 加权提示词构建系统（PartialPrompt + 随机调度生成）
- 文件迭代系统（ForEachFilename + ForEachDone + ForEachState）
- 单图像加载（LoadImageFromPath + SHA256 变更检测）
- 补间帧生成（BLEND/CLOSEST/PREVIOUS 三种模式）
- FrameSet 编辑操作（重索引、偏移、分割、合并、反转、追加、重复）
- UI 配置系统（DVB_Config + 图标 + 类别层级）

### Active

- [ ] **Load Text From Path** — 新增 `DVB_LoadTextFromPath` 节点：文件路径 → STRING 文本内容，配合现有 ForEachFilename 实现文本文件的 for 循环批量处理

### Out of Scope

- 视频文件直接解码（.mp4/.avi） — 属于其他节点包（如 VideoHelperSuite）的职责
- 远程 URL 文件加载 — 保持本地文件系统专注
- 文本内容语义分析/模板解析 — 保持纯数据通道角色，处理逻辑留给下游节点

## Context

- 项目由 "Dream Project"（Alt Key Project）维护，用于自身的 AI 视频制作需求（YouTube 频道）
- 同时被其他 ComfyUI 节点包作为基础设施依赖（Frame Interpolation、AnimateDiff Evolved、VideoHelperSuite、Stable Video Diffusion）
- 现有 28 个活跃节点，12 个功能模块
- 版本 1.2.0，发布在 GitHub

## Constraints

- **向后兼容**: MUST NOT 修改现有节点的 API、行为或输出格式 — 所有扩增必须是纯增量
- **零新依赖**: SHOULD NOT 引入新的 Python 包依赖（除非有压倒性理由）
- **无外部服务**: MUST NOT 依赖网络连接或外部 API

## Tech Stack

- **Language**: Python 3.x
- **Framework**: ComfyUI 自定义节点协议
- **核心依赖**: torch (Tensor 处理), PIL/Pillow (图像处理), numpy, scipy, imageio, evaluate

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FrameSet 作为核心抽象 | 统一图像批处理的帧率和索引管理 | 已验证，28 节点基于此模型 |
| PIL/Tensor 双模式图像（DVB_Image） | 延迟转换避免不必要的格式开销 | 已验证 |
| ForEachState JSON 文件追踪批处理进度 | 简单、跨会话持久、无数据库依赖 | 已验证 |
| 纯增量添加策略 | 保护现有用户工作流 | 所有新节点通过追加注册 |
| LoadTextFromPath 镜像 LoadImageFromPath | 降低用户学习成本，保持 API 一致性 | — Pending |

## Stakeholders

- ComfyUI + AnimateDiff 视频创作者
- 下游节点包维护者（依赖 FrameSet 抽象）
- Dream Project 自身的视频制作管线

---
*Last updated: 2026-05-20 after initialization*
