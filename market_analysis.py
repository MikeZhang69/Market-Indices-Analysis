import yfinance as yf
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

class MarketIndexAnalyzer:
    def __init__(self):
        # Major world market indices for long-term analysis (Yahoo Finance)
        self.yf_indices = {
            '^GSPC': 'S&P 500',           # US - Standard & Poor's 500
            '^IXIC': 'NASDAQ Composite',    # US - Nasdaq Composite Index
            '^FTSE': 'FTSE 100',           # UK - Financial Times Stock Exchange 100
            '^HSI': 'Hang Seng',           # Hong Kong - Hang Seng Index
            '^N225': 'Nikkei 225',          # Japan - Nikkei 225
            '^GSPTSE': 'S&P/TSX Composite', # Canada - S&P/TSX Composite
            '^KLSE': 'FTSE Bursa Malaysia KLCI',  # Malaysia - FBM KLCI (primary ticker)
            '^FCHI': 'CAC 40',             # France - CAC 40
            '^GDAXI': 'DAX',               # Germany - DAX
            '^STI': 'Straits Times Index', # Singapore - STI
            '^AXJO': 'S&P/ASX 200',        # Australia - S&P/ASX 200
        }
        # Optional Yahoo Finance fallback tickers for select indices
        self.yf_fallbacks = {
            'FTSE Bursa Malaysia KLCI': ['^FBMKLCI'],
        }
        # China indices via AkShare (better historical data)
        self.akshare_china_indices = {
            'sh000001': 'Shanghai Composite',  # China - Shanghai Composite Index
            'sz399001': 'Shenzhen Component',  # China - Shenzhen Component Index
            'sh000300': 'CSI 300',             # China - CSI 300 Index
        }
        # US indices via AkShare (backup/alternative source)
        self.akshare_us_indices = {
            '.INX': 'S&P 500',             # S&P 500 via Sina
            '.IXIC': 'NASDAQ Composite',    # NASDAQ Composite via Sina
        }
        self.data = pd.DataFrame()
        self.start_date = '1950-09-07'
        self.end_date = datetime.now().strftime('%Y-%m-%d')
    
    def fetch_data(self):
        """Fetch historical market data for all indices between the configured dates"""
        print(f"Fetching data from {self.start_date} to {self.end_date}")
        print("-" * 50)
        
        all_data = {}
        failed_yf = []  # Track failed Yahoo Finance downloads
        start_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(self.end_date, '%Y-%m-%d')
        
        # Fetch from Yahoo Finance
        print("Fetching from Yahoo Finance...")
        for ticker, name in self.yf_indices.items():
            try:
                df = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False, auto_adjust=True)
                if not df.empty:
                    # Handle both single and multi-level column index
                    if isinstance(df.columns, pd.MultiIndex):
                        if 'Close' in df.columns.get_level_values(0):
                            close_col = df['Close'].iloc[:, 0]
                        else:
                            close_col = df.iloc[:, 0]
                    else:
                        close_col = df['Close'] if 'Close' in df.columns else df.iloc[:, 0]
                    
                    close_series = pd.Series(close_col.values, index=close_col.index, name=name)
                    all_data[name] = close_series
                    print(f"  ✓ {name}: {len(close_series)} trading days ({close_series.index[0].strftime('%Y-%m-%d')} to {close_series.index[-1].strftime('%Y-%m-%d')})")
                else:
                    print(f"  ✗ {name}: No data from Yahoo Finance")
                    failed_yf.append(name)
            except Exception as e:
                print(f"  ✗ {name}: Yahoo Finance error")
                failed_yf.append(name)

        # Attempt Yahoo Finance fallbacks for tickers with known alternates
        if failed_yf:
            print("\nRetrying failed indices with Yahoo Finance fallback tickers...")
            still_failed = []
            for name in failed_yf:
                fallback_tickers = self.yf_fallbacks.get(name, [])
                recovered = False
                for fb_ticker in fallback_tickers:
                    try:
                        df = yf.download(fb_ticker, start=self.start_date, end=self.end_date, progress=False, auto_adjust=True)
                        if not df.empty:
                            if isinstance(df.columns, pd.MultiIndex):
                                if 'Close' in df.columns.get_level_values(0):
                                    close_col = df['Close'].iloc[:, 0]
                                else:
                                    close_col = df.iloc[:, 0]
                            else:
                                close_col = df['Close'] if 'Close' in df.columns else df.iloc[:, 0]

                            close_series = pd.Series(close_col.values, index=close_col.index, name=name)
                            all_data[name] = close_series
                            print(f"  ✓ {name}: recovered via fallback ticker {fb_ticker}")
                            recovered = True
                            break
                    except Exception:
                        continue
                if not recovered:
                    still_failed.append(name)
            failed_yf = still_failed
        
        # Try AkShare as fallback for failed US indices
        if failed_yf:
            print("\nFetching failed indices from AkShare (backup)...")
            for ak_ticker, name in self.akshare_us_indices.items():
                if name in failed_yf and name not in all_data:
                    try:
                        df = ak.index_us_stock_sina(symbol=ak_ticker)
                        if not df.empty:
                            df['date'] = pd.to_datetime(df['date'])
                            df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
                            df = df.set_index('date')
                            
                            close_series = pd.Series(df['close'].values, index=df.index, name=name)
                            all_data[name] = close_series
                            print(f"  ✓ {name}: {len(close_series)} trading days ({close_series.index[0].strftime('%Y-%m-%d')} to {close_series.index[-1].strftime('%Y-%m-%d')})")
                    except Exception as e:
                        print(f"  ✗ {name}: AkShare also failed - {str(e)}")
        
        # Fetch from AkShare (for China indices with better historical data)
        print("\nFetching from AkShare (China indices)...")
        for ticker, name in self.akshare_china_indices.items():
            try:
                df = ak.stock_zh_index_daily(symbol=ticker)
                if not df.empty:
                    # Convert date column and filter by date range
                    df['date'] = pd.to_datetime(df['date'])
                    df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
                    df = df.set_index('date')
                    
                    close_series = pd.Series(df['close'].values, index=df.index, name=name)
                    all_data[name] = close_series
                    print(f"  ✓ {name}: {len(close_series)} trading days ({close_series.index[0].strftime('%Y-%m-%d')} to {close_series.index[-1].strftime('%Y-%m-%d')})")
                else:
                    print(f"  ✗ {name}: No data available")
            except Exception as e:
                print(f"  ✗ {name}: Error - {str(e)}")
        
        self.data = pd.DataFrame(all_data)
        print("-" * 50)
        print(f"Total indices loaded: {len(self.data.columns)}")
        
        return self.data
    
    def calculate_returns(self):
        """Calculate daily and cumulative returns"""
        if self.data.empty:
            print("Please fetch data first using fetch_data()")
            return None, None
        
        # Calculate daily returns
        # Avoid implicit forward-fill default in future pandas versions
        daily_returns = self.data.pct_change(fill_method=None).dropna()
        
        # Calculate cumulative returns (normalized to start at 1)
        cumulative_returns = (1 + daily_returns).cumprod()
        
        return daily_returns, cumulative_returns
    
    def calculate_rolling_returns(self, years=1):
        """Calculate rolling returns for a given period"""
        trading_days = years * 252  # Approximate trading days per year
        rolling_returns = self.data.pct_change(periods=trading_days, fill_method=None)
        return rolling_returns
    
    def calculate_holding_period_returns(self):
        """Calculate returns for different holding periods to study time impact"""
        holding_periods = {
            '1 Year': 252,
            '3 Years': 252 * 3,
            '5 Years': 252 * 5,
            '10 Years': 252 * 10,
            '15 Years': 252 * 15,
            '20 Years': 252 * 20
        }
        
        results = {}
        for period_name, days in holding_periods.items():
            rolling = self.data.pct_change(periods=days, fill_method=None)
            # Calculate stats for each column separately to handle different data lengths
            results[period_name] = {
                'mean': rolling.mean() * 100,
                'std': rolling.std() * 100,
                'min': rolling.min() * 100,
                'max': rolling.max() * 100,
                'positive_pct': (rolling > 0).sum() / rolling.notna().sum() * 100
            }
        return results
    
    def plot_normalized_performance(self):
        """Plot normalized performance (all starting at 100) for comparison"""
        # Normalize each column from its first valid value
        normalized = pd.DataFrame()
        for col in self.data.columns:
            series = self.data[col].dropna()
            if not series.empty:
                normalized[col] = series / series.iloc[0] * 100
        
        fig = go.Figure()
        for column in normalized.columns:
            fig.add_trace(go.Scatter(
                x=normalized[column].dropna().index,
                y=normalized[column].dropna(),
                mode='lines',
                name=column
            ))
        
        fig.update_layout(
            title='Normalized Performance of Major Market Indices (Base = 100)',
            xaxis_title='Date',
            yaxis_title='Index Value (Normalized)',
            hovermode='x unified',
            template='plotly_white',
            height=600
        )
        fig.write_html('normalized_performance.html')
        print("Saved normalized performance plot as 'normalized_performance.html'")
        return fig
    
    def plot_cumulative_returns(self):
        """Plot cumulative returns of all indices"""
        plt.figure(figsize=(16, 8))
        
        for column in self.data.columns:
            series = self.data[column].dropna()
            if not series.empty:
                # Calculate cumulative returns from first valid value
                daily_ret = series.pct_change().dropna()
                cum_ret = (1 + daily_ret).cumprod()
                plt.plot(cum_ret.index, cum_ret, label=column, linewidth=1.5)
        
        plt.title('Cumulative Returns of Major Market Indices', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Cumulative Returns', fontsize=12)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.yscale('log')  # Log scale to better visualize long-term growth
        plt.tight_layout()
        plt.savefig('cumulative_returns.png', dpi=150)
        plt.close()
        print("Saved cumulative returns plot as 'cumulative_returns.png'")
    
    def plot_correlation_heatmap(self):
        """Plot correlation heatmap of index returns"""
        daily_returns, _ = self.calculate_returns()
        if daily_returns is None:
            return
        
        plt.figure(figsize=(10, 8))
        corr_matrix = daily_returns.corr()
        sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', vmin=-1, vmax=1, 
                    fmt='.2f', square=True, linewidths=0.5)
        plt.title('Correlation Matrix of Market Index Daily Returns', fontsize=14)
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=150)
        plt.close()
        print("Saved correlation heatmap as 'correlation_heatmap.png'")
    
    def plot_rolling_returns_distribution(self):
        """Plot distribution of rolling returns for different holding periods"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        periods = [1, 3, 5, 10, 15, 20]
        
        for ax, years in zip(axes.flatten(), periods):
            rolling = self.calculate_rolling_returns(years)
            if not rolling.empty:
                for column in rolling.columns:
                    ax.hist(rolling[column].dropna() * 100, bins=50, alpha=0.5, label=column)
                ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
                ax.set_title(f'{years}-Year Rolling Returns Distribution', fontsize=12)
                ax.set_xlabel('Return (%)')
                ax.set_ylabel('Frequency')
                ax.legend(fontsize=8)
        
        plt.tight_layout()
        plt.savefig('rolling_returns_distribution.png', dpi=150)
        plt.close()
        print("Saved rolling returns distribution as 'rolling_returns_distribution.png'")
    
    def plot_positive_return_probability(self):
        """Plot probability of positive returns vs holding period"""
        periods = list(range(1, 21))  # 1 to 20 years
        
        prob_data = {col: [] for col in self.data.columns}
        
        for years in periods:
            rolling = self.calculate_rolling_returns(years)
            for col in self.data.columns:
                if col in rolling.columns and not rolling[col].dropna().empty:
                    prob = (rolling[col].dropna() > 0).mean() * 100
                    prob_data[col].append(prob)
                else:
                    prob_data[col].append(np.nan)
        
        plt.figure(figsize=(14, 8))
        for col, probs in prob_data.items():
            plt.plot(periods, probs, marker='o', label=col, linewidth=2, markersize=6)
        
        plt.axhline(y=50, color='gray', linestyle='--', alpha=0.7)
        plt.xlabel('Holding Period (Years)', fontsize=12)
        plt.ylabel('Probability of Positive Return (%)', fontsize=12)
        plt.title('Probability of Positive Returns vs Holding Period', fontsize=16)
        plt.legend(loc='lower right')
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 105)
        plt.xticks(periods)
        plt.tight_layout()
        plt.savefig('positive_return_probability.png', dpi=150)
        plt.close()
        print("Saved positive return probability plot as 'positive_return_probability.png'")
    
    def generate_summary_statistics(self):
        """Generate comprehensive summary statistics"""
        daily_returns, _ = self.calculate_returns()
        if daily_returns is None:
            return None
        
        # Annualized statistics
        stats = pd.DataFrame({
            'Total Return (%)': ((self.data.iloc[-1] / self.data.iloc[0] - 1) * 100).round(2),
            'Annualized Return (%)': ((self.data.iloc[-1] / self.data.iloc[0]) ** (252 / len(self.data)) - 1) * 100,
            'Annualized Volatility (%)': daily_returns.std() * np.sqrt(252) * 100,
            'Sharpe Ratio': (daily_returns.mean() / daily_returns.std()) * np.sqrt(252),
            'Max Drawdown (%)': self._calculate_max_drawdown() * 100,
            'Best Day (%)': daily_returns.max() * 100,
            'Worst Day (%)': daily_returns.min() * 100,
            'Data Start': self.data.apply(lambda x: x.dropna().index[0].strftime('%Y-%m-%d') if not x.dropna().empty else 'N/A'),
            'Data End': self.data.apply(lambda x: x.dropna().index[-1].strftime('%Y-%m-%d') if not x.dropna().empty else 'N/A'),
            'Trading Days': self.data.count()
        })
        
        return stats.round(2)
    
    def _calculate_max_drawdown(self):
        """Calculate maximum drawdown for each index"""
        max_dd = {}
        for col in self.data.columns:
            series = self.data[col].dropna()
            rolling_max = series.expanding().max()
            drawdown = (series - rolling_max) / rolling_max
            max_dd[col] = drawdown.min()
        return pd.Series(max_dd)
    
    def save_data_to_csv(self):
        """Save the fetched data to CSV for further analysis"""
        # Reorder columns as requested
        desired_order = [
            'Shanghai Composite', 'Shenzhen Component', 'CSI 300',
            'Nikkei 225', 'S&P/TSX Composite', 'FTSE Bursa Malaysia KLCI',
            'CAC 40', 'DAX', 'Straits Times Index', 'S&P/ASX 200',
            'S&P 500', 'NASDAQ Composite', 'FTSE 100', 'Hang Seng'
        ]
        
        # Filter to include only columns that actually exist in the fetched data
        # taking into account that some might have failed to download
        available_columns = [col for col in desired_order if col in self.data.columns]
        
        # Add any other columns that might be in data but not in our specific order list
        other_columns = [col for col in self.data.columns if col not in available_columns]
        final_order = available_columns + other_columns
        
        # Create a copy with reordered columns
        df_to_save = self.data[final_order].copy()
        
        # Rename index to snapshot_date
        df_to_save.index.name = 'snapshot_date'
        
        df_to_save.to_csv('market_indices_data.csv')
        print("Saved raw data to 'market_indices_data.csv'")

def get_date_input(prompt, default_value):
    """Get date input from user with validation"""
    while True:
        user_input = input(f"{prompt} [{default_value}]: ").strip()
        if not user_input:
            return default_value
        try:
            datetime.strptime(user_input, '%Y-%m-%d')
            return user_input
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")

if __name__ == "__main__":
    print("=" * 60)
    print("MARKET INDEX ANALYSIS - Time Matters for Investors")
    print("=" * 60)
    print()
    
    # Get date range from user
    default_start = '1950-09-07'
    default_end = datetime.now().strftime('%Y-%m-%d')
    
    print("Enter date range for analysis (press Enter for default):")
    start_date = get_date_input("Start date (YYYY-MM-DD)", default_start)
    end_date = get_date_input("End date (YYYY-MM-DD)", default_end)
    
    print()
    
    # Initialize the analyzer with user-specified dates
    analyzer = MarketIndexAnalyzer()
    analyzer.start_date = start_date
    analyzer.end_date = end_date
    
    analyzer.fetch_data()
    
    # Save raw data
    print("\n" + "=" * 60)
    print("SAVING DATA")
    print("=" * 60)
    analyzer.save_data_to_csv()
    
    # Generate summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    stats = analyzer.generate_summary_statistics()
    if stats is not None:
        print(stats.to_string())
        stats.to_csv('summary_statistics.csv')
        print("\nSaved summary statistics to 'summary_statistics.csv'")
    
    # Generate visualizations
    print("\n" + "=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    analyzer.plot_normalized_performance()
    analyzer.plot_cumulative_returns()
    analyzer.plot_correlation_heatmap()
    analyzer.plot_rolling_returns_distribution()
    analyzer.plot_positive_return_probability()
    
    # Holding period analysis
    print("\n" + "=" * 60)
    print("HOLDING PERIOD ANALYSIS - How Time Matters")
    print("=" * 60)
    holding_results = analyzer.calculate_holding_period_returns()
    for period, metrics in holding_results.items():
        print(f"\n{period} Holding Period:")
        print(f"  Probability of Positive Return:")
        for idx, prob in metrics['positive_pct'].items():
            print(f"    {idx}: {prob:.1f}%")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - market_indices_data.csv (raw price data)")
    print("  - summary_statistics.csv (performance metrics)")
    print("  - normalized_performance.html (interactive chart)")
    print("  - cumulative_returns.png")
    print("  - correlation_heatmap.png")
    print("  - rolling_returns_distribution.png")
    print("  - positive_return_probability.png")
