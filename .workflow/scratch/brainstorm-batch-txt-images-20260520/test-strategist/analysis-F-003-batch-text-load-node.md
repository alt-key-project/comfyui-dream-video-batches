# F-003: Batch Text Load Node Test Strategy

## 1. 测试场景矩阵

### 1.1 场景分类总览

| 类别 | 场景数 | 覆盖目标 |
|------|--------|---------|
| Normal（正常路径） | 4 | 基本功能、输出正确性、排序一致性 |
| Boundary（边界条件） | 6 | 用户指定的边界场景（200+, Unicode, 非顺序, 空文件, 大文件, 编码） |
| Exception（异常路径） | 5 | 错误处理、参数校验、资源清理 |

### 1.2 详细测试用例

以下 15 个测试用例覆盖 guidance-specification Section 7.2 指定的全部边界场景。

---

**TC-001: 基础单文件加载**
- 场景类别: Normal
- 输入: 目录含 1 个 `prompt.txt`，内容 `"a beautiful sunset"`
- 预期: 输出 1 个 STRING，内容为 `"a beautiful sunset"`
- 验证点: 输出类型、内容一致性、无首尾空白篡改

**TC-002: 多文件自然排序加载**
- 场景类别: Normal
- 输入: 目录含 `frame_001.txt` 到 `frame_010.txt`，内容各自为 `"frame N"`
- 预期: 输出按文件名自然排序（001, 002, ..., 010），每个输出对应匹配的文件
- 验证点: `sorted()` 自然排序在数字文件名上的行为——注意 `sorted()` 对 `frame_10.txt` vs `frame_2.txt` 的字典序排序

**TC-003: Glob 模式过滤**
- 场景类别: Normal
- 输入: 目录含 `prompt_01.txt`, `prompt_02.txt`, `readme.txt`, `data.csv`
- pattern: `"prompt_*.txt"`
- 预期: 仅加载 `prompt_01.txt` 和 `prompt_02.txt`
- 验证点: glob 匹配正确性、非匹配文件不被加载

**TC-004: UTF-8 多语言内容**
- 场景类别: Normal
- 输入: `chinese.txt` 含中文、`japanese.txt` 含日文、`arabic.txt` 含阿拉伯文（均 UTF-8 编码）
- 预期: 所有文件内容完整保留，无乱码
- 验证点: UTF-8 编解码正确性

**TC-005: 200+ 文件批量加载（性能边界）**
- 场景类别: Boundary (用户指定)
- 输入: 目录含 200 个 `frame_0001.txt` 至 `frame_0200.txt`，每个文件 1KB 内容
- 预期: 全部 200 个文件被加载，顺序正确，内存无泄漏
- 验证点: 加载时间 < 5 秒 (SSD)、ForEachState 状态文件不膨胀、内存增长 < 文件总大小的 3 倍

**TC-006: Unicode 文件名**
- 场景类别: Boundary (用户指定)
- 输入: 文件名含中文（`提示词.txt`）、emoji（`prompt_emoji.txt`）、空格（`my prompt.txt`）、特殊符号（`test-file (1).txt`）
- 预期: 所有文件正确匹配和加载，内容正确
- 验证点: glob 和 `os.path` 对 Unicode 路径的处理、ForEachState JSON 对 Unicode key 的序列化

**TC-007: 非顺序命名**
- 场景类别: Boundary (用户指定)
- 输入: `frame_001.txt`, `frame_005.txt`, `frame_100.txt`, `frame_042.txt`
- 预期: 按文件名自然排序加载（001, 005, 042, 100），顺序可预测且稳定
- 验证点: 排序稳定性——多次运行输出顺序一致

**TC-008: 空文件**
- 场景类别: Boundary
- 输入: 目录含 `empty.txt`（0 字节文件），与正常文件混合
- 预期: `empty.txt` 输出空字符串 `""`，不触发异常，不阻塞其他文件加载
- 验证点: 空文件处理不抛出异常、输出为空字符串而非 None

**TC-009: 大文件加载 (>10MB)**
- 场景类别: Boundary
- 输入: 单个 15MB 的文本文件
- 预期: 成功加载，内容完整
- 验证点: 加载时间 < 3 秒，内存增量合理

**TC-010: GBK 编码文件**
- 场景类别: Boundary
- 输入: 使用 GBK 编码的中文文本文件，`encoding` 参数设为 `"gbk"`
- 预期: 内容正确解码，无乱码
- 验证点: encoding 参数传递链路正确性（节点参数 -> `open(file, encoding=...)`）

