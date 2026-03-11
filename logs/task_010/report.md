# Task 010 — 中文版报告生成 实现报告

## 实现概述
对 `create_research_report.py` 进行重构，将所有 Markdown 文本提取到顶层 `TEXTS` 双语字典，将 cells 构建逻辑封装为 `build_cells(lang)` 函数，脚本末尾遍历两种语言一次性输出英文版和中文版两个 Notebook。

## 主要实现内容

### 1. `TEXTS` 双语字典
新增顶层 `TEXTS` 字典，包含 14 个 key（`title`、`intro`、`data_overview`、`feature_eng`、`fig1`–`fig7`、`signal_analysis`、`insights`、`strategy_design`、`backtest`、`robustness`、`evaluation`、`conclusion`），每个 key 下各有 `"en"` 和 `"zh"` 两个版本的文本。中文文本使用量化研究领域标准术语（IC、ICIR、Signal Decay、多空策略等）。

### 2. `build_cells(lang)` 函数
将原有顶层 cells 构建代码封装为函数，接受 `lang` 参数（`"en"` 或 `"zh"`），在函数开头用 `t = {k: v[lang] for k, v in TEXTS.items()}` 展开当前语言文本，所有 `md(...)` 调用改为 `md(t["key"])` 形式。代码 cells 完全不变。

### 3. 双文件输出
```python
outputs = {
    "en": "research_report.ipynb",
    "zh": "research_report_zh.ipynb",
}
for lang, filename in outputs.items():
    notebook = {"cells": build_cells(lang), **NOTEBOOK_META}
    Path(filename).write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
```

## 验收标准完成情况
- [x] `research_report.ipynb` 内容与改动前保持一致（40 cells）— 已完成
- [x] `research_report_zh.ipynb` 成功创建，40 cells，与英文版数量相同 — 已完成
- [x] 中文版可通过 `jupyter nbconvert --execute` 无错误执行 — 已验证（输出 1,941,961 bytes）
- [x] 中文版所有 Markdown cell 均为中文，代码 cell 无变化 — 已完成

## 输出文件
- `code/create_research_report.py` — 重构后的双语报告生成脚本
- `code/research_report.ipynb` — 英文版（内容不变）
- `code/research_report_zh.ipynb` — 中文版（新增）
- `code/research_report_zh_executed.ipynb` — 中文版执行结果（新增）

<!-- FACTORY:DONE -->
