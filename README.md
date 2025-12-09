# Market Indices Analysis - How Time Matters for Investors

A comprehensive analysis tool for studying long-term market index performance across major global markets. This project fetches 35+ years of historical data (from January 1, 1990) to analyze how holding period affects investment returns across **14 major global indices** from **11 countries/regions**.

## Research Focus

**Key Question**: How does the length of holding period affect the probability of positive returns and overall investment performance?

## Features

- **35+ Years of Historical Data**: Fetches data from Jan 1, 1990 to present
- **Rolling Returns Analysis**: Calculate returns for 1, 3, 5, 10, 15, and 20-year holding periods
- **Probability Analysis**: Determine the probability of positive returns based on holding period
- **Correlation Analysis**: Understand how different markets move together
- **Interactive Visualizations**: Generate both static and interactive charts
- **Comprehensive Statistics**: Annualized returns, volatility, Sharpe ratio, max drawdown

## Included Indices

| Index | Symbol | Market | Data Start |
|-------|--------|--------|------------|
| S&P 500 | ^GSPC | US | 1990 |
| NASDAQ Composite | ^IXIC | US | 1990 |
| FTSE 100 | ^FTSE | UK | 1990 |
| Hang Seng Index | ^HSI | Hong Kong | 1990 |
| Nikkei 225 | ^N225 | Japan | 1990 |
| S&P/TSX Composite | ^GSPTSE | Canada | 1990 |
| FTSE Bursa Malaysia KLCI | ^KLSE | Malaysia | 1993 |
| CAC 40 | ^FCHI | France | 1990 |
| DAX | ^GDAXI | Germany | 1990 |
| Straits Times Index | ^STI | Singapore | 1990 |
| S&P/ASX 200 | ^AXJO | Australia | 1992 |
| Shanghai Composite | 000001 | China | 1990 |
| Shenzhen Component | 399001 | China | 1991 |
| CSI 300 | 000300 | China | 2002 |

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

## Viewing the Interactive Report

After running the analysis, you can view the interactive HTML report in several ways:

### Option 1: Open in VS Code
1. Locate the `normalized_performance.html` file in your project directory
2. Right-click on the file and select "Open Preview" or "Show Preview"
3. The interactive chart will open in VS Code's built-in preview pane

### Option 2: Open in Browser
1. Open your default web browser
2. Drag and drop the `normalized_performance.html` file into the browser window
3. Or use `File > Open File` in your browser and navigate to the HTML file

### Option 3: Command Line
```bash
# Open with default browser
xdg-open normalized_performance.html  # Linux
open normalized_performance.html      # macOS
start normalized_performance.html     # Windows
```

### Interactive Features
The HTML report includes:
- **Zoom and pan** through different time periods
- **Hover tooltips** showing exact values for each index
- **Legend toggle** to show/hide specific indices
- **Responsive design** that works on different screen sizes

## Key Metrics Calculated

- **Total Return**: Overall return from start to end
- **Annualized Return**: Compound annual growth rate (CAGR)
- **Annualized Volatility**: Standard deviation of returns (annualized)
- **Sharpe Ratio**: Risk-adjusted return measure
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Probability of Positive Return**: For various holding periods (1-20 years)

## Research Insights

This analysis helps answer questions like:
- What is the probability of making money if you hold for X years across 14 global markets?
- How does volatility decrease with longer holding periods?
- Which markets have been most correlated over the past 35+ years?
- What are the best and worst case scenarios for different holding periods?
- How do different regions perform relative to each other over time?