**TC-011: 编码错误降级（errors="replace"）**
- 场景类别: Boundary
- 输入: GBK 编码的文件，但 `encoding` 参数设为 `"utf-8"`，`errors="replace"`
- 预期: 加载不中断，不可解码的字符被替换字符替代
- 验证点: `errors="replace"` 策略生效，不抛出 UnicodeDecodeError

**TC-012: 无匹配文件**
- 场景类别: Exception
- 输入: 目录存在但没有任何 `.txt` 文件
- 预期: MUST 调用 `on_node_error()` 抛出异常，提示信息包含目录路径
- 验证点: 错误信息可读性、不产生残留 statefile

**TC-013: 目录不存在**
- 场景类别: Exception
- 输入: `directory` 参数指向不存在的路径
- 预期: MUST 调用 `on_node_error()` 抛出异常
- 验证点: 错误类型明确（目录不存在 vs 无匹配文件区分开）

**TC-014: 权限拒绝**
- 场景类别: Exception
- 输入: 目录存在但无可读权限（或在 Windows 上模拟为文件被独占锁定）
- 预期: MUST 调用 `on_node_error()` 抛出异常
- 验证点: 权限错误与文件不存在错误可通过异常信息区分

**TC-015: ForEachState 文件残留清理**
- 场景类别: Exception
- 输入: 运行一次完整加载后，检查 statefile 是否被清理
- 预期: 全部文件处理完成后（`pop()` 返回 None），statefile SHOULD 被删除（参考 ForEachFilename 的 `os.unlink(statefile)` 模式）
- 验证点: 无残留的 `foreach_*.json` 文件

## 2. 测试数据设计

### 2.1 推荐目录结构

```
examples/test-data/
  basic/                        # TC-001..TC-004
    prompt.txt
    frame_001.txt ~ frame_010.txt
    prompt_01.txt, prompt_02.txt, readme.txt, data.csv
    chinese_utf8.txt, japanese_utf8.txt, arabic_utf8.txt
  stress/                       # TC-005
    frame_0001.txt ~ frame_0200.txt   (生成脚本, 每个 1KB)
  unicode/                      # TC-006
    chinese_name.txt
    prompt_emoji.txt
    my prompt.txt
    test-file (1).txt
  sparse/                       # TC-007
    frame_001.txt, frame_005.txt, frame_042.txt, frame_100.txt
  edge/                         # TC-008..TC-011
    empty.txt
    large_file.txt              (15MB 生成文件)
    gbk_encoded.txt             (GBK 编码中文)
  error/                        # TC-012..TC-015
    empty_dir/                  (空目录用于 "无匹配文件" 测试)
```

### 2.2 测试数据生成脚本

MUST 提供一个 `examples/test-data/generate.py` 脚本。此脚本 MUST 是幂等的——多次运行产生相同输出。

## 3. 建议新增的 examples/ 测试工作流

### 3.1 工作流清单

| 工作流文件 | 测试场景 | 关键验证 |
|-----------|---------|---------|
| `examples/test-batch-text-basic.json` | TC-001..TC-004 | 基本功能端到端验证 |
| `examples/test-batch-text-stress.json` | TC-005 | 200 文件性能 |
| `examples/test-batch-text-unicode.json` | TC-006 | Unicode 文件名 |
| `examples/test-batch-text-edge.json` | TC-008..TC-011 | 空文件、大文件、编码 |

### 3.2 工作流设计模式

每个测试工作流应遵循以下结构：

1. **DVB_BatchLoadText 节点**: 配置 `directory`, `pattern`, `encoding`
2. **DVB_StringTokenizer 节点**: 接到每个输出端口，验证内容分段
3. **DVB_ForEachCheckpoint**: 标记处理完成，驱动多文件迭代
4. **节点注释**: 在 ComfyUI 工作流 JSON 中通过 `title` 属性标注预期结果

### 3.3 输出端口数量决策的测试影响

当前未确定采用「固定 N 个输出端口」还是「聚合输出」。两种方案对测试的影响：

- **固定 N 端口**: 工作流显式连接每个端口到下游节点，测试可精确验证每个端口的输出。适合文件数固定的场景。超出 N 个文件时 MUST 明确行为（截断或报错）。
- **聚合输出（列表）**: 单个端口输出 STRING 列表，由下游节点（如 ForEachFilename 类似机制）迭代消费。测试需验证列表长度和内容对应关系。

**建议**: 优先采用聚合输出（通过 ComfyUI 的 list 输出或 ForEach 模式），降低端口数量固定的限制。但 MUST 确保列表排序与文件排序一致。
