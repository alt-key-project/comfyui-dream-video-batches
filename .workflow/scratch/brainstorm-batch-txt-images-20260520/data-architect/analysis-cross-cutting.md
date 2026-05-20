# Data Architect — Cross-Cutting Concerns

## ForEachState Schema Extension

Proposed向后兼容扩展：

```json
{
  "/path/to/file.txt": false,
  "/path/to/another.txt": {"done": true, "encoding": "utf-8", "size": 4096}
}
```

读取逻辑：
- 值为 `bool` → 视为 `{"done": <bool>}`（兼容旧格式）
- 值为 `dict` → 读取 `done` 字段

写入统一使用新格式。保证与已有 foreach JSON 文件的向后兼容。

## FileScanner Abstraction

MUST 设计类型无关的 FileScanner：

```
FileScanner:
  - scan(directory, pattern, sort_method) → List[FileEntry]
  - filter_by_endings(entries, endings) → List[FileEntry]
```

- 图像 endings: `('.jpeg', '.jpg', '.png', '.tiff', '.gif', '.bmp', '.webp')`
- 文本 endings: `('.txt', '.md', '.json', '.csv', '.yaml', '.yml')`
- endings=None: 不过滤

现有 `shared.py:list_files_in_directory` SHOULD 重构为调用 FileScanner。

## Metadata Exposure

文件元数据 MAY 通过可选 STRING 输出端口以 JSON 格式暴露：

```json
[{"filename": "prompt_001.txt", "size": 1024, "encoding": "utf-8"}]
```

## Config Persistence

文本加载默认参数 MAY 通过 DVB_Config 体系持久化：
- `text_loader.default_encoding`
- `text_loader.default_separator`
- `text_loader.max_files`
