import argparse
import json
from pathlib import Path
from textwrap import dedent


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": dedent(source).strip("\n"),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(source).strip("\n"),
    }


# ---------------------------------------------------------------------------
# Markdown text — English and Chinese versions
# ---------------------------------------------------------------------------

TEXTS = {
    "title": {
        "en": """
            # HSI Sentiment Alpha Study
            ## Quantitative Research Report

            **Author**: Your Name
            **Date**: 2025
            **Data**: Hang Seng Index (2022-2024), expected n=747 trading days

            ### Executive Summary
            This study investigates whether social media sentiment voting data (Up/Down votes)
            can predict next-day returns for the Hang Seng Index (HSI). We construct three
            trading strategies and evaluate their performance with and without transaction costs.

            **Key Findings**:
            - Full signal-quality statistics are computed in Section 5.
            - Strategy-level performance comparison is reported in Sections 8 and 10.
            - Transaction-cost impact is quantified directly in the backtest metrics table.
            """,
        "zh": """
            # 恒生指数情绪因子研究
            ## 量化研究报告

            **作者**：姓名
            **日期**：2025
            **数据**：恒生指数（2022–2024），预计 n=747 个交易日

            ### 执行摘要
            本研究探讨社交媒体情绪投票数据（看多/看空票数）是否能预测恒生指数次日收益。
            我们构建三种交易策略，分别在含手续费与不含手续费两种情景下评估其表现。

            **核心结论**：
            - 信号质量统计详见第 5 节。
            - 各策略绩效对比详见第 8 节和第 10 节。
            - 手续费影响已直接量化于回测指标表中。
            """,
    },
    "intro": {
        "en": """
            ## 1. Introduction

            This report evaluates whether daily social sentiment voting can serve as a short-horizon alpha signal for the Hang Seng Index.
            The central hypothesis is that net bullish sentiment on day `t` contains information about next-day index performance.

            The study uses three layers of analysis:
            1. Data validation and feature construction.
            2. Signal diagnostics including IC, ICIR, and signal decay.
            3. Strategy design, backtesting, and robustness checks.

            The objective is practical rather than purely descriptive: determine whether the sentiment signal is strong enough, stable enough, and tradeable enough to support a simple systematic strategy.
            """,
        "zh": """
            ## 1. 研究背景

            本报告评估日度社交媒体情绪投票能否作为恒生指数的短期 Alpha 信号。
            核心假设是：t 日的净看多情绪包含对次日指数表现有预测价值的信息。

            研究分三个层次展开：
            1. 数据验证与特征构建。
            2. 信号诊断，包括 IC、ICIR 及信号衰减分析。
            3. 策略设计、回测与稳健性检验。

            本研究目标侧重实用性：判断情绪信号的强度、稳定性和可交易性是否足以支持一套简单的系统化策略。
            """,
    },
    "data_overview": {
        "en": """
            ## 2. Data Overview

            The dataset contains daily HSI price observations together with two sentiment-voting fields: `Up votes` and `Down votes`.
            Initial validation focuses on chronological ordering, missing-value handling, duplicate detection, and whether the sentiment shares approximately sum to one.

            Rows where either `Up votes` or `Down votes` is missing are dropped to avoid introducing look-ahead bias from imputation.
            The descriptive statistics above provide a baseline view of price levels and the cross-section of sentiment inputs.
            """,
        "zh": """
            ## 2. 数据概览

            数据集包含恒生指数每日价格及两个情绪投票字段：`Up votes`（看多票数比例）和 `Down votes`（看空票数比例）。
            初步验证重点关注时间顺序、缺失值处理、重复行检测，以及情绪份额之和是否近似为 1。

            凡 `Up votes` 或 `Down votes` 任一为空的行，直接删除，避免通过填充引入前视偏差。
            上方描述统计提供了价格水平与情绪输入截面的基准视图。
            """,
    },
    "feature_eng": {
        "en": """
            ## 3. Feature Engineering

            The core predictive variable is `sentiment_score = Up votes - Down votes`, which measures the net daily direction of crowd sentiment.
            We also construct `vote_imbalance = |sentiment_score|` as a proxy for conviction or consensus.

            To test different economic interpretations, the notebook creates:
            - `return_open`: next-day open-to-open return, aligned with a signal known after day `t`.
            - `extreme_bull` and `extreme_bear`: tail-state indicators for sentiment extremes.
            - `sentiment_lag1` to `sentiment_lag3`: delayed signals for decay analysis.
            """,
        "zh": """
            ## 3. 特征工程

            核心预测变量为 `sentiment_score = Up votes - Down votes`，衡量市场情绪的净方向。
            同时构建 `vote_imbalance = |sentiment_score|` 作为情绪强度（共识程度）的代理指标。

            为检验不同经济含义，本报告构建以下特征：
            - `return_open`：次日开盘对开盘收益率，与 t 日已知信号对齐。
            - `extreme_bull` 和 `extreme_bear`：情绪极值的尾部状态标记。
            - `sentiment_lag1` 至 `sentiment_lag3`：滞后信号，用于衰减分析。
            """,
    },
    "fig1": {
        "en": """
            ### 4. Exploratory Analysis

            **Figure 1.** HSI closing price series across the sample period.
            """,
        "zh": """
            ### 4. 探索性数据分析

            **图 1.** 样本区间内恒生指数收盘价时序。
            """,
    },
    "fig2": {
        "en": "**Figure 2.** Price and sentiment score on dual axes to compare broad co-movement over time.",
        "zh": "**图 2.** 价格与情绪得分双轴图，展示两者随时间的联动关系。",
    },
    "fig3": {
        "en": "**Figure 3.** Distribution of the sentiment score to assess symmetry, skew, and concentration around neutral.",
        "zh": "**图 3.** 情绪得分分布图，用于评估其对称性、偏度及在中性附近的集中程度。",
    },
    "fig4": {
        "en": "**Figure 4.** Scatter plot of sentiment versus next-day return with a fitted linear trend.",
        "zh": "**图 4.** 情绪得分与次日收益率的散点图及线性趋势拟合。",
    },
    "fig5": {
        "en": "**Figure 5.** Spearman correlation heatmap across returns, sentiment, and lagged sentiment features.",
        "zh": "**图 5.** 收益率、情绪及滞后情绪特征之间的 Spearman 相关系数热力图。",
    },
    "signal_analysis": {
        "en": """
            ## 5. Signal Analysis

            The next step evaluates whether sentiment is useful as a predictive signal.
            The primary quality metric is Spearman information coefficient (IC) between `sentiment_score_t` and `return_open_t+1`.
            We also inspect the time-series stability of IC, the t-test against zero, and how signal strength decays as the forecast horizon extends beyond one day.
            """,
        "zh": """
            ## 5. 信号分析

            本节评估情绪是否具有预测信号价值。
            主要质量指标为 `sentiment_score_t` 与 `return_open_t+1` 之间的 Spearman 信息系数（IC）。
            同时考察 IC 时序的稳定性、对零的 t 检验，以及随预测期延长信号强度的衰减情况。
            """,
    },
    "insights": {
        "en": """
            ## 6. Insights

            This section turns the signal diagnostics into concise research conclusions.
            In addition to the aggregate IC and ICIR, it tests whether the signal is stronger on high-consensus days where vote imbalance is large.
            """,
        "zh": """
            ## 6. 研究洞察

            本节将信号诊断结果提炼为简明的研究结论。
            除整体 IC 和 ICIR 外，还检验在投票分歧较大（高共识）的交易日，信号是否具有更强的预测力。
            """,
    },
    "strategy_design": {
        "en": """
            ## 7. Strategy Design

            Three strategies are evaluated:

            - **Strategy A: Extreme Sentiment Long/Short**
              Long on top-20% sentiment days and short on bottom-20% sentiment days.

            - **Strategy B: Threshold Rule**
              Go long when sentiment is above `+0.1`, short when below `-0.1`, and stay flat otherwise.

            - **Strategy C: Threshold + Conviction Filter**
              Apply Strategy B only when `vote_imbalance` is at or above the train-sample median.

            All signals are formed using information available on day `t` and are mapped to next-day returns through the pre-aligned `return_open` series.
            """,
        "zh": """
            ## 7. 策略设计

            本研究评估三种策略：

            - **策略 A：极值情绪多空**
              在情绪处于前 20% 分位的交易日做多，后 20% 分位的交易日做空。

            - **策略 B：阈值规则**
              情绪得分高于 `+0.1` 时做多，低于 `-0.1` 时做空，否则空仓。

            - **策略 C：阈值 + 强度过滤**
              仅在 `vote_imbalance` 不低于训练集样本中位数时执行策略 B 的信号。

            所有信号均基于 t 日已知信息构建，并通过预对齐的 `return_open` 序列映射至次日收益。
            """,
    },
    "backtest": {
        "en": """
            ## 8. Backtest Results

            This section compares all strategy variants with and without transaction costs.
            The figures below focus on cumulative returns, drawdowns, monthly return seasonality, and return distributions.
            """,
        "zh": """
            ## 8. 回测结果

            本节对比所有策略在含手续费与不含手续费两种情景下的表现。
            下方图表聚焦于累计收益、回撤、月度收益季节性及收益分布。
            """,
    },
    "robustness": {
        "en": """
            ## 9. Robustness Checks

            Robustness analysis examines whether the strategy conclusions are sensitive to threshold selection, lag structure, and extreme-value handling.
            Rolling Sharpe is also reported to test whether performance is stable through time rather than concentrated in a single regime.
            """,
        "zh": """
            ## 9. 稳健性检验

            稳健性分析考察策略结论对阈值选择、滞后结构及极值处理的敏感性。
            同时报告滚动 Sharpe 比率，以检验策略表现是否随时间保持稳定，而非集中于单一市场状态。
            """,
    },
    "evaluation": {
        "en": """
            ## 10. Strategy Evaluation

            The table below is intended as the final side-by-side comparison of the three strategies after accounting for implementation realism.
            Strategy quality should be judged jointly on return, Sharpe ratio, drawdown, trade count, and fee sensitivity rather than on any single metric.
            """,
        "zh": """
            ## 10. 策略综合评估

            下表为考虑实际执行约束后三种策略的最终横向对比。
            策略质量应综合收益率、Sharpe 比率、最大回撤、交易次数和手续费敏感性进行评判，而非依赖单一指标。
            """,
    },
    "insight_dynamic": {
        "en": (
            'predictiveness = (\n'
            '    "moderate"\n'
            '    if abs(mean_ic) > 0.02 and ic_pvalue < 0.10\n'
            '    else "weak"\n'
            ')\n'
            'direction_note = (\n'
            '    "Note: IC < 0 — this is a **contrarian** signal. "\n'
            '    "Positive sentiment predicts negative returns; strategies should be inverted.\\n"\n'
            '    if mean_ic < 0 else ""\n'
            ')\n'
            'all_decay_insignificant = all(\n'
            '    row["p_value"] > 0.05\n'
            '    for _, row in decay_df.iterrows()\n'
            '    if not pd.isna(row["p_value"])\n'
            ')\n'
            'timing_view = (\n'
            '    "not statistically significant at any tested horizon"\n'
            '    if all_decay_insignificant\n'
            '    else (\n'
            '        "front-loaded"\n'
            '        if abs(lag_map.get("t+1", np.nan)) >= max(abs(v) for v in lag_map.values())\n'
            '        else "more persistent than a pure one-day signal"\n'
            '    )\n'
            ')\n'
            'imbalance_view = (\n'
            '    "helps"\n'
            '    if abs(high_ic) > abs(low_ic)\n'
            '    else "does not clearly improve"\n'
            ')\n\n'
            'insight_text = f"""\n'
            '## Signal Analysis Insights\n\n'
            '### Key Findings\n\n'
            "1. **Predictive power**: The signal appears **{predictiveness}**, with Mean IC = {mean_ic:.4f}, ICIR = {icir:.4f}, and t-test p-value = {ic_pvalue:.4f}.\n"
            '{direction_note}'
            "2. **Decay profile**: The signal is **{timing_view}**. IC(t+1) = {lag_map.get('t+1', np.nan):.4f}, IC(t+2) = {lag_map.get('t+2', np.nan):.4f}, IC(t+3) = {lag_map.get('t+3', np.nan):.4f}.\n"
            "3. **Consensus filter**: High vote-imbalance days {imbalance_view} signal quality. High-consensus IC = {high_ic:.4f}, low-consensus IC = {low_ic:.4f}, spread = {ic_spread:.4f}.\n"
            "4. **Stability**: {positive_ic_pct:.1%} of monthly IC observations are positive.\n\n"
            '### Trading Interpretation\n\n'
            '- Use the daily sentiment score as the base signal.\n'
            '- Statistical significance indicates a relationship exists; it does not by itself validate the original trade direction.\n'
            '- Emphasize short-horizon execution if the front-end IC is strongest.\n'
            '- Consider vote imbalance as a quality filter if it improves IC magnitude.\n'
            '"""'
        ),
        "zh": (
            'predictiveness = (\n'
            '    "中等"\n'
            '    if abs(mean_ic) > 0.02 and ic_pvalue < 0.10\n'
            '    else "弱"\n'
            ')\n'
            'direction_note = (\n'
            '    "提示：IC < 0，说明这是一个**反向**信号。"\n'
            '    "正情绪预测负收益，策略方向应取反。\\n"\n'
            '    if mean_ic < 0 else ""\n'
            ')\n'
            'all_decay_insignificant = all(\n'
            '    row["p_value"] > 0.05\n'
            '    for _, row in decay_df.iterrows()\n'
            '    if not pd.isna(row["p_value"])\n'
            ')\n'
            'timing_view = (\n'
            '    "任意测试期均不显著"\n'
            '    if all_decay_insignificant\n'
            '    else (\n'
            '        "短期集中"\n'
            '        if abs(lag_map.get("t+1", np.nan)) >= max(abs(v) for v in lag_map.values())\n'
            '        else "比纯单日信号更具持续性"\n'
            '    )\n'
            ')\n'
            'imbalance_view = (\n'
            '    "有助于提升"\n'
            '    if abs(high_ic) > abs(low_ic)\n'
            '    else "未显著改善"\n'
            ')\n\n'
            'insight_text = f"""\n'
            '## 信号分析洞察\n\n'
            '### 核心结论\n\n'
            "1. **预测力**：信号整体表现为**{predictiveness}**，Mean IC = {mean_ic:.4f}，ICIR = {icir:.4f}，t 检验 p 值 = {ic_pvalue:.4f}。\n"
            '{direction_note}'
            "2. **衰减特征**：信号呈**{timing_view}**态势。IC(t+1) = {lag_map.get('t+1', np.nan):.4f}，IC(t+2) = {lag_map.get('t+2', np.nan):.4f}，IC(t+3) = {lag_map.get('t+3', np.nan):.4f}。\n"
            "3. **共识过滤器**：高投票分歧日{imbalance_view}信号质量。高共识 IC = {high_ic:.4f}，低共识 IC = {low_ic:.4f}，差值 = {ic_spread:.4f}。\n"
            "4. **稳定性**：{positive_ic_pct:.1%} 的月度 IC 为正。\n\n"
            '### 交易含义\n\n'
            '- 以每日情绪得分作为基础信号。\n'
            '- 统计显著仅说明存在关系，并不自动代表原始交易方向正确。\n'
            '- 若短期 IC 最强，优先考虑短线执行。\n'
            '- 若投票分歧能提升 IC 强度，可作为质量过滤条件。\n'
            '"""'
        ),
    },
    "overfitting_md": {
        "en": (
            "'''\n"
            "## Overfitting Risk Discussion\n\n"
            "1. **Single split validation**: parameters are fit on the first 80% of observations and checked on the final 20%, but this is still only one time split.\n"
            "2. **Threshold selection**: the `+/-0.1` cutoff may contain data-mining bias.\n"
            "3. **Limited history**: the sample does not span a full set of market regimes.\n"
            "4. **Implementation simplification**: trades assume immediate execution with no slippage.\n"
            "5. **Recommended next step**: extend to rolling or expanding walk-forward validation on newer unseen data.\n"
            "'''"
        ),
        "zh": (
            "'''\n"
            "## 过拟合风险讨论\n\n"
            "1. **单次切分验证**：参数仅在前 80% 训练集上拟合，并在后 20% 测试集上验证，但这仍只是一次时序切分。\n"
            "2. **阈值选择偏差**：`+/-0.1` 阈值存在数据挖掘偏差风险。\n"
            "3. **历史数据不足**：样本未覆盖完整的市场周期。\n"
            "4. **执行假设简化**：回测假设以下一开盘价无滑点立即成交。\n"
            "5. **建议后续步骤**：在更新数据上继续做滚动或扩展窗口的 walk-forward 样本外测试。\n"
            "'''"
        ),
    },
    "conclusion": {
        "en": """
            ## 11. Conclusion

            ### Summary
            - Sentiment signal shows weak-to-moderate predictive power for next-day HSI returns, based on the IC and ICIR diagnostics reported above.
            - The best strategy should be selected from the evaluation table using fee-adjusted Sharpe as the primary metric.
            - Transaction costs materially affect realized performance and should be treated as part of the signal viability test.

            ### Limitations
            1. Short history, not tested across a full market cycle.
            2. Validation is based on a single 80/20 time split rather than a full walk-forward design.
            3. Assumes immediate execution at the next open with no slippage.

            ### Next Steps
            1. Extend to out-of-sample testing on new data.
            2. Combine sentiment with complementary alpha factors.
            3. Explore volatility targeting and more disciplined position sizing.
            """,
        "zh": """
            ## 11. 结论

            ### 总结
            - 基于上述 IC 和 ICIR 诊断，情绪信号对恒生指数次日收益具有弱至中等程度的预测力。
            - 最优策略应以含手续费的 Sharpe 比率为主要指标，从评估表中选取。
            - 手续费对实际绩效影响显著，应作为信号可行性检验的组成部分。

            ### 局限性
            1. 历史数据较短，未覆盖完整的市场周期。
            2. 当前验证仅基于单次 80/20 时序切分，而非完整的 walk-forward 设计。
            3. 假设在次日开盘立即以无滑点价格执行。

            ### 后续方向
            1. 在新数据上进行样本外测试。
            2. 将情绪信号与互补的 Alpha 因子相结合。
            3. 探索波动率目标化策略与更严格的仓位管理方法。
            """,
    },
}


