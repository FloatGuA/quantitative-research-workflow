# HSI Sentiment Alpha Study

对恒生指数（HSI）市场数据与社交媒体投票情绪数据进行全流程量化研究，检验情绪信号是否对市场收益具有预测力，并构建可回测的交易策略。最终产出适合量化实习评估的 Jupyter Notebook 报告。

---

## 快速开始

### 前提条件

1. Python 3.10+
2. 将数据文件放入 `code/` 目录（格式要求见下方"使用其他数据"章节）
3. 安装依赖：

```bash
pip install pandas numpy matplotlib seaborn scipy openpyxl nbformat nbconvert nbclient
```

### 一键生成完整报告（推荐）

```bash
cd code
python run.py
```

`run.py` 自动完成全部步骤：检测数据文件 → 生成 Notebook → 执行 → 导出 HTML → 导出 PDF。
所有输出写入 `code/output/`，以数据文件名为前缀命名。

**可选参数：**

```bash
python run.py --data-name SPX        # 指定数据文件名（默认自动检测）
python run.py --output-dir results   # 自定义输出目录（默认 output/）
python run.py --skip-pdf             # 跳过 PDF 导出
```

### 分步执行

```bash
cd code

# 仅生成 Notebook（不执行）
python create_research_report.py
# 支持参数：--data-name SPX --output-dir output

# 用浏览器打开查看
python -m jupyter notebook output/HSI_research_report_executed.ipynb
```

---

## 项目结构

```
quantitative-research-workflow/
├── README.md
├── spec.md                      # 需求规格说明
├── architecture.md              # 架构设计文档
├── CLAUDE.md                    # 迭代开发说明
├── HSI.xlsx                     # [用户提供] 原始数据（放根目录或 code/ 均可）
│
├── code/
│   ├── run.py                       # ★ 一键运行脚本（推荐入口）
│   ├── create_research_report.py    # 程序化生成 Notebook 的脚本
│   │
│   ├── output/                      # [自动生成] 所有输出文件
│   │   ├── HSI_research_report.ipynb
│   │   ├── HSI_research_report_zh.ipynb
│   │   ├── HSI_research_report_executed.ipynb
│   │   ├── HSI_research_report_zh_executed.ipynb
│   │   ├── HSI_research_report.html
│   │   ├── HSI_research_report_zh.html
│   │   ├── HSI_research_report.pdf
│   │   └── HSI_research_report_zh.pdf
│   │
│   ├── task_001_data_loading.py     # 数据加载与清洗
│   ├── task_002_feature_engineering.py  # 收益率 + 情绪特征
│   ├── task_003_eda.py              # EDA 可视化（7 张图）
│   ├── task_004_signal_analysis.py  # IC / ICIR / Signal Decay
│   ├── task_005_insights.py         # Insight 文字总结
│   ├── task_006_strategy_design.py  # 三种策略定义
│   ├── task_007_backtest.py         # 矢量化回测引擎
│   └── task_008_robustness.py       # 稳健性检验
│
├── tasks/                       # 各 Task 的任务定义文档
├── logs/                        # Codex 实现报告 + 审查报告
│   └── final/progress.md        # 整体进度汇总
└── worklog.md                   # 迭代工作日志
```

---

## 使用其他数据

本项目可适配任何市场的价格 + 情绪投票数据，只需将数据文件准备为以下格式并命名为 `HSI.xlsx`，放入 `code/` 目录即可。

### 必需列

| 列名 | 类型 | 说明 |
|------|------|------|
| `Date` | 日期（YYYY-MM-DD 或可被 pandas 解析的格式） | 交易日期，不可重复 |
| `Open` | 数值 | 当日开盘价 |
| `High` | 数值 | 当日最高价 |
| `Low` | 数值 | 当日最低价 |
| `Close` | 数值 | 当日收盘价 |
| `Up votes` | 数值（0~1） | 当日看多情绪比例 |
| `Down votes` | 数值（0~1） | 当日看空情绪比例 |

### 格式要求

