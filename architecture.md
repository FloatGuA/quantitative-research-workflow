# Quantitative Research Workflow — Architecture

## 项目概述

对恒生指数（HSI）市场数据与社交媒体情绪投票数据进行全流程量化研究，检验情绪信号是否对市场收益具有预测力，并构建可回测的交易策略。最终输出为适合量化实习评估的 Jupyter Notebook 报告。

---

## 输出文件结构

```
code/
├── research_report.ipynb      # 主输出：完整研究报告 Notebook
├── HSI.xlsx                   # 输入数据（需用户提供，放于 code/ 目录）
└── requirements.txt           # Python 依赖列表
```

---

## Notebook 架构（单文件策略）

整个研究以**单个 Jupyter Notebook**实现，9 个 Task 对应 9 个章节，全部内嵌图表，无外部依赖文件。

### 章节结构

| 章节 | Task | 核心内容 |
|------|------|----------|
| 1. Introduction | — | 研究背景、数据说明、假设 |
| 2. Data Overview | Task 1 | 数据加载、清洗、统计摘要 |
| 3. Feature Engineering | Task 2 | 收益率构建、情绪特征计算 |
| 4. Exploratory Analysis | Task 3 | EDA 可视化（7 张核心图） |
| 5. Signal Analysis | Task 4 | IC 时序、ICIR、Signal Decay |
| 6. Insights | Task 5 | 结构化文字总结 |
| 7. Strategy Design | Task 6 | 三种策略定义与经济直觉 |
| 8. Backtest Results | Task 7 | 回测引擎、绩效指标、可视化 |
| 9. Robustness Checks | Task 8 | 敏感性分析、滚动 Sharpe |
| 10. Conclusion | Task 9 | 最终整合与结论 |

---

## 数据流

```
HSI.xlsx
    ↓ Task 1: 加载 + 清洗 + forward fill
    ↓ Task 2: 收益率 + 情绪特征工程
    ↓ Task 3: EDA 可视化
    ↓ Task 4: IC / ICIR / Signal Decay
    ↓ Task 5: Insight 文字总结
    ↓ Task 6: 策略定义
    ↓ Task 7: 回测引擎 + 绩效指标
    ↓ Task 8: 稳健性检验
    ↓ Task 9: 整合所有章节 → research_report.ipynb
```

---

## 关键设计决策

### 1. 防未来信息泄漏
- forward fill 只向前填充（`method='ffill'`），不用 backward fill
- 情绪信号使用 `shift(1)` 对齐到下一个交易日收益
- next-day open return：`(open_{t+1} - open_t) / open_t`

### 2. 任务拆分策略
- Task 1-8 各自独立生成 Notebook cells（Python 脚本形式）
- Task 9 将所有 cells 整合为最终 `research_report.ipynb`
- 每个 Task 的实现文件：`task_0N_impl.py`（辅助脚本，最终合入 Notebook）

### 3. 回测引擎设计
- 矢量化回测（pandas-based），无需 backtrader 等重型框架
- 手续费参数化：`fee_rate=0.001`（单边 0.1%）
- 基准：买入持有 HSI（close-to-close return 累积）

### 4. 可视化规范
- 所有图表使用 `matplotlib` + `seaborn`，`plt.show()` 内嵌于 Notebook
- 配色：情绪正面用 green，负面用 red，中性用 gray
- 图表标题使用英文（量化报告国际化惯例）

### 5. 情绪特征
- `sentiment_score = Up votes - Down votes`（主信号，范围约 -1 到 1）
- `vote_imbalance = |Up votes - Down votes|`（信号强度过滤器）
- 极值标记：top/bottom 20% 分位数布尔标记
- 滞后信号：lag1/2/3 用于 Signal Decay 分析

---

## 技术栈

- **Python 3.10+**
- `pandas` — 数据处理、时序操作
- `numpy` — 数值计算
- `matplotlib` + `seaborn` — 可视化
- `scipy.stats` — Spearman 相关、t-test
- `jupyter` — Notebook 环境
- `openpyxl` — 读取 xlsx 文件

---

## 实现顺序

1. Task 1：数据加载与清洗（基础，所有后续依赖）
2. Task 2：特征工程（依赖 Task 1）
3. Task 3：EDA（依赖 Task 2）
4. Task 4：信号分析（依赖 Task 2）
5. Task 5：Insight 总结（依赖 Task 4）
6. Task 6：策略设计（依赖 Task 2）
7. Task 7：回测引擎（依赖 Task 6）
8. Task 8：稳健性检验（依赖 Task 7）
9. Task 9：最终整合（依赖所有 Task）

<!-- FACTORY:DONE -->