# ---------------------------------------------------------------------------
# Cell builder
# ---------------------------------------------------------------------------

def build_cells(lang: str, data_name: str = "HSI") -> list:
    t = {k: v[lang] for k, v in TEXTS.items()}
    cells = []

    cells.extend(
        [
            md(t["title"]),
            code(
                """
                from pathlib import Path

                import warnings
                import numpy as np
                import pandas as pd
                import matplotlib.pyplot as plt
                import seaborn as sns
                from IPython.display import Markdown, display
                from scipy import stats
                from scipy.stats import mstats, ttest_1samp

                warnings.filterwarnings("ignore")

                plt.rcParams["figure.dpi"] = 120
                plt.rcParams["font.size"] = 11
                plt.rcParams["axes.grid"] = True
                plt.rcParams["grid.alpha"] = 0.3
                sns.set_style("whitegrid")

                print("Libraries loaded successfully")
                print(f"Pandas: {pd.__version__}, NumPy: {np.__version__}")
                """
            ),
            md(t["intro"]),
            code(
                """
                DATA_FILE = Path("%%DATA_NAME%%.xlsx")
                VOTE_TOLERANCE = 1e-6
                SUMMARY_COLUMNS = ["Open", "High", "Low", "Close", "Up votes", "Down votes"]

                if not DATA_FILE.exists():
                    raise FileNotFoundError(
                        f"Input file not found: {DATA_FILE.resolve()}. "
                        "Place HSI.xlsx in the notebook working directory before execution."
                    )

                df_raw = pd.read_excel(DATA_FILE)
                df_raw["Date"] = pd.to_datetime(df_raw["Date"])
                df_raw = df_raw.sort_values("Date").reset_index(drop=True)

                required_columns = {"Date", "Open", "High", "Low", "Close", "Up votes", "Down votes"}
                missing_columns = required_columns.difference(df_raw.columns)
                if missing_columns:
                    raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

                inspection = pd.DataFrame(
                    {
                        "dtype": df_raw.dtypes.astype(str),
                        "missing": df_raw.isna().sum(),
                    }
                )

                duplicate_rows = int(df_raw.duplicated().sum())
                df_raw["vote_sum"] = df_raw["Up votes"] + df_raw["Down votes"]
                df_raw["vote_anomaly"] = (df_raw["vote_sum"] - 1).abs() > VOTE_TOLERANCE
                vote_anomalies = int(df_raw["vote_anomaly"].sum())

                df_raw = df_raw.dropna(subset=["Up votes", "Down votes"]).reset_index(drop=True)

                summary_stats = df_raw[SUMMARY_COLUMNS].describe().T

                print(f"Shape: {df_raw.shape}")
                print(f"Date range: {df_raw['Date'].min().date()} to {df_raw['Date'].max().date()}")
                print(f"Duplicate rows: {duplicate_rows}")
                print(f"Vote sum anomalies: {vote_anomalies}")
                display(df_raw.head())
                display(inspection)
                display(summary_stats)
                """
            ),
            md(t["data_overview"]),
            code(
                """
                df = df_raw.copy()

                df["return_open"] = df["Open"].shift(-1) / df["Open"] - 1
                df["return_close"] = df["Close"].pct_change()

                df["sentiment_score"] = df["Up votes"] - df["Down votes"]
                df["vote_imbalance"] = df["sentiment_score"].abs()

                TRAIN_RATIO = 0.8
                split_n = int(len(df) * TRAIN_RATIO)
                q80 = df["sentiment_score"].iloc[:split_n].quantile(0.8)
                q20 = df["sentiment_score"].iloc[:split_n].quantile(0.2)
                df["is_train"] = False
                if split_n > 0:
                    df.loc[: split_n - 1, "is_train"] = True
                df["extreme_bull"] = df["sentiment_score"] >= q80
                df["extreme_bear"] = df["sentiment_score"] <= q20

                df["sentiment_lag1"] = df["sentiment_score"].shift(1)
                df["sentiment_lag2"] = df["sentiment_score"].shift(2)
                df["sentiment_lag3"] = df["sentiment_score"].shift(3)

                feature_summary = df[
                    ["sentiment_score", "vote_imbalance", "return_open", "return_close"]
                ].describe().T
                display(feature_summary)
                """
            ),
            md(t["feature_eng"]),
            code(
                """
                diagnostics = pd.DataFrame(
                    {
                        "metric": [
                            "Extreme bull days",
                            "Extreme bear days",
                            "Median vote imbalance",
                            "Valid next-day returns",
                        ],
                        "value": [
                            int(df["extreme_bull"].sum()),
                            int(df["extreme_bear"].sum()),
                            float(df["vote_imbalance"].median()),
                            int(df["return_open"].notna().sum()),
                        ],
                    }
                )

                display(diagnostics)
                """
            ),
            md(t["fig1"]),
            code(
                """
                fig, ax = plt.subplots(figsize=(14, 5))
                ax.plot(df["Date"], df["Close"], color="steelblue", linewidth=1.2)
                ax.set_title("HSI Close Price")
                ax.set_xlabel("Date")
                ax.set_ylabel("Close")
                plt.show()
                """
            ),
            md(t["fig2"]),
            code(
                """
                fig, ax1 = plt.subplots(figsize=(14, 5))
                ax2 = ax1.twinx()
                line1 = ax1.plot(df["Date"], df["Close"], color="steelblue", alpha=0.75, label="Close")
                line2 = ax2.plot(df["Date"], df["sentiment_score"], color="darkorange", alpha=0.75, label="Sentiment")
                ax1.set_title("HSI Price vs Sentiment Score")
                ax1.set_xlabel("Date")
                ax1.set_ylabel("Close", color="steelblue")
                ax2.set_ylabel("Sentiment Score", color="darkorange")
                lines = line1 + line2
                ax1.legend(lines, [line.get_label() for line in lines], loc="upper left")
                plt.show()
                """
            ),
            md(t["fig3"]),
            code(
                """
                fig, ax = plt.subplots(figsize=(10, 5))
                sentiment = df["sentiment_score"].dropna()
                ax.hist(sentiment, bins=50, density=True, alpha=0.6, color="steelblue", label="Histogram")
                sentiment.plot.kde(ax=ax, color="darkorange", linewidth=2, label="KDE")
                ax.set_title("Sentiment Score Distribution")
                ax.set_xlabel("Sentiment Score")
                ax.set_ylabel("Density")
                ax.legend()
                plt.show()
                """
            ),
            md(t["fig4"]),
            code(
                """
                scatter_df = df[["sentiment_score", "return_open"]].dropna()
                slope, intercept, r_value, p_value, _ = stats.linregress(
                    scatter_df["sentiment_score"],
                    scatter_df["return_open"],
                )

                fig, ax = plt.subplots(figsize=(8, 6))
                ax.scatter(scatter_df["sentiment_score"], scatter_df["return_open"], alpha=0.3, s=12)
                x_line = np.linspace(scatter_df["sentiment_score"].min(), scatter_df["sentiment_score"].max(), 100)
                ax.plot(x_line, slope * x_line + intercept, color="crimson", linewidth=2)
                ax.set_title(f"Sentiment vs Next-Day Return (r={r_value:.3f}, p={p_value:.3f})")
                ax.set_xlabel("Sentiment Score")
                ax.set_ylabel("Next-Day Open Return")
                plt.show()
                """
            ),
        ]
    )

    cells.extend(
        [
            code(
                """
                FEE_RATE = 0.001
                ANNUAL_FACTOR = 252

                def run_backtest(frame, signals, fee_rate=0.0):
                    portfolio = frame[["Date", "return_open"]].copy()
                    portfolio["signal"] = pd.Series(signals, index=frame.index).fillna(0).astype("int64")
                    portfolio["strategy_return"] = portfolio["signal"] * portfolio["return_open"].fillna(0.0)

                    position_change = portfolio["signal"].diff().abs().fillna(0)
                    portfolio["fee"] = position_change * fee_rate
                    portfolio["strategy_return"] = portfolio["strategy_return"] - portfolio["fee"]

                    cum_value = (1 + portfolio["strategy_return"]).cumprod()
                    portfolio["cum_return"] = cum_value - 1
                    portfolio["drawdown"] = (cum_value - cum_value.cummax()) / cum_value.cummax()
                    return portfolio

                def calculate_metrics(portfolio, annual_factor=ANNUAL_FACTOR):
                    returns = portfolio["strategy_return"].dropna()
                    total_return = (1 + returns).prod() - 1
                    n_years = len(returns) / annual_factor
                    annual_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0.0
                    annual_vol = returns.std() * np.sqrt(annual_factor)
                    sharpe = annual_return / annual_vol if annual_vol > 0 else 0.0
                    max_drawdown = portfolio["drawdown"].min()
                    active_days = (returns != 0).sum()
                    win_rate = (returns > 0).sum() / active_days if active_days > 0 else 0.0
                    total_fee = float(portfolio["fee"].sum())
                    num_trades = int(portfolio["signal"].diff().abs().fillna(0).sum())
                    return {
                        "Total Return": total_return,
                        "Annual Return": annual_return,
                        "Annual Volatility": annual_vol,
                        "Sharpe Ratio": sharpe,
                        "Max Drawdown": max_drawdown,
                        "Win Rate": win_rate,
                        "Total Fee Cost": total_fee,
                        "Num Trades": num_trades,
                    }

                def benchmark_buyhold(frame):
                    benchmark = frame[["Date", "return_close"]].copy()
                    benchmark["return_close"] = benchmark["return_close"].fillna(0.0)
                    benchmark["cum_return"] = (1 + benchmark["return_close"]).cumprod() - 1
                    cum_value = 1 + benchmark["cum_return"]
                    benchmark["drawdown"] = (cum_value - cum_value.cummax()) / cum_value.cummax()
                    return benchmark

                def rebase_portfolio(portfolio):
                    rebased = portfolio.copy()
                    cum_value = (1 + rebased["strategy_return"].fillna(0.0)).cumprod()
                    rebased["cum_return"] = cum_value - 1
                    rebased["drawdown"] = (cum_value - cum_value.cummax()) / cum_value.cummax()
                    return rebased

                def split_metrics(frame, results):
                    if "is_train" not in frame.columns:
                        return pd.DataFrame()
                    records = []
                    for period_name, mask in [
                        ("In-Sample (Train)", frame["is_train"]),
                        ("Out-of-Sample (Test)", ~frame["is_train"]),
                    ]:
                        period_index = frame.index[mask]
                        for strategy_name, result in results.items():
                            period_portfolio = result["portfolio"].loc[
                                result["portfolio"].index.isin(period_index)
                            ].copy()
                            period_portfolio = rebase_portfolio(period_portfolio)
                            metrics = calculate_metrics(period_portfolio)
                            records.append(
                                {
                                    "Period": period_name,
                                    "Strategy": strategy_name,
                                    **metrics,
                                }
                            )
                    return pd.DataFrame(records)

                strategy_map = {
                    "Strategy_A": df["signal_a"],
                    "Strategy_B": df["signal_b"],
                    "Strategy_C": df["signal_c"],
                }

                backtest_results = {}
                for strategy_name, signal_series in strategy_map.items():
                    for fee in [0.0, FEE_RATE]:
                        key = f"{strategy_name}_{'w_fee' if fee > 0 else 'no_fee'}"
                        portfolio = run_backtest(df, signal_series, fee_rate=fee)
                        backtest_results[key] = {
                            "portfolio": portfolio,
                            "metrics": calculate_metrics(portfolio),
                        }

                metrics_table = pd.DataFrame(
                    {name: result["metrics"] for name, result in backtest_results.items()}
                ).T

                display(
                    metrics_table.style.format(
                        {
                            "Total Return": "{:.2%}",
                            "Annual Return": "{:.2%}",
                            "Annual Volatility": "{:.2%}",
                            "Sharpe Ratio": "{:.3f}",
                            "Max Drawdown": "{:.2%}",
                            "Win Rate": "{:.2%}",
                            "Total Fee Cost": "{:.4f}",
                        }
                    )
                )

                split_metrics_table = split_metrics(df, backtest_results)
                if not split_metrics_table.empty:
                    split_date = df.loc[~df["is_train"], "Date"].iloc[0]
                    display(Markdown(f"**Train/Test split date:** {split_date.date()}"))
                    display(
                        split_metrics_table.style.format(
                            {
                                "Total Return": "{:.2%}",
                                "Annual Return": "{:.2%}",
                                "Annual Volatility": "{:.2%}",
                                "Sharpe Ratio": "{:.3f}",
                                "Max Drawdown": "{:.2%}",
                                "Win Rate": "{:.2%}",
                                "Total Fee Cost": "{:.4f}",
                            }
                        )
                    )
                """
            ),
            md(t["backtest"]),
            code(
                """
                benchmark = benchmark_buyhold(df)
                color_map = {
                    "Strategy_A": "#1f77b4",
                    "Strategy_B": "#ff7f0e",
                    "Strategy_C": "#2ca02c",
                }

                fig, ax = plt.subplots(figsize=(14, 7))
                ax.plot(
                    benchmark["Date"],
                    benchmark["cum_return"],
                    color="black",
                    linewidth=2,
                    label="Benchmark Buy & Hold",
                )

                for strategy_name, color in color_map.items():
                    no_fee = backtest_results[f"{strategy_name}_no_fee"]["portfolio"]
                    with_fee = backtest_results[f"{strategy_name}_w_fee"]["portfolio"]
                    ax.plot(no_fee["Date"], no_fee["cum_return"], color=color, linewidth=2, label=f"{strategy_name} no fee")
                    ax.plot(
                        with_fee["Date"],
                        with_fee["cum_return"],
                        color=color,
                        linewidth=1.8,
                        linestyle="--",
                        label=f"{strategy_name} w/ fee",
                    )

                ax.set_title("Cumulative Returns: Strategies vs Benchmark")
                ax.set_xlabel("Date")
                ax.set_ylabel("Cumulative Return")
                ax.legend(ncol=2)
                plt.show()
                """
            ),
            code(
                """
                fig, ax = plt.subplots(figsize=(14, 5))
                for name, result in backtest_results.items():
                    linestyle = "--" if name.endswith("w_fee") else "-"
                    ax.plot(
                        result["portfolio"]["Date"],
                        result["portfolio"]["drawdown"],
                        linestyle=linestyle,
                        linewidth=1.4,
                        label=name,
                    )
                ax.set_title("Drawdown Curves")
                ax.set_xlabel("Date")
                ax.set_ylabel("Drawdown")
                ax.legend(ncol=2)
                plt.show()

                monthly = backtest_results["Strategy_A_no_fee"]["portfolio"][["Date", "strategy_return"]].copy()
                monthly = monthly.set_index("Date")
                monthly_ret = monthly["strategy_return"].resample("ME").sum().to_frame("monthly_return")
                monthly_ret["Year"] = monthly_ret.index.year
                monthly_ret["Month"] = monthly_ret.index.month
                heatmap_data = monthly_ret.pivot(index="Year", columns="Month", values="monthly_return").reindex(columns=range(1, 13))

                fig, ax = plt.subplots(figsize=(14, 5))
                sns.heatmap(heatmap_data, annot=True, fmt=".2%", cmap="RdYlGn", center=0, ax=ax)
                ax.set_title("Monthly Returns Heatmap (Strategy A, No Fee)")
                ax.set_xlabel("Month")
                ax.set_ylabel("Year")
                plt.show()
                """
            ),
            code(
                """
                fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
                for i, strategy_name in enumerate(["Strategy_A", "Strategy_B", "Strategy_C"]):
                    series = backtest_results[f"{strategy_name}_no_fee"]["portfolio"]["strategy_return"].dropna()
                    axes[i].hist(series, bins=50, color="steelblue", alpha=0.75, edgecolor="white")
                    axes[i].axvline(0, color="red", linestyle="--", linewidth=1)
                    axes[i].set_title(f"{strategy_name} Return Distribution")
                    axes[i].set_xlabel("Daily Return")
                    axes[i].set_ylabel("Frequency")
                plt.show()
                """
            ),
            md(t["robustness"]),
            code(
                """
                def threshold_sensitivity_analysis(frame):
                    records = []
                    for threshold in [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]:
                        signals = (frame["sentiment_score"] < -threshold).astype(int) - (
                            frame["sentiment_score"] > threshold
                        ).astype(int)
                        portfolio = run_backtest(frame, signals, fee_rate=FEE_RATE)
                        metrics = calculate_metrics(portfolio)
                        records.append(
                            {
                                "threshold": threshold,
                                "Sharpe Ratio": metrics["Sharpe Ratio"],
                                "Annual Return": metrics["Annual Return"],
                                "Max Drawdown": metrics["Max Drawdown"],
                            }
                        )
                    return pd.DataFrame(records)

                def lag_signal_analysis(frame):
                    records = []
                    for lag in [0, 1, 2, 3]:
                        score = frame["sentiment_score"] if lag == 0 else frame[f"sentiment_lag{lag}"]
                        signals = (score < -0.1).astype(int) - (score > 0.1).astype(int)
                        portfolio = run_backtest(frame, signals, fee_rate=FEE_RATE)
                        metrics = calculate_metrics(portfolio)
                        records.append(
                            {
                                "lag": lag,
                                "Sharpe Ratio": metrics["Sharpe Ratio"],
                                "Annual Return": metrics["Annual Return"],
                                "Max Drawdown": metrics["Max Drawdown"],
                            }
                        )
                    return pd.DataFrame(records)

                def outlier_removal_analysis(frame):
                    winsorized = frame.copy()
                    winsorized["sentiment_winsorized"] = mstats.winsorize(
                        frame["sentiment_score"].fillna(0),
                        limits=[0.01, 0.01],
                    )

                    original_signals = (frame["sentiment_score"] < -0.1).astype(int) - (
                        frame["sentiment_score"] > 0.1
                    ).astype(int)
                    winsorized_signals = (winsorized["sentiment_winsorized"] < -0.1).astype(int) - (
                        winsorized["sentiment_winsorized"] > 0.1
                    ).astype(int)

                    original_portfolio = run_backtest(frame, original_signals, fee_rate=FEE_RATE)
                    winsorized_portfolio = run_backtest(frame, winsorized_signals, fee_rate=FEE_RATE)

                    original_metrics = calculate_metrics(original_portfolio)
                    winsorized_metrics = calculate_metrics(winsorized_portfolio)

                    return pd.DataFrame(
                        {
                            "Metric": ["Sharpe Ratio", "Annual Return", "Max Drawdown"],
                            "Original": [
                                original_metrics["Sharpe Ratio"],
                                original_metrics["Annual Return"],
                                original_metrics["Max Drawdown"],
                            ],
                            "Winsorized": [
                                winsorized_metrics["Sharpe Ratio"],
                                winsorized_metrics["Annual Return"],
                                winsorized_metrics["Max Drawdown"],
                            ],
                        }
                    )

                sensitivity_df = threshold_sensitivity_analysis(df)
                lag_df = lag_signal_analysis(df)
                outlier_df = outlier_removal_analysis(df)

                display(sensitivity_df.style.format({"Sharpe Ratio": "{:.3f}", "Annual Return": "{:.2%}", "Max Drawdown": "{:.2%}"}))
                display(lag_df.style.format({"Sharpe Ratio": "{:.3f}", "Annual Return": "{:.2%}", "Max Drawdown": "{:.2%}"}))
                display(outlier_df)

                fig, axes = plt.subplots(1, 3, figsize=(15, 5))
                axes[0].plot(sensitivity_df["threshold"], sensitivity_df["Sharpe Ratio"], "bo-")
                axes[0].set_title("Sharpe vs Threshold")
                axes[0].set_xlabel("Threshold")
                axes[0].set_ylabel("Sharpe Ratio")

                axes[1].plot(sensitivity_df["threshold"], sensitivity_df["Annual Return"], "go-")
                axes[1].set_title("Annual Return vs Threshold")
                axes[1].set_xlabel("Threshold")
                axes[1].set_ylabel("Annual Return")

                axes[2].plot(sensitivity_df["threshold"], sensitivity_df["Max Drawdown"], "ro-")
                axes[2].set_title("Max Drawdown vs Threshold")
                axes[2].set_xlabel("Threshold")
                axes[2].set_ylabel("Max Drawdown")
                plt.show()
                """
            ),
            code(
                """
                def rolling_sharpe(portfolio, window=252, annual_factor=252):
                    rolling_mean = portfolio["strategy_return"].rolling(window).mean()
                    rolling_std = portfolio["strategy_return"].rolling(window).std()
                    return (rolling_mean / rolling_std) * np.sqrt(annual_factor)

                no_fee_results = {
                    "Strategy_A": backtest_results["Strategy_A_no_fee"]["portfolio"],
                    "Strategy_B": backtest_results["Strategy_B_no_fee"]["portfolio"],
                    "Strategy_C": backtest_results["Strategy_C_no_fee"]["portfolio"],
                }

                fig, ax = plt.subplots(figsize=(14, 5))
                for name, portfolio in no_fee_results.items():
                    ax.plot(portfolio["Date"], rolling_sharpe(portfolio), label=name, alpha=0.8)
                ax.axhline(0, color="black", linestyle="--", alpha=0.6)
                ax.set_title("Rolling 12-Month Sharpe Ratio")
                ax.set_xlabel("Date")
                ax.set_ylabel("Sharpe Ratio")
                ax.legend()
                plt.show()

                display(Markdown(%%OVERFITTING_MD%%))
                """
            ),
            md(t["evaluation"]),
            code(
                """
                eval_rows = []
                for strategy_name in ["Strategy_A", "Strategy_B", "Strategy_C"]:
                    no_fee = backtest_results[f"{strategy_name}_no_fee"]["metrics"]
                    w_fee = backtest_results[f"{strategy_name}_w_fee"]["metrics"]
                    sharpe_drop_pct = (
                        np.nan
                        if np.isclose(no_fee["Sharpe Ratio"], 0)
                        else (no_fee["Sharpe Ratio"] - w_fee["Sharpe Ratio"]) / abs(no_fee["Sharpe Ratio"])
                    )
                    eval_rows.append(
                        {
                            "Strategy": strategy_name,
                            "Economic Idea": {
                                "Strategy_A": "Trade sentiment extremes only",
                                "Strategy_B": "Trade directional sentiment above threshold",
                                "Strategy_C": "Trade threshold signal only on high-conviction days",
                            }[strategy_name],
                            "Sharpe (No Fee)": no_fee["Sharpe Ratio"],
                            "Sharpe (With Fee)": w_fee["Sharpe Ratio"],
                            "Annual Return (With Fee)": w_fee["Annual Return"],
                            "Max DD (With Fee)": w_fee["Max Drawdown"],
                            "Trades (With Fee)": w_fee["Num Trades"],
                            "Sharpe Drop %": sharpe_drop_pct,
                        }
                    )

                evaluation_table = pd.DataFrame(eval_rows)
                display(
                    evaluation_table.style.format(
                        {
                            "Sharpe (No Fee)": "{:.3f}",
                            "Sharpe (With Fee)": "{:.3f}",
                            "Annual Return (With Fee)": "{:.2%}",
                            "Max DD (With Fee)": "{:.2%}",
                            "Sharpe Drop %": "{:.2%}",
                        }
                    )
                )
                """
            ),
            md(t["conclusion"]),
        ]
    )

    cells.extend(
        [
            md(t["fig5"]),
            code(
                """
                corr_cols = [
                    "sentiment_score",
                    "vote_imbalance",
                    "return_open",
                    "return_close",
                    "sentiment_lag1",
                    "sentiment_lag2",
                    "sentiment_lag3",
                ]
                corr = df[corr_cols].corr(method="spearman")

                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr, annot=True, fmt=".3f", cmap="RdBu_r", center=0, ax=ax)
                ax.set_title("Spearman Correlation Heatmap")
                plt.show()
                """
            ),
            md(t["signal_analysis"]),
            code(
                """
                MIN_MONTHLY_OBSERVATIONS = 5

                train_df = df.loc[df["is_train"]] if "is_train" in df.columns else df
                working = train_df.copy()
                working["year_month"] = working["Date"].dt.to_period("M")
                monthly_ic_records = []

                for period, group in working.groupby("year_month"):
                    clean = group[["sentiment_score", "return_open"]].dropna()
                    if len(clean) < MIN_MONTHLY_OBSERVATIONS:
                        continue
                    ic, p_val = stats.spearmanr(clean["sentiment_score"], clean["return_open"])
                    monthly_ic_records.append(
                        {
                            "period": period,
                            "ic": ic,
                            "p_value": p_val,
                            "n": len(clean),
                        }
                    )

                ic_df = pd.DataFrame(monthly_ic_records)
                if ic_df.empty:
                    raise ValueError("No monthly IC values were produced.")

                ic_df["period_dt"] = ic_df["period"].dt.to_timestamp()
                mean_ic = ic_df["ic"].mean()
                std_ic = ic_df["ic"].std()
                icir = np.nan if pd.isna(std_ic) or np.isclose(std_ic, 0) else mean_ic / std_ic
                positive_ic_pct = (ic_df["ic"] > 0).mean()
                ic_tstat, ic_pvalue = ttest_1samp(ic_df["ic"].dropna(), 0)

                ic_metrics = pd.DataFrame(
                    {
                        "metric": ["Mean IC", "IC Std", "ICIR", "IC > 0 pct", "IC t-stat", "IC p-value", "Months"],
                        "value": [mean_ic, std_ic, icir, positive_ic_pct, ic_tstat, ic_pvalue, len(ic_df)],
                    }
                )
                display(ic_metrics)

                fig, ax = plt.subplots(figsize=(14, 5))
                colors = ["green" if x > 0 else "red" for x in ic_df["ic"]]
                ax.bar(ic_df["period_dt"], ic_df["ic"], width=20, color=colors, alpha=0.7)
                ax.axhline(0, color="black", linewidth=0.7)
                ax.axhline(mean_ic, color="navy", linestyle="--", label=f"Mean IC={mean_ic:.4f}")
                ax.set_title("Monthly Information Coefficient")
                ax.set_xlabel("Date")
                ax.set_ylabel("Spearman IC")
                ax.legend()
                plt.show()
                """
            ),
            code(
                """
                train_df = df.loc[df["is_train"]] if "is_train" in df.columns else df
                decay_records = []
                for lag in [1, 2, 3]:
                    future_return = train_df["return_open"].shift(-lag)
                    clean = pd.DataFrame(
                        {"signal": train_df["sentiment_score"], "future_return": future_return}
                    ).dropna()
                    ic, p_val = stats.spearmanr(clean["signal"], clean["future_return"])
                    decay_records.append(
                        {
                            "horizon": f"t+{lag}",
                            "ic": ic,
                            "p_value": p_val,
                            "n": len(clean),
                        }
                    )

                decay_df = pd.DataFrame(decay_records)
                display(decay_df)

                fig, ax = plt.subplots(figsize=(8, 5))
                ax.bar(decay_df["horizon"], decay_df["ic"], color=["#1f77b4", "#6baed6", "#bdd7e7"])
                ax.axhline(0, color="black", linewidth=0.7)
                ax.set_title("Signal Decay Across Horizons")
                ax.set_xlabel("Forecast Horizon")
                ax.set_ylabel("Spearman IC")
                for idx, row in decay_df.iterrows():
                    offset = 0.001 if row["ic"] >= 0 else -0.003
                    ax.text(idx, row["ic"] + offset, f"{row['ic']:.4f}", ha="center")
                plt.show()
                """
            ),
            md(t["insights"]),
            code(
                """
                _vi_train = df.loc[df["is_train"]] if "is_train" in df.columns else df
                high_cutoff = _vi_train["vote_imbalance"].quantile(0.7)
                low_cutoff = _vi_train["vote_imbalance"].quantile(0.3)

                high_sample = _vi_train.loc[
                    _vi_train["vote_imbalance"] >= high_cutoff, ["sentiment_score", "return_open"]
                ].dropna()
                low_sample = _vi_train.loc[
                    _vi_train["vote_imbalance"] <= low_cutoff, ["sentiment_score", "return_open"]
                ].dropna()

                high_ic = stats.spearmanr(high_sample["sentiment_score"], high_sample["return_open"])[0]
                low_ic = stats.spearmanr(low_sample["sentiment_score"], low_sample["return_open"])[0]
                ic_spread = high_ic - low_ic

                lag_map = {row["horizon"]: row["ic"] for _, row in decay_df.iterrows()}

                %%INSIGHT_DYNAMIC%%

                display(Markdown(insight_text))
                """
            ),
            code(
                """
                def strategy_a_signals(frame):
                    signals = pd.Series(0, index=frame.index, dtype="int64")
                    signals.loc[frame["extreme_bull"]] = -1
                    signals.loc[frame["extreme_bear"]] = 1
                    return signals

                def strategy_b_signals(frame, threshold=0.1):
                    signals = pd.Series(0, index=frame.index, dtype="int64")
                    signals.loc[frame["sentiment_score"] > threshold] = -1
                    signals.loc[frame["sentiment_score"] < -threshold] = 1
                    return signals

                def strategy_c_signals(frame, threshold=0.1):
                    base = strategy_b_signals(frame, threshold=threshold)
                    if "is_train" in frame.columns:
                        median_imbalance = frame.loc[frame["is_train"], "vote_imbalance"].median()
                    else:
                        median_imbalance = frame["vote_imbalance"].median()
                    high_conviction = frame["vote_imbalance"] >= median_imbalance
                    return base.where(high_conviction, other=0).astype("int64")

                df["signal_a"] = strategy_a_signals(df)
                df["signal_b"] = strategy_b_signals(df, threshold=0.1)
                df["signal_c"] = strategy_c_signals(df, threshold=0.1)

                signal_summary = pd.DataFrame(
                    {
                        "Strategy A": df["signal_a"].value_counts().reindex([-1, 0, 1], fill_value=0),
                        "Strategy B": df["signal_b"].value_counts().reindex([-1, 0, 1], fill_value=0),
                        "Strategy C": df["signal_c"].value_counts().reindex([-1, 0, 1], fill_value=0),
                    }
                )
                signal_summary.index = ["Short (-1)", "Flat (0)", "Long (1)"]
                display(signal_summary)
                """
            ),
            md(t["strategy_design"]),
        ]
    )

    # Reorder: sections 1-4 first, then 5-11, then EDA figures 5-7 + signal/insights/strategy
    cells = cells[:16] + cells[27:] + cells[16:27]

    # Substitute placeholders in code cells
    insight_dynamic = TEXTS["insight_dynamic"][lang]
    overfitting_md = TEXTS["overfitting_md"][lang]
    for cell in cells:
        if cell["cell_type"] == "code":
            cell["source"] = (
                cell["source"]
                .replace("%%DATA_NAME%%", data_name)
                .replace("%%INSIGHT_DYNAMIC%%", insight_dynamic)
                .replace("%%OVERFITTING_MD%%", overfitting_md)
            )

    return cells