- 文件格式：`.xlsx`（Excel），第一行为列名
- 数据按交易日排列，允许乱序（脚本会自动排序）
- `Up votes` 和 `Down votes` 应为 0 到 1 之间的小数（比例值，非原始票数）；两者之和约为 1，允许轻微偏差
- 情绪数据允许缺失，脚本会自动用前向填充（forward fill）处理
- 建议数据量 ≥ 200 个交易日，否则月度 IC 统计样本不足

### 注意

- 如果你的数据中情绪列名称不同（如 `bullish`/`bearish`），需在 `create_research_report.py` 开头修改对应的列名常量
- 价格单位不影响分析（收益率计算为相对变化）

---

## 数据说明

| 字段 | 说明 |
|------|------|
| `Date` | 交易日期 |
| `Open`, `High`, `Low`, `Close` | HSI 价格数据 |
| `Up votes` | 当日社交媒体看多投票比例（0~1） |
| `Down votes` | 当日社交媒体看空投票比例（0~1） |

- **时间范围**：2022-02-24 至 2025-03-12，约 747 个交易日
- **缺失处理**：约 26% 的记录缺失情绪数据，使用 forward fill 填充（无未来信息泄漏）

---

## 研究内容

### 情绪特征

| 特征 | 定义 | 经济含义 |
|------|------|----------|
| `sentiment_score` | Up votes − Down votes | 主信号，净多空情绪（−1 到 1） |
| `vote_imbalance` | \|Up votes − Down votes\| | 情绪强度，用于信号过滤 |
| `extreme_bull` | sentiment_score top 20% | 极度乐观标记 |
| `extreme_bear` | sentiment_score bottom 20% | 极度悲观标记 |
| `sentiment_lag1/2/3` | 滞后 1/2/3 日情绪 | Signal Decay 分析 |

### 三种交易策略

| 策略 | 逻辑 | 特点 |
|------|------|------|
| **Strategy A** — Long-Short | Long top 20% sentiment，Short bottom 20% | 行业标准 L/S 信号检验 |
| **Strategy B** — Threshold | sentiment > 0.1 → long；< −0.1 → short | 简单阈值规则 |
| **Strategy C** — Volume Filter | 仅在 vote_imbalance 高于中位数时执行 B | 情绪强度过滤 |

### 绩效指标

累计收益、年化收益、Sharpe Ratio、最大回撤、胜率、年化波动率；含手续费（单边 0.1%）与无手续费两个版本，基准为买入持有 HSI。

---

## 报告结构

最终 `research_report.ipynb` 共 11 章：

1. Introduction
2. Data Overview
3. Feature Engineering
4. Exploratory Analysis（7 张可视化）
5. Signal Analysis（IC 时序、ICIR、Signal Decay）
6. Insights
7. Strategy Design
8. Backtest Results
9. Robustness Checks
10. Strategy Evaluation
11. Conclusion

---

## 单模块调试

```bash
cd code
python task_001_data_loading.py      # → hsi_clean.csv
python task_002_feature_engineering.py  # → hsi_features.csv
python task_003_eda.py               # → fig_0*.png
python task_004_signal_analysis.py
python task_005_insights.py
python task_006_strategy_design.py
python task_007_backtest.py
python task_008_robustness.py
```

---

## 已知注意事项

- **Task 005/008 模块导入**：在 Notebook 中直接运行单个 cell 时，`from task_00N import ...` 可能因路径问题失败；建议通过 `nbconvert --execute` 整体执行
- **Strategy C 轻微前视偏差**：`vote_imbalance` 中位数基于全样本计算，严格回测场景建议改用 expanding median
- **绩效指标格式化**：Task 007 返回格式化字符串指标（如 `"12.34%"`），Task 008 内部有反解析逻辑

---

## 技术栈

| 库 | 用途 |
|----|------|
| `pandas` | 数据处理、时序操作 |
| `numpy` | 数值计算 |
| `matplotlib` + `seaborn` | 可视化 |
| `scipy.stats` | Spearman 相关、t-test |
| `openpyxl` | 读取 xlsx |
| `nbformat` + `nbconvert` + `nbclient` | 程序化生成 / 执行 Notebook |
