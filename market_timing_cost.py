"""
Market Timing Cost Analysis
Analyzes the cost of missing the best trading days
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def analyze_market_timing_cost(csv_file='market_indices_data.csv', index_name='S&P 500 (US)', initial_investment=10000):
    """
    Analyze the cost of missing the best trading days
    
    Parameters:
    - csv_file: Path to the CSV file with market data
    - index_name: Name of the index to analyze
    - initial_investment: Starting investment amount
    """
    
    # Load data
    print(f"Loading data from {csv_file}...")
    df = pd.read_csv(csv_file, index_col='snapshot_date', parse_dates=True)
    
    if index_name not in df.columns:
        print(f"Error: {index_name} not found in data. Available indices: {list(df.columns)}")
        return None
    
    # Get the price series
    prices = df[index_name].dropna()
    
    if len(prices) < 100:
        print(f"Error: Not enough data for {index_name}")
        return None
    
    print(f"Analyzing {index_name} from {prices.index[0].date()} to {prices.index[-1].date()}")
    print(f"Total trading days: {len(prices)}")
    
    # Calculate daily returns
    daily_returns = prices.pct_change().dropna()
    
    # Calculate fully invested scenario
    fully_invested_value = initial_investment * (1 + daily_returns).prod()
    fully_invested_annualized = ((fully_invested_value / initial_investment) ** (252 / len(daily_returns))) - 1
    
    # Sort returns to find best days
    sorted_returns = daily_returns.sort_values(ascending=False)
    
    # Calculate scenarios for missing best days
    scenarios = []
    best_days_to_miss = [5, 10, 20, 30, 40]
    
    for n_days in best_days_to_miss:
        # Remove the top N best days
        best_days = sorted_returns.head(n_days).index
        returns_without_best = daily_returns.copy()
        returns_without_best.loc[best_days] = 0  # Set best days to 0% return (missed them)
        
        # Calculate final value
        final_value = initial_investment * (1 + returns_without_best).prod()
        annualized_return = ((final_value / initial_investment) ** (252 / len(returns_without_best))) - 1
        lost_amount = fully_invested_value - final_value
        lost_percentage = (lost_amount / fully_invested_value) * 100
        
        scenarios.append({
            'scenario': f'Miss {n_days} Best',
            'final_value': final_value,
            'annualized_return': annualized_return * 100,
            'lost_amount': lost_amount,
            'lost_percentage': lost_percentage
        })
    
    # Add fully invested scenario
    scenarios.insert(0, {
        'scenario': 'Fully Invested',
        'final_value': fully_invested_value,
        'annualized_return': fully_invested_annualized * 100,
        'lost_amount': 0,
        'lost_percentage': 0
    })
    
    # Create DataFrame
    results_df = pd.DataFrame(scenarios)
    
    # Print results
    print("\n" + "=" * 80)
    print(f"MARKET TIMING COST ANALYSIS: {index_name}")
    print("=" * 80)
    print(f"\nStarting Investment: ${initial_investment:,.2f}")
    print(f"Analysis Period: {prices.index[0].date()} to {prices.index[-1].date()}")
    print(f"Total Trading Days: {len(daily_returns):,}")
    print("\nResults:")
    print(results_df.to_string(index=False))
    
    # Create visualization
    create_visualization(results_df, index_name, initial_investment, prices.index[0], prices.index[-1])
    
    return results_df

def create_visualization(results_df, index_name, initial_investment, start_date, end_date):
    """Create a comprehensive visualization of market timing costs"""
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[2, 1.5, 0.8], hspace=0.3)
    
    # Color scheme
    colors = ['#2ecc71', '#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#c0392b']
    
    # 1. Bar Chart
    ax1 = fig.add_subplot(gs[0, 0])
    
    scenarios = results_df['scenario'].values
    values = results_df['final_value'].values
    
    bars = ax1.bar(range(len(scenarios)), values, color=colors[:len(scenarios)], edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${val:,.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_xticks(range(len(scenarios)))
    ax1.set_xticklabels(scenarios, rotation=0, ha='center')
    ax1.set_ylabel('Final Value (USD)', fontsize=12, fontweight='bold')
    ax1.set_title(f'The Cost of Market Timing: Missing the Best Days\n{index_name} - Starting with ${initial_investment:,} investment',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, max(values) * 1.15)
    
    # Format y-axis as currency
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}k'))
    
    # 2. Data Table
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.axis('tight')
    ax2.axis('off')
    
    # Prepare table data
    table_data = []
    for _, row in results_df.iterrows():
        if row['scenario'] == 'Fully Invested':
            lost_text = 'Baseline'
        else:
            lost_text = f"-${row['lost_amount']:,.0f} ({row['lost_percentage']:.1f}%)"
        
        table_data.append([
            row['scenario'],
            f"${row['final_value']:,.0f}",
            f"{row['annualized_return']:.2f}%",
            lost_text
        ])
    
    table = ax2.table(cellText=table_data,
                     colLabels=['Scenario', 'Final Value', 'Annualized Return', 'Lost vs Fully Invested'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.25, 0.25, 0.25, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style the header
    for i in range(4):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style the baseline row
    for i in range(4):
        table[(1, i)].set_facecolor('#e8f5e9')
    
    # Style other rows with gradient
    for row_idx in range(2, len(table_data) + 1):
        intensity = 1.0 - (row_idx - 2) * 0.15
        for i in range(4):
            table[(row_idx, i)].set_facecolor((1.0, intensity, intensity))
    
    # 3. Warning/Note Box
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.axis('off')
    
    note_text = (
        "⚠️ The Hidden Cost of Market Timing\n\n"
        "The best trading days often occur during periods of high volatility, right after the worst days. "
        "If you're out of the market trying to avoid losses, you'll likely miss the biggest gains too. "
        "Stay invested!"
    )
    
    ax3.text(0.5, 0.5, note_text,
            ha='center', va='center',
            fontsize=11,
            bbox=dict(boxstyle='round,pad=1', facecolor='#fff3e0', edgecolor='#ff9800', linewidth=2),
            transform=ax3.transAxes)
    
    # Add period info
    period_text = f"Analysis Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    fig.text(0.5, 0.02, period_text, ha='center', fontsize=9, style='italic', color='gray')
    
    plt.suptitle('', fontsize=1)  # Remove default suptitle
    
    # Save figure
    output_file = 'market_timing_cost.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"\nVisualization saved as '{output_file}'")
    
    return output_file

if __name__ == "__main__":
    # Analyze S&P 500 as the primary example
    print("=" * 80)
    print("MARKET TIMING COST ANALYSIS")
    print("=" * 80)
    print()
    
    # You can change these parameters
    results = analyze_market_timing_cost(
        csv_file='market_indices_data.csv',
        index_name='S&P 500',
        initial_investment=10000
    )
    
    if results is not None:
        # Save results to CSV
        results.to_csv('market_timing_cost_results.csv', index=False)
        print(f"\nResults saved to 'market_timing_cost_results.csv'")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

