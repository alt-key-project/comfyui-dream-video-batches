# F-003: Batch Text Load Node — Data Structure Analysis

## Output Port Strategy

ComfyUI 节点输出端口为静态声明。三种方案评估：

| Scheme | Description | Verdict |
|--------|-------------|---------|
| A: 单一聚合 STRING | 所有文件以分隔符连接为一个字符串 | **RECOMMENDED** |
| B: 固定 N 端口 | 预定义 text_1...text_N | Alternative |
| C: LIST 类型 | 使用 ComfyUI 原生 LIST | Not recommended |

**推荐方案 A**: 单一 STRING 输出 `("STRING",)` 命名为 `("texts",)`，默认分隔符 `"\n---FILE---\n"`。

理由：ComfyUI 生态中 STRING 下游消费最成熟。分隔符在 LLM prompt 中易于识别。

SHOULD 提供可选的第二个输出端口 `("INT",)` 命名为 `("count",)` 表示文件总数。

## max_files Parameter

- 默认值: 100
- 0 表示无限制（危险，不推荐）
- 超出时 MUST 截断并 print 警告

## FrameSet Isolation

Batch Text Load Node MUST NOT 返回 FrameSet 类型。文本加载与图像加载 MUST 保持独立节点类型。

未来如需文本-图像关联 SHOULD 通过 ComfyUI 工作流层面连接实现。
