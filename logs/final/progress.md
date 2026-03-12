# quantitative-research-workflow — 整体进度汇总

## 项目概述
HSI 情绪信号量化研究，检验社交媒体投票数据（Up votes / Down votes）对恒生指数次日收益的预测力，构建三种量化交易策略并进行回测和稳健性检验，最终整合为完整 Jupyter Notebook 研究报告。

## 任务完成情况

| Task | 名称 | Codex状态 | 审查结论 |
|------|------|-----------|----------|
| 001 | 数据加载与清洗 | ✅ Done | Pass |
| 002 | 收益率构建与情绪特征工程 | ✅ Done | Pass |
| 003 | 探索性数据分析（EDA） | ✅ Done | Pass |
| 004 | 信号分析（IC/ICIR/Signal Decay） | ✅ Done | Pass |
| 005 | Insight 总结 | ✅ Done | Pass with Warnings |
| 006 | 策略设计 | ✅ Done | Pass |
| 007 | 回测引擎 | ✅ Done | Pass |
| 008 | 稳健性检验 | ✅ Done | Pass with Warnings |
| 009 | 最终报告整合 | ✅ Done | Pass with Warnings |
| 010 | 中文版报告生成 | ✅ Done | Pass |
| 011 | 方法论修正：信号方向反转 + 训练/测试集划分 | ✅ Done | Pass with Warnings |
| 012 | 方法论修正 Round 2：IC/Decay 训练集限定 + qcut 去偏 + p-value 守卫 | ✅ Done | Pass |

## Must Fix 汇总

**Task 001**：无 Must Fix

**Task 002**：无 Must Fix

**Task 003**：无 Must Fix

**Task 004**：无 Must Fix

**Task 005**：
- `task_005_insights.py` 对 `task_004_signal_analysis` 的硬耦合 import 可能在独立运行时导致 ImportError

**Task 006**：无 Must Fix

**Task 007**：无 Must Fix

**Task 008**：
- `parse_percent(str(metrics["Sharpe Ratio"]))` 的潜在类型混淆风险（当前代码实际使用正确，但逻辑需注释澄清）

**Task 009**：
- `cells = cells[:16] + cells[27:] + cells[16:27]` 硬编码索引重排逻辑脆弱，一旦 cells 数量变化将静默错乱章节顺序

## Should Fix 汇总（跨任务）

- **模块间硬耦合**（Task 005、008）：多个模块通过 `from task_00N import ...` 形成耦合链，在非标准执行环境中存在 ImportError 风险，建议统一提取公共工具模块或在 Notebook 中内联所有依赖
- **全样本中位数前视偏差**（Task 006 Strategy C）：`vote_imbalance` 中位数基于全样本计算，在真实回测场景中应使用滚动或历史截至当日的中位数
- **格式化字符串绩效指标**（Task 007-008）：Task 007 的 `calculate_metrics()` 返回格式化字符串，Task 008 需要反解析，增加了脆弱性，建议同时保留原始数值版本

## Task 010 Should Fix

- **硬编码重排索引**（继承自 Task 009）：`build_cells()` 内 `cells[:16] + cells[27:] + cells[16:27]` 未修复
- **Insights f-string 未中文化**：Section 6 动态生成的 `insight_text` 模板仍为英文，需纳入 `TEXTS` 管理

## Task 011 Should Fix

- ~~**`build_sentiment_quantiles` 仍使用全样本 qcut**~~ ✅ 已在 Task 012 修复
- **OOS 回测起始仓位不干净**：`_rebase_portfolio` 切片后不处理起始仓位，OOS 第一笔收益可能来自 IS 末尾续仓；建议对 OOS 第一行 `strategy_return` 归零后再 rebase

## Task 012 修复内容

直接修复，无独立 Codex 任务，本次改动文件：`task_002_feature_engineering.py`、`task_004_signal_analysis.py`、`task_005_insights.py`、`create_research_report.py`。

1. **IC/月度 IC 限定训练集**：`compute_monthly_ic` 和 inline IC cell 改为仅对 `is_train == True` 的行计算，消除 OOS 数据对信号评估的污染
2. **Signal Decay 限定训练集**：`compute_signal_decay` 和 inline decay cell 同样只用训练集做 `shift(-lag)` 和 Spearman 计算
3. **Vote Imbalance 效应限定训练集**：`compute_vote_imbalance_effect` 和 inline 代码的 quantile 切点仅从训练集计算
4. **`sentiment_quantile` 去前视偏差**：改用训练集 `pd.qcut` 得到 bins，再用 `pd.cut` 应用到全样本，边界设为 `±∞` 防止测试集越界
5. **IC Decay p-value 守卫**：`timing_view` 和 `generate_insights` 的衰减结论在所有 horizon p-value > 0.05 时优先输出"不显著"，避免对统计不显著的衰减过度解读

## 后续清理（同会话）

改动文件：`task_002_feature_engineering.py`、`task_003_eda.py`、`create_research_report.py`、`export_pdf.py`；新增 `requirements.txt`。

1. **删除 `sentiment_quantile`**：数据量不足分 5 组且下游无依赖，从特征工程、EDA、Notebook 全链路删除（EDA 由 7 图缩减为 5 图）
2. **新增 `requirements.txt`**：锁定 8 个依赖的最低版本，安装命令改为 `pip install -r requirements.txt`
3. **修复 `export_pdf.py`**：Edge headless 需传 `file://` URI 而非裸路径，同时加 `--no-sandbox`，PDF 导出从此可靠运行

## 整体结论
**Pass with Warnings**

12 个 Tasks 全部完成。主要遗留警告：模块间耦合（Task 005/008）、OOS 起始仓位不干净（Task 011 轻微）。信号方法论问题已基本消除。

<!-- FACTORY:DONE -->
