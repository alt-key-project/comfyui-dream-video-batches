# Cross-Cutting Test Concerns: Batch Text File Loader

## 1. 性能基准

### 1.1 200 文件加载时间基准

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| 200 文件扫描 + 排序 | < 100ms | `glob.glob` + `sorted()` 耗时 |
| 200 文件读入内存 | < 3 秒 | `open().read()` 循环耗时 |
| 200 文件整体加载 (scan + read + state update) | < 5 秒 | ComfyUI 节点端到端耗时 |
| 内存峰值（200 x 1KB 文件） | < 3MB | 加载前后通过 `tracemalloc` 或任务管理器对比 |
| ForEachState JSON 大小（200 entries） | < 15KB | statefile 文件大小 |

### 1.2 性能测试执行方式

由于项目不引入外部测试框架，性能基准 MUST 通过以下方式验证：

- **开发阶段**: 在 ComfyUI 中加载节点，观察控制台输出中的 `pop {}` 打印（ForEachState 自带打印），记录处理时间
- **验证脚本**: `examples/test-data/generate.py` SHOULD 包含 `--benchmark` 选项，执行纯 Python 级别的扫描+读取耗时统计
- **内存观测**: 利用现有的 `DVB_TraceMalloc` 节点（`utility.py` 中已定义但被注释），在测试工作流中插入内存追踪点

### 1.3 性能退化阈值

若加载时间超过基准的 **200%** (即 200 文件 > 10 秒)，SHOULD 视为性能退化的信号，需要排查：
- 是否在循环内进行不必要的文件系统调用
- ForEachState 的 `_save()` 是否在每次 `add_files_to_process` 调用时都写磁盘（当前设计会——200 个文件意味着 200 次 JSON 序列化写入，这是一个潜在的性能瓶颈）

**性能风险提示**: 当前 `ForEachState.add_files_to_process` 每次调用都执行 `json.dumps` + `f.write`。批量添加 200 个文件时，这意味着 200 次全量 JSON 写入。建议在实现 `file_loader.py` 时 MAY 考虑批量更新后统一写入，而非每次 `add_files_to_process` 立即持久化。

## 2. 回归测试策略

### 2.1 现有功能受保护清单

以下现有功能 MUST NOT 因新增代码而产生行为变化：

| 现有功能 | 节点 | 受保护原因 |
|---------|------|-----------|
| 图像文件迭代 | DVB_ForEachFilename | 依赖 ForEachState 核心机制 |
| 迭代完成标记 | DVB_ForEachCheckpoint | 依赖 ForEachState 核心机制 |
| 单图像加载 | DVB_LoadImageFromPath | 独立功能，验证无意外影响 |
| 所有 FrameSet 操作 | FrameSet 全部方法 | 核心数据结构 |
| 配置系统 | DVB_Config | 全局配置单例 |

### 2.2 回归验证清单

每次代码变更后 MUST 执行以下验证：

1. **现有工作流可用性**: 在 ComfyUI 中依次加载 `examples/blend-example.json`、`examples/camera-roll-example.json`、`examples/frame-blend.json`、`examples/transitions.json`，确认每个工作流加载无报错，节点列表无缺失。
2. **ForEachFilename 行为一致性**: 使用 `examples/test-data/basic/` 中的图像文件，运行 ForEachFilename 验证迭代完整性和 `os.unlink` 清理正确性。
3. **node_list.json 完整性**: 验证 `update_node_index()` 运行后，新旧节点的 NODE_NAME 均存在于 `node_list.json` 中。
4. **import 无副作用**: 在 ComfyUI 加载节点时控制台无新增异常。

### 2.3 回归测试工作流设计

建议新增 `examples/test-regression.json`，该工作流 MUST：

- 同时包含 DVB_ForEachFilename 和 DVB_BatchLoadText（若同一工作流中可共存）
- 使用不同的 `id` 值（如 "apple" vs "banana"）确保状态隔离
- 输出结果可对比：ForEachFilename 输出图像数量 vs BatchLoadText 输出文本数量

