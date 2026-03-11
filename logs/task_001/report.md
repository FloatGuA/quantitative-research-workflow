# Task 001 — 数据加载与清洗 实现报告

## 实现概述
实现了完整的 HSI.xlsx 数据加载与清洗流水线，通过四个独立函数封装各步骤，最终输出清洗后的 `hsi_clean.csv`。

## 主要实现内容
- `load_data()`：使用 `pd.read_excel` 加载 HSI.xlsx，解析 Date 列为 datetime，按日期升序排序
- `inspect_data()`：打印数据形状、列类型、缺失值、重复行数量，并计算 `vote_sum` 和 `vote_anomaly` 标注异常行（允许 1e-6 误差）
- `clean_data()`：对 `Up votes` 和 `Down votes` 使用 `.ffill()` 前向填充，打印填充前后的缺失值数量
- `summarize_data()`：对 OHLC 和情绪列调用 `.describe()` 输出完整统计摘要
- `save_data()`：将清洗结果保存为 `hsi_clean.csv`

## 关键代码逻辑
数据检测中，通过 `(df["vote_sum"] - 1).abs() > 1e-6` 标注投票总和异常行，异常行被保留而非删除，保留 `vote_anomaly` 列供后续使用。清洗仅使用 `ffill`（前向填充），严格避免 `bfill`（后向填充）防止未来信息泄漏。

## 验收标准完成情况
- [x] 正确加载 HSI.xlsx，排序后按日期升序 — 已完成
- [x] 正确检测缺失值和重复行 — 已完成（inspect_data 函数输出）
- [x] forward fill 正确执行，使用 `.ffill()`，无 backward fill — 已完成
- [x] 异常行被标注（vote_anomaly 列），不删除 — 已完成
- [x] 统计摘要输出完整（OHLC + 情绪列的 describe）— 已完成
- [ ] 验证 195 条情绪缺失记录 — 代码正确执行检测逻辑，实际数量依赖数据文件，未能静态验证

## 输出文件
- `code/task_001_data_loading.py` — 数据加载与清洗模块，含 `main()` 入口

<!-- FACTORY:DONE -->