# ---------------------------------------------------------------------------
# Generate both notebooks
# ---------------------------------------------------------------------------

NOTEBOOK_META = {
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.x",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def auto_detect_data_name() -> str:
    """Find the first .xlsx file in cwd and return its stem."""
    xlsx_files = sorted(Path(".").glob("*.xlsx"))
    if not xlsx_files:
        raise FileNotFoundError("No .xlsx file found in current directory.")
    if len(xlsx_files) > 1:
        print(f"Multiple xlsx files found: {[f.name for f in xlsx_files]}, using {xlsx_files[0].name}")
    return xlsx_files[0].stem


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HSI research report notebooks.")
    parser.add_argument(
        "--data-name",
        default=None,
        help="Data file stem (e.g. 'HSI' for HSI.xlsx). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for generated notebooks (default: output/).",
    )
    args = parser.parse_args()

    data_name = args.data_name or auto_detect_data_name()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    outputs = {
        "en": output_dir / f"{data_name}_research_report.ipynb",
        "zh": output_dir / f"{data_name}_research_report_zh.ipynb",
    }

    for lang, output_path in outputs.items():
        notebook = {"cells": build_cells(lang, data_name=data_name), **NOTEBOOK_META}
        output_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{output_path} created successfully! ({len(notebook['cells'])} cells)")
