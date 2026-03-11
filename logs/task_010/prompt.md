# Task 010 — 中文版报告生成

## 目标
在现有英文报告生成脚本 `create_research_report.py` 的基础上，增加中文版报告生成能力，使脚本一次运行同时输出英文版 `research_report.ipynb` 和中文版 `research_report_zh.ipynb`。代码 cells 内容保持完全一致，仅 Markdown 描述性文字切换为中文。

## 工作目录
`code/`

## 依赖
- `create_research_report.py`（Task 009 产物）
- 无新增外部依赖

## 输出文件
- `research_report.ipynb` — 英文版（保持不变）
- `research_report_zh.ipynb` — 中文版（新增）

## 详细要求

### 双语文本管理
将所有 Markdown cell 的字符串提取到顶层 `TEXTS` 字典，结构如下：

```python
TEXTS = {
    "section_key": {
        "en": "English text...",
        "zh": "中文文本...",
    },
    ...
}
```

涵盖以下所有 Markdown 节点：
- 标题与执行摘要（`title`）
- Section 1–11 的章节说明（`intro`、`data_overview`、`feature_eng`、`signal_analysis`、`insights`、`strategy_design`、`backtest`、`robustness`、`evaluation`、`conclusion`）
- 图表说明文字（`fig1`–`fig7`）

### Cell 构建函数化
将原有的顶层 cells 构建逻辑封装为 `build_cells(lang: str) -> list`，接受 `"en"` 或 `"zh"` 参数，返回对应语言的 cells 列表。

### 同时生成两个 Notebook
脚本末尾遍历 `{"en": "research_report.ipynb", "zh": "research_report_zh.ipynb"}`，各调用一次 `build_cells(lang)` 并写入文件。

## 代码规范
- 代码 cells 内容完全相同，不做任何修改
- 中文文本应准确传达原英文含义，使用量化研究领域的标准中文术语
- 保持原有 cells 重排逻辑（`cells[:16] + cells[27:] + cells[16:27]`）不变

## 验收标准
- [ ] `research_report.ipynb` 内容与改动前保持一致（cells 数量相同）
- [ ] `research_report_zh.ipynb` 成功创建，cells 数量与英文版相同
- [ ] 中文版可通过 `jupyter nbconvert --execute` 无错误执行
- [ ] 中文版所有 Markdown cell 均为中文，代码 cell 无变化

<!-- FACTORY:DONE -->
