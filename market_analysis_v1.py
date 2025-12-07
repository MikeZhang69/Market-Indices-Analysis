import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set style for plots
plt.style.use('seaborn')
sns.set_palette("viridis")

def fetch_market_indices():
    """Fetch major market indices data"""
    # Define the tickers for major market indices
    indices = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones',
        '^IXIC': 'NASDAQ',
        '^FTSE': 'FTSE 100',
        '^GDAXI': 'DAX',
        '^N225': 'Nikkei 225',
        '^HSI': 'Hang Seng',
        '^AXJO': 'S&P/ASX 200'
    }
    
    # Set date range (1 year of data)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print(f"Fetching market data from {start_date.date()} to {end_date.date()}...")
    
    # Fetch data
    data = yf.download(
        tickers=list(indices.keys()),
        start=start_date,
        end=end_date,
        group_by='ticker',
        progress=False
    )
    
    return data, indices

def analyze_returns(data, indices):
    """Calculate and analyze returns for each index"""
    returns = {}
    
    for ticker, name in indices.items():
        try:
            # Get adjusted close prices
            prices = data[ticker]['Adj Close']
            
            # Calculate daily returns
            daily_returns = prices.pct_change().dropna()
            
            # Calculate cumulative returns
            cumulative_returns = (1 + daily_returns).cumprod()
            
            # Calculate annualized metrics
            annual_return = (1 + daily_returns.mean()) ** 252 - 1
            annual_volatility = daily_returns.std() * (252 ** 0.5)
            sharpe_ratio = (annual_return - 0.05) / annual_volatility  # Assuming 5% risk-free rate
            
            returns[name] = {
                'ticker': ticker,
                'daily_returns': daily_returns,
                'cumulative_returns': cumulative_returns,
                'annual_return': annual_return,
                'annual_volatility': annual_volatility,
                'sharpe_ratio': sharpe_ratio,
                'last_price': prices.iloc[-1],
                '52_week_high': prices.max(),
                '52_week_low': prices.min(),
                'current_vs_high': (prices.iloc[-1] / prices.max() - 1) * 100
            }
        except Exception as e:
            print(f"Error processing {name} ({ticker}): {str(e)}")
    
    return pd.DataFrame(returns).T

def plot_performance(returns_df):
    """Create interactive performance visualization"""
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '1-Year Cumulative Returns',
            'Annualized Return vs Volatility',
            '52-Week Performance',
            'Sharpe Ratio Comparison'
        ),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
              [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # 1. Cumulative Returns
    for idx, (index_name, row) in enumerate(returns_df.iterrows()):
        fig.add_trace(
            go.Scatter(
                x=row['cumulative_returns'].index,
                y=row['cumulative_returns'],
                name=index_name,
                mode='lines',
                line=dict(width=2)
            ),
            row=1, col=1
        )
    
    # 2. Risk-Return Scatter
    fig.add_trace(
        go.Scatter(
            x=returns_df['annual_volatility'],
            y=returns_df['annual_return'],
            mode='markers+text',
            text=returns_df.index,
            textposition='top center',
            marker=dict(
                size=12,
                color=returns_df['sharpe_ratio'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Sharpe Ratio')
            ),
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. 52-Week Performance
    for idx, (index_name, row) in enumerate(returns_df.iterrows()):
        fig.add_trace(
            go.Bar(
                x=[index_name],
                y=[(row['last_price'] / row['52_week_low'] - 1) * 100],
                name=index_name,
                text=f"{row['last_price']:,.2f}",
                textposition='auto',
                marker_color=f'rgba(55, 128, 191, {0.7 + idx*0.1})',
                showlegend=False
            ),
            row=2, col=1
        )
    
    # 4. Sharpe Ratio Comparison
    fig.add_trace(
        go.Bar(
            x=returns_df.index,
            y=returns_df['sharpe_ratio'],
            text=returns_df['sharpe_ratio'].round(2),
            textposition='auto',
            marker_color='rgba(50, 171, 96, 0.6)',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text='Global Market Indices Analysis',
        height=1000,
        showlegend=True,
        plot_bgcolor='white'
    )
    
    # Update axis labels
    fig.update_xaxes(title_text='Date', row=1, col=1)
    fig.update_yaxes(title_text='Cumulative Returns', row=1, col=1)
    fig.update_xaxes(title_text='Volatility (Annualized)', row=1, col=2)
    fig.update_yaxes(title_text='Return (Annualized)', row=1, col=2)
    fig.update_yaxes(title_text='% from 52-Week Low', row=2, col=1)
    fig.update_yaxes(title_text='Sharpe Ratio', row=2, col=2)
    
    return fig

def generate_report(returns_df):
    """Generate a summary report of the analysis"""
    # Sort by annual return
    top_performers = returns_df.sort_values('annual_return', ascending=False)
    
    print("\n=== MARKET INDICES ANALYSIS REPORT ===")
    print(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("\n=== TOP PERFORMING INDICES (1-YEAR) ===")
    print(top_performers[['annual_return', 'annual_volatility', 'sharpe_ratio']].head().to_string(
        formatter={
            'annual_return': '{:.1%}'.format,
            'annual_volatility': '{:.1%}'.format,
            'sharpe_ratio': '{:.2f}'.format
        }
    ))
    
    print("\n=== RISK-ADJUSTED RETURNS ===")
    print(returns_df.sort_values('sharpe_ratio', ascending=False)[['sharpe_ratio']].to_string(
        formatter={'sharpe_ratio': '{:.2f}'.format}
    ))
    
    print("\n=== CURRENT VS 52-WEEK HIGHS ===")
    print(returns_df.sort_values('current_vs_high', ascending=False)[['current_vs_high']].to_string(
        formatter={'current_vs_high': '{:.1f}%'.format}
    ))

def main():
    """Main function to run the analysis"""
    try:
        # Fetch market data
        data, indices = fetch_market_indices()
        
        # Analyze returns
        returns_df = analyze_returns(data, indices)
        
        # Generate report
        generate_report(returns_df)
        
        # Create and show interactive plot
        fig = plot_performance(returns_df)
        fig.show()
        
        # Save the plot as HTML
        fig.write_html("market_analysis.html")
        print("\nAnalysis complete! Interactive plot saved as 'market_analysis.html'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
