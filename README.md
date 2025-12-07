# Market Indices Analysis - How Time Matters for Investors

A comprehensive analysis tool for studying long-term market index performance across major global markets. This project fetches 25 years of historical data (from January 1, 2000) to analyze how holding period affects investment returns.

## Research Focus

**Key Question**: How does the length of holding period affect the probability of positive returns and overall investment performance?

## Features

- **25 Years of Historical Data**: Fetches data from Jan 1, 2000 to present
- **Rolling Returns Analysis**: Calculate returns for 1, 3, 5, 10, 15, and 20-year holding periods
- **Probability Analysis**: Determine the probability of positive returns based on holding period
- **Correlation Analysis**: Understand how different markets move together
- **Interactive Visualizations**: Generate both static and interactive charts
- **Comprehensive Statistics**: Annualized returns, volatility, Sharpe ratio, max drawdown

## Included Indices

| Index | Symbol | Market |
|-------|--------|--------|
| S&P 500 | ^GSPC | US |
| NASDAQ-100 | ^NDX | US |
| FTSE 100 | ^FTSE | UK |
| Hang Seng Index | ^HSI | Hong Kong |
| Shanghai Composite | 000001.SS | China |
| Shenzhen Component | 399001.SZ | China |
| CSI 300 | 000300.SS | China |

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Market-Indices-Analysis.git
   cd Market-Indices-Analysis
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the analysis script:
```bash
python market_analysis.py
```

## Generated Outputs

### Data Files
- `market_indices_data.csv` - Raw historical price data
- `summary_statistics.csv` - Performance metrics for each index

### Visualizations
- `normalized_performance.html` - Interactive chart comparing all indices (base = 100)
- `cumulative_returns.png` - Long-term cumulative returns (log scale)
- `correlation_heatmap.png` - Correlation matrix of daily returns
- `rolling_returns_distribution.png` - Distribution of returns for different holding periods
- `positive_return_probability.png` - Probability of positive returns vs holding period

## Key Metrics Calculated

- **Total Return**: Overall return from start to end
- **Annualized Return**: Compound annual growth rate (CAGR)
- **Annualized Volatility**: Standard deviation of returns (annualized)
- **Sharpe Ratio**: Risk-adjusted return measure
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Probability of Positive Return**: For various holding periods (1-20 years)

## Research Insights

This analysis helps answer questions like:
- What is the probability of making money if you hold for X years?
- How does volatility decrease with longer holding periods?
- Which markets have been most correlated over the past 25 years?
- What are the best and worst case scenarios for different holding periods?
