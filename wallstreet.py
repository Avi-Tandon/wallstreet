import gdown
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import warnings

# Suppress FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define the File IDs and Download the Files
file_ids = {
    'ADANIENT': '1e-LwXV4Xj9-C6iRXmyQO2hWooZMkrUIJ',
    'AXISBANK': '1uuH-la6CfMnywwJUMM0Rb7JxkUB4MePL',
    'BHARTIARTL': '1hjQ26ayOTr2rLv5UEAA9uAxU8NJHe0rk',
    'CIPLA': '1duDhUgT4W45DTlWX5x6dXbm91oxxh9Vf',
    'HINDALCO': '1N6dZCVHkNKFZMwR1HWDqNte9m9uIkDQd',
    'HINDUNILVR': '1_xFEPTXYBnnWoY4PCU4OLpQRzi5ujelM',
    'INFOSYS': '1KQoDpXi-GAa-fDVaFTZHbSXF_PK7FyA9',
    'ITC': '13c5pSyDSLGV1ZibZe7hnJC9oMaa015wt',
    'MARUTI': '11CuuJlpZpxOKaPQNMRjJGDJepehyfHc_',
    'SBIN': '1VcrO8Xgz5aQekM0rOsQdKLio2sjM-_O7',
    'SUNPHARMA': '1b0LrTcRzmV2kUs8ZZ7klq_vyo5zXKq7E',
    'TATASTEEL': '1FHvZG1LeixsXCJOJVsuz8NH_98pU0rsK',
    'WIPRO': '1332HvEpNOZdq7LMkrBFIHCbvkTj0KlWe',
    # Add more file names and their corresponding IDs as needed
}

# Download the Files from Google Drive
for file_name, file_id in file_ids.items():
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, file_name, quiet=False)

# Define a Function to Calculate Technical Indicators and Score Stocks
def calculate_indicators_and_score(file_name):
    # Load data
    data = pd.read_csv(file_name)
    
    # Ensure date is parsed correctly
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    
    # Initialize scores
    score = 0
    
    # Calculate and score RSI
    try:
        data['RSI'] = calculate_rsi(data['Close'])
        avg_rsi = data['RSI'].mean()
        score += avg_rsi  # Simple scoring; refine as needed
    except Exception as e:
        print(f"Error calculating RSI for {file_name}: {e}")
    
    # Calculate and score MACD
    try:
        data['MACD'], data['Signal_Line'] = calculate_macd(data['Close'])
        avg_macd = data['MACD'].mean()
        avg_signal_line = data['Signal_Line'].mean()
        score += avg_macd - avg_signal_line  # Simple scoring; refine as needed
    except Exception as e:
        print(f"Error calculating MACD for {file_name}: {e}")
    
    # Calculate and score Bollinger Bands
    try:
        data['BB_High'], data['BB_Low'] = calculate_bollinger_bands(data['Close'])
        last_close = data['Close'].iloc[-1]
        score += (last_close - data['BB_Low'].iloc[-1]) / (data['BB_High'].iloc[-1] - data['BB_Low'].iloc[-1])
    except Exception as e:
        print(f"Error calculating Bollinger Bands for {file_name}: {e}")
    
    # Calculate and score Parabolic SAR
    try:
        data['Parabolic_SAR'] = calculate_parabolic_sar(data['High'], data['Low'], data['Close'])
        last_sar = data['Parabolic_SAR'].iloc[-1]
        last_close = data['Close'].iloc[-1]
        score += (last_close - last_sar) / last_close
    except Exception as e:
        print(f"Error calculating Parabolic SAR for {file_name}: {e}")
    
    return score, data

# Define custom functions for technical indicators

def calculate_rsi(close_prices, window=14):
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(close_prices, short_window=12, long_window=26, signal_window=9):
    short_ema = close_prices.ewm(span=short_window, adjust=False).mean()
    long_ema = close_prices.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger_bands(close_prices, window=20, num_std_dev=2):
    rolling_mean = close_prices.rolling(window=window).mean()
    rolling_std = close_prices.rolling(window=window).std()
    bollinger_high = rolling_mean + (rolling_std * num_std_dev)
    bollinger_low = rolling_mean - (rolling_std * num_std_dev)
    return bollinger_high, bollinger_low

def calculate_parabolic_sar(high_prices, low_prices, close_prices, step=0.02, max_step=0.2):
    sar = close_prices.copy()
    af = step
    ep = high_prices.iloc[0]
    trend = 1  # 1 for uptrend, -1 for downtrend
    
    for i in range(1, len(close_prices)):
        if trend == 1:
            sar[i] = sar[i-1] + af * (ep - sar[i-1])
            if close_prices[i] > ep:
                ep = close_prices[i]
            if low_prices[i] < sar[i]:
                trend = -1
                sar[i] = ep
                ep = low_prices[i]
                af = step
        else:
            sar[i] = sar[i-1] + af * (ep - sar[i-1])
            if close_prices[i] < ep:
                ep = close_prices[i]
            if high_prices[i] > sar[i]:
                trend = 1
                sar[i] = ep
                ep = high_prices[i]
                af = step
        af = min(af + step, max_step)
    
    return sar

# Calculate scores for each stock
scores = {}
stock_data = {}
for file_name in file_ids.keys():
    score, data = calculate_indicators_and_score(file_name)
    scores[file_name] = score
    stock_data[file_name] = data

# Sort stocks based on scores and select top 3-4
sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
top_stocks = sorted_stocks[:4]

# Print results
print("Top 3-4 Stocks Based on Indicators:")
for stock, score in top_stocks:
    print(f"{stock} with score: {score}")

# Consolidate all plots in a single HTML file
with open("stock_analysis.html", "w") as f:
    for stock in stock_data.keys():
        f.write(f"<h2>{stock}</h2>")
        fig = go.Figure()

        data = stock_data[stock]

        # Calculate and plot RSI
        try:
            fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI'))
        except Exception as e:
            f.write(f"<p>Error plotting RSI for {stock}: {e}</p>")
        
        # Calculate and plot MACD
        try:
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD'))
            fig.add_trace(go.Scatter(x=data.index, y=data['Signal_Line'], mode='lines', name='Signal Line'))
        except Exception as e:
            f.write(f"<p>Error plotting MACD for {stock}: {e}</p>")
        
        # Calculate and plot Bollinger Bands
        try:
            fig.add_trace(go.Scatter(x=data.index, y=data['BB_High'], mode='lines', name='Bollinger High'))
            fig.add_trace(go.Scatter(x=data.index, y=data['BB_Low'], mode='lines', name='Bollinger Low'))
        except Exception as e:
            f.write(f"<p>Error plotting Bollinger Bands for {stock}: {e}</p>")
        
        # Calculate and plot Parabolic SAR
        try:
            fig.add_trace(go.Scatter(x=data.index, y=data['Parabolic_SAR'], mode='markers', name='Parabolic SAR'))
        except Exception as e:
            f.write(f"<p>Error plotting Parabolic SAR for {stock}: {e}</p>")

        fig.update_layout(title=f'Technical Indicators for {stock}', xaxis_title='Date', yaxis_title='Value')

        # Embed plot in HTML
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

print("Analysis complete. Check the 'stock_analysis.html' file for the results.")