## 3. 测试数据目录结构建议

### 3.1 完整目录树

```
examples/
  blend-example.json              # 现有 - 不修改
  camera-roll-example.json        # 现有 - 不修改
  frame-blend.json                # 现有 - 不修改
  transitions.json                # 现有 - 不修改
  a.jpg                           # 现有 - 不修改
  b.jpg                           # 现有 - 不修改
  test-batch-text-basic.json      # 新增 - TC-001..TC-004
  test-batch-text-stress.json     # 新增 - TC-005
  test-batch-text-unicode.json    # 新增 - TC-006
  test-batch-text-edge.json       # 新增 - TC-008..TC-011
  test-regression.json            # 新增 - 回归验证
  test-data/
    generate.py                   # 新增 - 测试数据生成脚本
    README.txt                    # 新增 - 测试数据说明
    basic/
      prompt.txt
      frame_001.txt ~ frame_010.txt
      prompt_01.txt, prompt_02.txt, readme.txt, data.csv
      chinese_utf8.txt, japanese_utf8.txt, arabic_utf8.txt
    stress/
      (generate.py --stress 生成)
    unicode/
      chinese_name.txt
      prompt_emoji.txt
      "my prompt.txt"
      "test-file (1).txt"
    sparse/
      frame_001.txt, frame_005.txt, frame_042.txt, frame_100.txt
    edge/
      empty.txt                    (0 字节)
      gbk_encoded.txt              (GBK 编码)
      large_file.txt               (generate.py --large 生成)
    error/
      empty_dir/                   (空目录)
      locked_dir/                  (权限测试 - 手动创建)
```

### 3.2 数据管理原则

- **测试数据 MUST 可生成**: 所有大文件（>1MB）和重复文件（200+）MUST 通过 `generate.py` 生成，不提交到 git。`.gitignore` MUST 排除 `test-data/stress/` 和 `test-data/edge/large_file.txt`。
- **小文件 MAY 提交**: `basic/` 和 `unicode/` 中的小文本文件可提交到 git 作为文档化示例。
- **编码文件标注**: GBK 编码文件 MUST 在 `test-data/README.txt` 中明确标注编码类型，避免开发者误用编辑器修改后保存为 UTF-8。

## 4. 跨功能关注点

### 4.1 ForEachState ID 隔离的测试方法

由于 ForEachState 的文件隔离依赖于 JSON 文件名（`foreach_{id}.json`），验证隔离性最可靠的方法是：

1. 运行 DVB_ForEachFilename(id="apple", directory=DIR_A)
2. 同时运行 DVB_BatchLoadText(id="banana", directory=DIR_A)
3. 验证 DIR_A 下产生两个独立的 statefile：`foreach_apple.json` 和 `foreach_banana.json`
4. 验证两个文件内容互不包含对方的条目

### 4.2 错误处理一致性

新增节点的错误处理 MUST 遵循与现有节点相同的模式：

- 不可恢复错误：调用 `on_node_error(cls, message)` — 打印并抛出异常
- 可恢复警告：使用 `print()` 输出到控制台 — 不中断执行
- 编码错误：`errors="replace"` — 静默替换，这是 guidance-specification 明确确认的策略

### 4.3 与 ComfyUI 节点生命周期的交互

ComfyUI 节点的 `IS_CHANGED` 方法控制缓存失效。ForEachFilename 使用 `return float("NaN")` 确保每次执行都不使用缓存。DVB_BatchLoadText MUST 评估是否需要类似策略：

- 若文件内容可能在两次执行间变化（用户手动编辑 txt），SHOULD 使用 `float("NaN")` 或文件 hash 策略（参考 DVB_LoadImageFromPath 的 `IS_CHANGED` 实现）
- 若采用缓存策略，MUST 在 `IS_CHANGED` 中加入 directory + pattern + 文件列表 hash 的计算
