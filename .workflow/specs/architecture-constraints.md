---
title: "Architecture Constraints"
readMode: required
priority: high
category: arch
keywords:
  - architecture
  - module
  - layer
  - boundary
  - dependency
  - structure
---

# Architecture Constraints

Auto-generated from project structure. Update manually as architecture evolves.

## Module Structure
- Type: single-package ComfyUI custom node
- Entry point: `__init__.py` (node registration + manifest)
- Core library: `core/` — shared data structures and utilities
- Node modules: root-level `.py` files (one per category: `camera.py`, `transitions.py`, etc.)
- Examples: `examples/` — workflow JSON files + sample images
- Config: `config.json` — UI customization (icons, categories)

## Layer Boundaries

```
__init__.py          → 注册层：将所有节点类注册到 ComfyUI
  ├── calculate.py   → 节点层：ComfyUI 节点类（UI + 业务逻辑）
  ├── camera.py
  ├── cutandjoin.py
  ├── ...其他节点模块...
  └── core/          → 核心层：纯数据结构 + 工具函数
       ├── frameset.py    (FrameSet, IndexedImage)
       ├── dvb_image.py   (DVB_Image — PIL/Tensor 转换)
       ├── batch_processing.py (DVB_ImageBatchProcessor)
       ├── config.py      (DVB_Config)
       ├── utility.py     (ForEachState)
       ├── statestore.py  (DRV_StateFile, DRV_StateStore)
       ├── partial_prompt.py (PartialPrompt)
       ├── vector.py      (Vector2d, Quad2d)
       ├── memory.py      (gc_comfyui)
       └── err.py         (on_node_error, raise_error)
```

## Dependency Rules
- `core/` MUST NOT import from node modules (root `.py` files)
- Node modules MAY import `from .core import *` and `from .categories import *`
- `core/` modules MAY import from each other
- No circular dependencies detected in current codebase
- New nodes MUST follow the pattern: one module per logical category

## Technology Constraints
- Runtime: Python 3.x (embedded in ComfyUI or system Python)
- Framework: ComfyUI custom node protocol
- Key dependencies: torch, Pillow, numpy, scipy, imageio, evaluate
- Node naming: `{ClassName} [DVB]` suffix applied automatically
- Category hierarchy: `DVB / {icon} {subcategory}`

## Entries

