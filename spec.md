# Quantitative Research Workflow — HSI Sentiment Alpha Study

## 项目概述

对恒生指数（HSI）市场数据与社交媒体投票情绪数据进行全流程量化研究，检验情绪信号是否对市场收益具有预测力，并构建可回测的交易策略。最终产出适合量化交易实习评估的专业研究报告（Jupyter Notebook）。

---

## 数据说明

- **文件**：`HSI.xlsx`，位于项目根目录
- **时间范围**：2022-02-24 至 2025-03-12，共 747 个交易日
- **列结构**：
  - `Date`：交易日期
  - `Open`, `High`, `Low`, `Close`：价格数据
  - `Up votes`, `Down votes`：当日社交媒体情绪投票比例（0~1 之间的小数，非原始票数）
- **数据质量问题**：
  - 195 条记录缺失情绪数据（约 26%），使用 **forward fill** 填充
  - 部分行 `Up votes + Down votes ≠ 1`，需检测并记录为数据异常，保留但标注

---

## 功能需求

### Task 1 — 数据加载与清洗
- 加载 `HSI.xlsx`，解析日期列，按时间排序
- 检测缺失值、重复行、数据类型异常
- 检测 `Up votes + Down votes ≠ 1` 的异常行，记录数量，保留数据但标注
- 对情绪列使用 forward fill 填充缺失值（不使用 backward fill，避免未来信息泄漏）
- 输出基础统计 summary（均值、标准差、分位数等）

### Task 2 — 收益率构建与情绪特征工程
- **主要收益率**：next-day open return：`return_t = (open_{t+1} - open_t) / open_t`
- **辅助收益率**：close-to-close return，用于对比
- **情绪特征**：
  - `sentiment_score = Up votes - Down votes`（范围约 -1 到 1）
  - `vote_imbalance = |Up votes - Down votes|`（情绪强度）
  - `extreme_bull`：sentiment_score 处于 top 20% 的布尔标记
  - `extreme_bear`：sentiment_score 处于 bottom 20% 的布尔标记
  - 滞后信号：`sentiment_lag1`, `sentiment_lag2`, `sentiment_lag3`
- 每个特征附说明文字解释经济含义

### Task 3 — 探索性数据分析（EDA）
可视化清单（全部内嵌于 Notebook）：
- 价格时序图（Close）
- 情绪时序图叠加价格（双轴）
- 情绪分布直方图 + KDE
- 情绪 vs 未来收益散点图（含趋势线）
- 分位数平均收益柱状图（5 组）
- **Cumulative average return by sentiment quantile**（核心图，5 条曲线）
- 特征相关性热力图

### Task 4 — 信号分析
- **IC 时序图**：每月计算 `sentiment_score` 与 `return_t+1` 的 Spearman 相关系数，绘制时序
- **ICIR**：`mean(IC) / std(IC)`，作为信号质量的关键指标
- **Signal Decay Test**：分别计算 sentiment_t 对 return_t+1、return_t+2、return_t+3 的 IC，绘制 decay 曲线，判断 alpha 是否为短期信号
- 统计显著性检验（t-test）

### Task 5 — Insight 总结
基于 Task 4 输出，以结构化文字总结：
- 情绪信号是否具有统计预测力
- 信号的时效性（短期 / 中期）
- 投票强度对信号质量的影响
- 信号在不同市场状态下的稳定性

### Task 6 — 策略设计
三种策略，每种含经济直觉说明：
- **Strategy A — Long-Short Portfolio（主策略）**：每日 long top 20% sentiment，short bottom 20% sentiment（行业标准信号检验方式）
- **Strategy B — Threshold Strategy**：`sentiment_score > 0.1` → long；`< -0.1` → short；否则空仓
- **Strategy C — Volume Filter Strategy**：仅在 `vote_imbalance` 高于中位数时执行 Strategy B 的信号

### Task 7 — 回测引擎
- 对三种策略分别运行回测
- **两个版本**：无手续费 vs 有手续费（单边 0.1%，每次换仓触发）
- 计算指标：
  - 累计收益（Cumulative Return）
  - 年化收益（Annualized Return）
  - Sharpe Ratio
  - 最大回撤（Max Drawdown）
  - 胜率（Win Rate）
  - 年化波动率
- 基准对比：买入持有 HSI
- 可视化：累计收益曲线、回撤曲线、月度收益热力图、收益分布直方图

### Task 8 — 稳健性检验
- 不同阈值敏感性分析（Strategy B）
- 滞后信号检验（lag 1/2/3）
- 去极值后重跑
- 滚动 Sharpe（12 个月窗口）
- 讨论过拟合风险

### Task 9 — 最终报告整合
将所有分析整合为完整 Jupyter Notebook，结构如下：
1. Introduction
2. Data Overview
3. Feature Engineering
4. Exploratory Analysis
5. Signal Analysis（IC / Decay）
6. Insights
7. Strategy Design
8. Backtest Results（含手续费对比）
9. Robustness Checks
10. Strategy Evaluation
11. Conclusion

每章含文字说明 + 图表，适合作为量化实习评估报告提交。

---

## 技术栈

- **语言**：Python 3.10+
- **核心库**：`pandas`, `numpy`, `matplotlib`, `seaborn`
- **统计**：`scipy.stats`（t-test、Spearman 相关）
- **输出格式**：Jupyter Notebook（`.ipynb`），所有图表内嵌

---

## 约束条件

- 不调用任何外部 API，不使用实时数据
- 不引入机器学习模型（保持纯统计 / 规则策略）
- 所有图表必须内嵌于 Notebook，不依赖外部文件
- 严格避免未来信息泄漏（forward fill 只向前，信号使用 `shift(1)` 对齐）
- 回测不加入滑点，手续费为可配置参数（默认单边 0.1%）

---

## 输入 / 输出

- **输入**：`HSI.xlsx`（项目根目录）
- **输出**：`research_report.ipynb`（含所有分析、图表、结论）

---

## 验收标准

- [ ] 数据清洗步骤可复现，forward fill 逻辑正确（无未来信息泄漏）
- [ ] 所有情绪特征含经济含义说明
- [ ] EDA 包含 cumulative average return by sentiment quantile 图
- [ ] IC 时序图、ICIR 数值、Signal Decay 曲线均有输出
- [ ] 三种策略均有完整回测，手续费版和无手续费版均有对比
- [ ] 最终 Notebook 章节结构完整，适合作为实习报告提交
