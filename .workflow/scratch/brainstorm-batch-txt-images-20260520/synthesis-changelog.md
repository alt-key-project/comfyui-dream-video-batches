# Synthesis Changelog

## Session: brainstorm-batch-txt-images-20260520

### Direction Change (EP-001)

**What changed**: 从"批量加载节点 + 共享核心"架构重定向为"单文件加载节点（文本版 LoadImageFromPath）"

**Why**: 用户在 Phase 4.5 发现方向偏离，指出真正需要的是 ForEach 循环模式——现有的 `ForEachFilename` 已经解决了目录扫描+文件迭代问题，只需要一个 `DVB_LoadTextFromPath` 节点来读取单个文本文件，就像 `DVB_LoadImageFromPath` 读取单个图像一样。

**Before**:
- F-001: Shared File Loading Core (core/file_loader.py)
- F-003: Batch Text Load Node (one-shot load all)

**After**:
- F-001: Load Text From Path (text_loaders.py: DVB_LoadTextFromPath)
- Scope reduced from ~300 lines to ~60 lines
- Zero new core infrastructure needed
- Zero modifications to existing files

### Conflicts Resolved

| Conflict | Resolution |
|----------|-----------|
| Output port strategy (aggregated vs fixed-N vs list) | Aggregated STRING (moot after simplification — single file, single STRING) |
| max_files parameter | Removed — not applicable to single-file node |
| Node category | IO (confirmed, matching DVB_LoadImageFromPath) |
| Node name | "Load Text From Path" (mirrors "Load Image From Path") |

### Clarifications

- User confirmed: no need for simultaneous image+text loading
- User confirmed: ForEach iteration pattern (not batch-all-at-once)
- User confirmed: pure incremental addition

### Roles Participated
- system-architect: Architecture strategy, API design
- data-architect: Data model, encoding, FileEntry (simplified post-redirect)
- ux-expert: Node UX, parameter design, error messages
- test-strategist: Test scenarios, boundary cases

### Complexity Score: 1/8 (was ~4 before re-scope)
