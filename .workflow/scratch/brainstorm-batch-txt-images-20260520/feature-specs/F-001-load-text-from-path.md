# F-001: Load Text From Path

## 1. Requirements Summary

- The node MUST accept a file path (STRING) as input
- The node MUST read the text file content and output it as a single STRING
- The node MUST support configurable text encoding via an `encoding` parameter (default: `"utf-8"`)
- The node SHOULD detect file changes via hash-based `IS_CHANGED` (analogous to `DVB_LoadImageFromPath`)
- The node MUST follow the existing node naming convention (`NODE_NAME` + ` [DVB]`)
- The node MUST be a pure incremental addition — no existing files modified

## 2. Design Decisions

### DD-001: Mirror DVB_LoadImageFromPath Structure

The new node SHALL follow `DVB_LoadImageFromPath` as a structural template:
- Same `CATEGORY`: `NodeCategories.IO`
- Same input pattern: single `image_path` equivalent (`text_path`)
- Same output pattern: single typed output (`STRING` instead of `IMAGE`)
- Same `IS_CHANGED` hash-based change detection

**Rationale**: Consistency reduces user learning cost. Users familiar with `DVB_LoadImageFromPath` will immediately understand `DVB_LoadTextFromPath`.

### DD-002: Encoding Parameter

The node MUST expose an optional `encoding` parameter:
- Type: dropdown or STRING input
- Default: `"utf-8"`
- Common options: `utf-8`, `gbk`, `gb2312`, `latin-1`, `utf-16`
- On decode error: use Python's `errors="replace"` strategy (replace undecodable bytes with U+FFFD)

**Rationale**: Chinese users (primary audience of this project) commonly encounter GBK-encoded text files. `errors="replace"` prevents single file encoding issues from breaking the entire workflow.

### DD-003: No ForEach Dependency

This node SHALL NOT depend on or modify ForEachFilename/ForEachDone. It operates on a single file path, making it composable with any upstream node that outputs a file path — including but not limited to ForEachFilename.

**Rationale**: Separation of concerns. File iteration and file reading are orthogonal capabilities.

### DD-004: Empty/Missing File Handling

- If file path is empty string: return empty STRING (matching `DVB_LoadImageFromPath` behavior)
- If file does not exist: call `on_node_error()` which raises an exception (matching existing error patterns)
- If file cannot be read (permissions): call `on_node_error()`

**Rationale**: Consistent error behavior with existing nodes.

## 3. Interface Contract

### Node Definition

```python
class DVB_LoadTextFromPath:
    NODE_NAME = "Load Text From Path"
    ICON = "📄"
    CATEGORY = NodeCategories.IO
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "result"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_path": ("STRING", {"default": '', "multiline": False}),
                "encoding": (["utf-8", "gbk", "gb2312", "latin-1", "utf-16",
                              "ascii", "utf-8-sig", "shift_jis", "euc-kr"],),
            }
        }

    @classmethod
    def IS_CHANGED(cls, text_path, encoding, **kwargs):
        # Hash-based change detection like DVB_LoadImageFromPath
        ...

    def result(self, text_path, encoding, **other):
        ...
```

### Registration

In `__init__.py`:
- Add `DVB_LoadTextFromPath` to `_NODE_CLASSES` list (append at end)
- No other changes required

## 4. Constraints & Risks

- **R1**: Large text files (>10MB) may cause UI lag when passed through ComfyUI's STRING type. Consider adding a warning for files >1MB.
- **R2**: Binary files opened as text will produce garbage. No format detection is performed (Non-Goal: text preprocessing).
- **R3**: The node creates no new file dependencies — all logic is self-contained in a new `text_loaders.py` module.

## 5. Acceptance Criteria

- [ ] DVB_LoadTextFromPath node appears in ComfyUI under `DVB/💾 io`
- [ ] Node loads a .txt file and outputs its content as STRING
- [ ] Encoding parameter changes the decoding behavior correctly
- [ ] Empty path returns empty string (no crash)
- [ ] Missing file raises an exception with clear error message
- [ ] IS_CHANGED returns different hash when file content changes
- [ ] Existing nodes (DVB_LoadImageFromPath, ForEachFilename, etc.) behave identically
- [ ] Works in combo: `ForEachFilename → DVB_LoadTextFromPath → ... → ForEachDone`

## 6. Detailed Analysis References

- @[system-architect/analysis.md](../system-architect/analysis.md)
- @[data-architect/analysis.md](../data-architect/analysis.md)
- @[ux-expert/analysis-F-003-batch-text-load-node.md](../ux-expert/analysis-F-003-batch-text-load-node.md)
- @[guidance-specification.md](../guidance-specification.md) — Section 6.3 (Error Handling), Section 10 (Feature Decomposition)

## 7. Cross-Feature Dependencies

- **Existing**: `DVB_LoadImageFromPath` (loaders.py) — structural reference
- **Existing**: `DVB_ForEachFilename` / `DVB_ForEachCheckpoint` (utility.py) — composable upstream/downstream
- **Existing**: `on_node_error()` (core/err.py) — error reporting
- **No new intra-project dependencies**

---

*Generated from cross-role synthesis at 2026-05-20*
