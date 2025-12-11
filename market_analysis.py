import pandas as pd
import matplotlib.pyplot as plt
try:
    import seaborn as sns
except ImportError:
    sns = None
    print("Warning: Seaborn not found. Heatmaps will be skipped or degraded.")
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None
    print("Warning: Plotly not found. Interactive charts will be skipped.")
from datetime import datetime, timedelta
import numpy as np
import os

class MarketIndexAnalyzer:
    def __init__(self):
        # Major world market indices for long-term analysis (Yahoo Finance)
        self.yf_indices = {
            '^GSPC': 'S&P 500 (US)',           # US - Standard & Poor's 500
            '^IXIC': 'NASDAQ Composite (US)',    # US - Nasdaq Composite Index
            '^FTSE': 'FTSE 100 (UK)',           # UK - Financial Times Stock Exchange 100
            '^HSI': 'Hang Seng (HK)',           # Hong Kong - Hang Seng Index
            '^N225': 'Nikkei 225 (JP)',          # Japan - Nikkei 225
            '^GSPTSE': 'S&P/TSX Composite (CA)', # Canada - S&P/TSX Composite
            '^KLSE': 'FTSE Bursa Malaysia KLCI (MY)',  # Malaysia - FBM KLCI (primary ticker)
            '^FCHI': 'CAC 40 (FR)',             # France - CAC 40
            '^GDAXI': 'DAX (German)',               # Germany - DAX
            '^STI': 'Straits Times Index (SG)', # Singapore - STI
            '^AXJO': 'S&P/ASX 200 (AU)',        # Australia - S&P/ASX 200
        }
        # Optional Yahoo Finance fallback tickers for select indices
        self.yf_fallbacks = {
            'FTSE Bursa Malaysia KLCI': ['^FBMKLCI'],
        }
        # China indices via AkShare (better historical data)
        self.akshare_china_indices = {
            'sh000001': 'Shanghai Composite (CN)',  # China - Shanghai Composite Index
            'sz399001': 'Shenzhen Component (CN)',  # China - Shenzhen Component Index
            'sh000300': 'CSI 300 (CN)',             # China - CSI 300 Index
        }
        # US indices via AkShare (backup/alternative source)
        self.akshare_us_indices = {
            '.INX': 'S&P 500 (US)',             # S&P 500 via Sina
            '.IXIC': 'NASDAQ Composite (US)',    # NASDAQ Composite via Sina
        }
        self.data = pd.DataFrame()
        self.start_date = '1950-09-07'
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Set style for professional financial look (Navy/Gold/White theme)
        plt.style.use('seaborn-v0_8-whitegrid')
        
        self.colors = [
            '#003366',  # Deep Navy (Primary)
            '#C0B283',  # Muted Gold (Secondary)
            '#2E8B57',  # Sea Green (Success/Growth)
            '#D32F2F',  # Crimson (Risk/Loss)
            '#5D4037',  # Brown (Earth tones)
            '#757575',  # Grey (Neutral)
            '#0288D1',  # Light Blue
            '#7B1FA2',  # Purple
            '#388E3C',  # Dark Green
            '#FBC02D',  # Bright Gold
            '#E64A19',  # Deep Orange
            '#455A64',  # Blue Grey
            '#1976D2',  # Blue
            '#C2185B'   # Pink
        ]
        
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'axes.prop_cycle': plt.cycler(color=self.colors),
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.color': '#cccccc',
            'text.color': '#333333',
            'axes.labelcolor': '#333333',
            'xtick.color': '#333333',
            'ytick.color': '#333333',
            'legend.frameon': True,
            'legend.facecolor': 'white',
            'legend.edgecolor': '#cccccc',
            'figure.autolayout': True
        })
    
    def fetch_data(self, use_local_if_available=True):
        """Fetch historical market data or load from local CSV"""
        csv_file = 'market_indices_data.csv'
        
        if use_local_if_available and os.path.exists(csv_file):
            print(f"Loading data from local file: {csv_file}")
            try:
                self.data = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                
                # Migration logic: Rename old columns to new names with country codes
                # This handles data loaded from existing CSVs without needing to re-fetch
                migration_map = {
                    'S&P 500': 'S&P 500 (US)',
                    'NASDAQ Composite': 'NASDAQ Composite (US)',
                    'FTSE 100': 'FTSE 100 (UK)',
                    'Hang Seng': 'Hang Seng (HK)',
                    'Nikkei 225': 'Nikkei 225 (JP)',
                    'S&P/TSX Composite': 'S&P/TSX Composite (CA)',
                    'FTSE Bursa Malaysia KLCI': 'FTSE Bursa Malaysia KLCI (MY)',
                    'CAC 40': 'CAC 40 (FR)',
                    'DAX': 'DAX (German)',
                    'Straits Times Index': 'Straits Times Index (SG)',
                    'S&P/ASX 200': 'S&P/ASX 200 (AU)',
                    'Shanghai Composite': 'Shanghai Composite (CN)',
                    'Shenzhen Component': 'Shenzhen Component (CN)',
                    'CSI 300': 'CSI 300 (CN)'
                }
                
                renamed_cols = {}
                for col in self.data.columns:
                    if col in migration_map:
                        renamed_cols[col] = migration_map[col]
                
                if renamed_cols:
                    print(f"Migrating {len(renamed_cols)} columns to new format (adding country codes)...")
                    self.data.rename(columns=renamed_cols, inplace=True)
                
                print(f"Loaded {len(self.data.columns)} indices with {len(self.data)} rows.")
                return self.data
            except Exception as e:
                print(f"Failed to load local file: {e}. Attempting to fetch...")
        
        print(f"Fetching data from {self.start_date} to {self.end_date}")
        print("-" * 50)
        
        # Lazy import to avoid hard dependency if using local data
        try:
            import yfinance as yf
            import akshare as ak
        except ImportError as e:
            print(f"CRITICAL ERROR: Missing dependencies for data fetching ({e}).")
            print(f"Please install requirements or ensure '{csv_file}' exists.")
            if os.path.exists(csv_file):
                print(f"Falling back to local file {csv_file}...")
                self.data = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                return self.data
            return pd.DataFrame()

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
        if px is None or go is None:
            print("Skipping normalized performance plot (Plotly not installed)")
            return

        # Normalize each column from its first valid value
        normalized = pd.DataFrame()
        for col in self.data.columns:
            series = self.data[col].dropna()
            if not series.empty:
                normalized[col] = series / series.iloc[0] * 100
        
        # Set style for professional financial look
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Financial Color Palette (Navy, Gold, White theme)
        colors = [
            '#003366',  # Deep Navy (Primary)
            '#C0B283',  # Muted Gold (Secondary)
            '#2E8B57',  # Sea Green (Success/Growth)
            '#D32F2F',  # Crimson (Risk/Loss)
            '#5D4037',  # Brown (Earth tones)
            '#757575',  # Grey (Neutral)
            '#0288D1',  # Light Blue
            '#7B1FA2',  # Purple
            '#388E3C',  # Dark Green
            '#FBC02D',  # Bright Gold
            '#E64A19',  # Deep Orange
            '#455A64',  # Blue Grey
            '#1976D2',  # Blue
            '#C2185B'   # Pink
        ]
        
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'axes.prop_cycle': plt.cycler(color=colors),
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.color': '#cccccc',
            'text.color': '#333333',
            'axes.labelcolor': '#333333',
            'xtick.color': '#333333',
            'ytick.color': '#333333',
            'legend.frameon': True,
            'legend.facecolor': 'white',
            'legend.edgecolor': '#cccccc',
            'figure.autolayout': True
        })
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
            height=600,
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="#333333"
            ),
            title_font_color="#003366",
            colorway=self.colors
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
        
        if sns:
            sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', vmin=-1, vmax=1, 
                        fmt='.2f', square=True, linewidths=0.5)
        else:
            plt.imshow(corr_matrix, cmap='RdYlGn', vmin=-1, vmax=1)
            plt.colorbar()
            plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
            plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    text = plt.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}",
                                   ha="center", va="center", color="black")
            
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
            'Shanghai Composite (CN)', 'Shenzhen Component (CN)', 'CSI 300 (CN)',
            'Nikkei 225 (JP)', 'S&P/TSX Composite (CA)', 'FTSE Bursa Malaysia KLCI (MY)',
            'CAC 40 (FR)', 'DAX (German)', 'Straits Times Index (SG)', 'S&P/ASX 200 (AU)',
            'S&P 500 (US)', 'NASDAQ Composite (US)', 'FTSE 100 (UK)', 'Hang Seng (HK)'
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
    
    # Market timing cost analysis
    print("\n" + "=" * 60)
    print("MARKET TIMING COST ANALYSIS")
    print("=" * 60)
    try:
        from market_timing_cost import analyze_market_timing_cost
        analyze_market_timing_cost(
            csv_file='market_indices_data.csv',
            index_name='S&P 500 (US)',
            initial_investment=10000
        )
    except Exception as e:
        print(f"Note: Market timing cost analysis skipped - {str(e)}")
    
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
    print("  - market_timing_cost.png (cost of missing best trading days)")
    print("  - market_timing_cost_results.csv (timing cost analysis results)")
