# Roadmap: comfyui-dream-video-batches

## Overview

新增 `DVB_LoadTextFromPath` 节点，填补 ComfyUI 生态中缺失的文本文件加载能力。镜像现有的 `DVB_LoadImageFromPath` 设计，接收文件路径 → 输出 STRING 文本内容。配合 `ForEachFilename` 即可实现文本文件的 for 循环批量处理——这是市面上稳定可用的罕见能力。

## Phases

- [ ] **Phase 1: Load Text From Path** — 新增文本文件加载节点，支持编码配置，与 ForEachFilename 无缝协作

## Phase Details

### Phase 1: Load Text From Path
**Goal**: 新增 `DVB_LoadTextFromPath` 节点，用户可通过文件路径加载文本内容并输出为 STRING
**Depends on**: Nothing (first phase)
**Requirements**: REQ-001 (Load Text From Path)
**Success Criteria** (what must be TRUE):
  1. `DVB_LoadTextFromPath` 节点出现在 ComfyUI 节点列表 `DVB/💾 io` 分类下
  2. 节点接收 `text_path` (STRING) + `encoding` (dropdown, default utf-8)，输出 `text` (STRING)
  3. 空路径返回空字符串（不崩溃），缺失文件调用 `on_node_error()` 抛出异常
  4. `IS_CHANGED` 基于文件内容哈希检测变更（镜像 `DVB_LoadImageFromPath`）
  5. 现有节点行为不受影响（纯增量添加：新增 `text_loaders.py` + 在 `__init__.py` 末尾注册）
  6. 可与 `ForEachFilename → DVB_LoadTextFromPath → ... → ForEachDone` 组合实现文本批处理循环

### Tasks

| # | Task | Type | Description |
|---|------|------|-------------|
| 1 | 创建 text_loaders.py | impl | 新建模块，定义 `DVB_LoadTextFromPath` 节点类 |
| 2 | 注册节点 | impl | 在 `__init__.py` 的 `_NODE_CLASSES` 末尾追加 `DVB_LoadTextFromPath` |
| 3 | 验证 | test | 在 ComfyUI 中加载节点，测试正常路径/空路径/不存在路径/编码切换 |
| 4 | 示例工作流 | docs | 在 `examples/` 添加 `load-text-from-path.json` 示例 |

## Scope Decisions

- **In scope**: `DVB_LoadTextFromPath` 节点（text_path + encoding → STRING）
- **Deferred**: 批量加载节点变体（批量图像加载、混合加载等——有 ForEachFilename 就够了）
- **Out of scope**: 文本内容预处理/解析、远程 URL 加载、视频文件解码

## Progress

| Phase | Status | Completed |
|-------|--------|-----------|
| 1. Load Text From Path | Not started | - |

---
*Created: 2026-05-21 | Mode: light | Strategy: direct*
