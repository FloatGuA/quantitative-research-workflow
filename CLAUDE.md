# quantitative-research-workflow — 开发说明

## 你的角色
你是这个项目的迭代维护者。工厂已完成初始构建，你负责后续所有修复和功能扩展。
**不要直接修改代码**——按照下方"迭代工作方式"执行。

---

## 项目简介
对恒生指数（HSI）市场数据与社交媒体投票情绪数据进行全流程量化研究，检验情绪信号是否对市场收益具有预测力，并构建可回测的交易策略，最终产出适合量化实习评估的 Jupyter Notebook 报告。

---

## 技术栈
- **语言**：Python 3.10+
- **核心库**：`pandas`, `numpy`, `matplotlib`, `seaborn`
- **统计**：`scipy.stats`（t-test、Spearman 相关）
- **数据读取**：`openpyxl`（读取 xlsx）
- **报告生成**：`nbformat`（程序化创建 Jupyter Notebook）
- **输出格式**：Jupyter Notebook（`.ipynb`），所有图表内嵌

---

## 启动方式

### 前提条件
将 `HSI.xlsx` 放入 `code/` 目录（数据文件不在 git 中）。

### 生成研究报告
```bash
cd code
python create_research_report.py
# 生成 research_report.ipynb

# 运行 Notebook（需要 Jupyter）
jupyter notebook research_report.ipynb

# 或直接执行导出 HTML
jupyter nbconvert --to notebook --execute research_report.ipynb --output research_report_executed.ipynb
```

### 单独运行各分析模块（调试用）
```bash
cd code
python task_001_data_loading.py      # 生成 hsi_clean.csv
python task_002_feature_engineering.py  # 生成 hsi_features.csv
python task_003_eda.py               # 生成 fig_0*.png
python task_004_signal_analysis.py   # IC/ICIR/Decay 分析
python task_005_insights.py          # Insight 文字总结
python task_006_strategy_design.py   # 策略信号定义
python task_007_backtest.py          # 回测引擎
python task_008_robustness.py        # 稳健性检验
```

---

## 目录结构

```
code/
├── research_report.ipynb        # ★ 主输出：完整研究报告 Notebook
├── create_research_report.py    # 程序化生成 Notebook 的脚本
├── task_001_data_loading.py     # 数据加载与清洗（生成 hsi_clean.csv）
├── task_002_feature_engineering.py  # 收益率 + 情绪特征（生成 hsi_features.csv）
├── task_003_eda.py              # EDA 可视化（7张图）
├── task_004_signal_analysis.py  # IC/ICIR/Signal Decay
├── task_005_insights.py         # 信号 Insight 总结（动态生成文字）
├── task_006_strategy_design.py  # 三种策略信号定义
├── task_007_backtest.py         # 矢量化回测引擎 + 绩效指标
├── task_008_robustness.py       # 稳健性检验（敏感性/去极值/滚动Sharpe）
├── HSI.xlsx                     # [用户提供] 输入数据
├── hsi_clean.csv                # [自动生成] 清洗后数据
└── hsi_features.csv             # [自动生成] 特征工程数据
```

---

## 当前状态

### 任务完成情况

| Task | 名称 | Codex | 审查结论 |
|------|------|-------|----------|
| 001 | 数据加载与清洗 | ✅ Done | Pass |
| 002 | 收益率与特征工程 | ✅ Done | Pass |
| 003 | 探索性数据分析（EDA） | ✅ Done | Pass |
| 004 | 信号分析（IC/ICIR/Decay） | ✅ Done | Pass |
| 005 | Insight 总结 | ✅ Done | Pass with Warnings |
| 006 | 策略设计 | ✅ Done | Pass |
| 007 | 回测引擎 | ✅ Done | Pass |
| 008 | 稳健性检验 | ✅ Done | Pass with Warnings |
| 009 | 最终报告整合 | ✅ Done | Pass with Warnings |

### Must Fix（必须修复）
当前无阻塞性问题。

### Should Fix（建议修复）

1. **Task 005/008 — 模块导入脆弱性**：
   `task_005_insights.py` 和 `task_008_robustness.py` 中的 `from task_00N import ...` 依赖当前目录，在 Jupyter Notebook 中直接运行时可能失败。
   **修复方案**：将依赖函数内联，或统一放到 `utils.py` 模块中。

2. **Task 006 — 前视偏差风险（轻微）**：
   Strategy C 的 `vote_imbalance` 中位数在全样本上计算，严格来说存在轻微的前视偏差。
   **修复方案**：改用 expanding median（`df['vote_imbalance'].expanding().median()`）。

3. **Task 007/008 — 指标序列化**：
   Task 007 的 `calculate_metrics()` 返回已格式化的字符串（如 `"12.34%"`），Task 008 需要反序列化才能做数值比较。
   **修复方案**：`calculate_metrics()` 返回原始 float 值，格式化在展示层处理。

4. **Task 009 — Notebook cell 顺序硬编码**：
   `create_research_report.py` 中 `cells[:16] + cells[27:] + cells[16:27]` 使用硬编码索引，cell 数量变化时会静默失效。
   **修复方案**：改用命名标记（section headers）来定位和排序 cells。

---

## 下一步迭代建议

1. **优先**：修复 Should Fix 第 1 项（task_005/008 导入问题），使 Notebook 可以无依赖运行
2. **优先**：验证 `research_report.ipynb` 端到端可执行（`jupyter nbconvert --execute`）
3. **中期**：添加 `requirements.txt`，锁定依赖版本
4. **中期**：添加数据缺失时的友好错误提示（`HSI.xlsx` 不存在时报清晰错误）
5. **可选**：将重复使用的函数（回测引擎、绩效指标）抽取到 `utils.py`

---

## 迭代工作方式
每次迭代（修复或新功能）都按以下顺序执行，不跳步：

1. **分析需求** — 读 review.md 的 Must Fix / 用户提出的新需求，理解要做什么
2. **必要时更新 architecture.md** — 判断影响范围
3. **写 tasks/task_00N.md** — 序号续接（当前最后一个是 task_009），同时复制到 `logs/task_00N/prompt.md` 留痕
4. **调 codex**：
   ```bash
   python C:/Coding/AI-development-workflow/codex_runner.py \
     --prompt-file tasks/task_00N.md \
     --dir code \
     --title "Task 00N - <描述>"
   ```
5. **触发 report-writer skill** → `logs/task_00N/report.md`
6. **触发 reviewer skill** → `logs/task_00N/review.md`
7. **验收**，更新 `logs/final/progress.md`
8. **会话结束时触发 work-logger skill**，日志写入该项目目录的 `worklog.md`

---

## 工厂产物路径

- 架构设计：`architecture.md`
- 任务定义：`tasks/task_001.md` ... `tasks/task_009.md`
- 实现报告：`logs/task_00N/report.md`
- 审查报告：`logs/task_00N/review.md`
- 进度汇总：`logs/final/progress.md`
- Codex 日志：`logs/task_00N/codex.log`

<!-- FACTORY:DONE -->
