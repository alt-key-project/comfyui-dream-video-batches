---
title: "Coding Conventions"
readMode: required
priority: high
category: coding
keywords:
  - style
  - naming
  - import
  - pattern
  - convention
  - formatting
---

# Coding Conventions

Auto-generated from project analysis. Update manually as patterns evolve.

## Formatting
- Indentation: 4 spaces
- Encoding: `# -*- coding: utf-8 -*-` header on most files
- Line endings: LF
- No formatter config detected (no .editorconfig, no .prettierrc)
- Comments: minimal, Chinese-capable

## Naming
- Classes: PascalCase (`DVB_LoadImageFromPath`, `FrameSet`, `NodeCategories`)
- Functions/methods: snake_case (`on_node_error`, `gc_comfyui`, `list_files_in_directory`)
- Constants: UPPER_SNAKE_CASE for class-level constants (`TYPE_NAME`, `NODE_NAME`, `CATEGORY`)
- Class name prefix: `DVB_` for all node classes
- Files: snake_case (`dvb_image.py`, `batch_processing.py`, `node_support.py`)

## Imports
- Style: mixed — named imports from local modules, wildcard imports (`from .core import *`)
- Order: stdlib → third-party → local (`.` prefix for intra-package)
- Common pattern: `from .categories import *` + `from .core import *`

## Patterns
- Node class MUST have: `NODE_NAME`, `CATEGORY`, `RETURN_TYPES`, `RETURN_NAMES`, `FUNCTION` class attributes
- Input definition: `@classmethod INPUT_TYPES(cls)` returns dict with "required" and optional "optional"
- Error reporting: `on_node_error(cls, message)` from `core/err.py` — raises Exception
- GPU cleanup: `gc_comfyui()` before/after batch operations
- Config access: `DVB_Config().get("dotted.path.key", default)`
- Node registration: classes added to `_NODE_CLASSES` list in `__init__.py`

## Entries

