# F-001: Shared File Loading Core — Data Model Analysis

## FileEntry Data Class

文件扫描结果 MUST 从 `List[str]` 升级为 `List[FileEntry]`：

```
FileEntry:
  - filepath: str          # 绝对路径
  - filename: str          # 文件名（含扩展名）
  - stem: str              # 文件名（不含扩展名）
  - index: int | None      # 从文件名提取的数字序号
  - size_bytes: int | None # 文件大小（可选）
```

理由：现有 `ForEachState` 使用字符串路径作为键，但文本加载节点需要文件名用于日志、排序和展示。`index` 字段复用 `_num_from_filename` 逻辑。

## Sort Strategies

排序 MUST 支持三种模式（参数 `sort_method`）：

| Mode | Algorithm | Example |
|------|-----------|---------|
| `"numeric"` | 提取文件名中最后一段数字按数值排序 | file_2.txt, file_10.txt, file_100.txt |
| `"natural"` | 自然排序（数字部分按数值比较） | file_2.txt, file_10.txt, file_100.txt |
| `"alphabetical"` | 标准字符串排序 | file_10.txt, file_100.txt, file_2.txt |

默认 SHOULD 为 `"natural"`。MUST NOT 引入第三方依赖（如 natsort）。

## Encoding Data Flow

```
用户 encoding 参数 (STRING, default="utf-8")
  → 对每个 FileEntry:
    → open(filepath, "r", encoding=encoding)
    → UnicodeDecodeError → 根据 on_encoding_error 参数处理 ("skip"|"replace"|"fail")
    → 成功: content = f.read()
```

encoding 默认 MUST 为 `"utf-8"`，错误处理默认 SHOULD 为 `"replace"`。

## Memory Strategy

- 文件扫描阶段只收集路径，文本读取延迟到 FUNCTION 执行时
- 文件数超过 max_files（默认 100）MUST 截断并警告
- 单文件超过 50MB MUST 跳过或警告（根据 on_large_file 参数）
- 加载完成后 SHOULD 调用 gc_comfyui()
