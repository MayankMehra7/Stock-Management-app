import streamlit as st
import yfinance as yf
import pandas as pd

# Custom CSS for background image and other styles
st.markdown(
    f"""
    <style>
    /* Background image */
    .stApp {{
        background-image: url("file://C:/Users/mayan/Downloads/download (1).jpeg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Increase the font size of the table */
    .dataframe td, .dataframe th {{
        font-size: 18px !important;
        padding: 10px !important;
    }}
    
    /* Increase the header font size */
    .dataframe th {{
        font-size: 20px !important;
    }}
    
    /* Set text color for better visibility */
    .stApp, .dataframe th, .dataframe td {{
        color: #fff;
    }}
    </style>
    """, unsafe_allow_html=True
)

def calculate_max_profit(prices):
    min_price = float('inf')
    max_profit = 0
    buy_day = 0
    sell_day = 0

    for i in range(len(prices)):
        if prices[i] < min_price:
            min_price = prices[i]
            buy_day = i
        elif prices[i] - min_price > max_profit:
            max_profit = prices[i] - min_price
            sell_day = i

    return buy_day, sell_day, max_profit

def fetch_stock_data(ticker, period='max'):
    stock_data = yf.download(ticker, period=period)
    close_prices = stock_data['Close'].tolist()
    return close_prices, stock_data.index

def suggest_stock_actions(tickers, available_cash):
    num_stocks = len(tickers)
    cash_per_stock = available_cash / num_stocks
    recommendations = []
    
    total_shares = 0
    total_investment = 0
    total_value = 0

    for ticker in tickers:
        try:
            prices, dates = fetch_stock_data(ticker)
            if prices:
                buy_day, sell_day, profit = calculate_max_profit(prices)
                buy_date = dates[buy_day].strftime('%Y-%m-%d')
                sell_date = dates[sell_day].strftime('%Y-%m-%d')
                buy_price = prices[buy_day]
                sell_price = prices[sell_day]
                
                shares_to_buy = int(cash_per_stock // buy_price)
                investment = shares_to_buy * buy_price
                value = shares_to_buy * sell_price
                profit = value - investment
                
                recommendations.append({
                    'Ticker': ticker,
                    'Buy Date': buy_date,
                    'Buy Price': buy_price,
                    'Sell Date': sell_date,
                    'Sell Price': sell_price,
                    'Cash Allocated': cash_per_stock,
                    'Shares to Buy': shares_to_buy,
                    'Total Investment': investment,
                    'Total Value': value,
                    'Profit': profit
                })
                
                total_shares += shares_to_buy
                total_investment += investment
                total_value += value
            else:
                recommendations.append({
                    'Ticker': ticker,
                    'Buy Date': None,
                    'Buy Price': None,
                    'Sell Date': None,
                    'Sell Price': None,
                    'Cash Allocated': None,
                    'Shares to Buy': None,
                    'Total Investment': None,
                    'Total Value': None,
                    'Profit': None
                })
        except Exception as e:
            st.write(f"Error processing {ticker}: {e}")
            recommendations.append({
                'Ticker': ticker,
                'Buy Date': None,
                'Buy Price': None,
                'Sell Date': None,
                'Sell Price': None,
                'Cash Allocated': None,
                'Shares to Buy': None,
                'Total Investment': None,
                'Total Value': None,
                'Profit': None
            })

    totals = pd.DataFrame([{
        'Ticker': 'Total',
        'Buy Date': '',
        'Buy Price': '',
        'Sell Date': '',
        'Sell Price': '',
        'Cash Allocated': available_cash,
        'Shares to Buy': total_shares,
        'Total Investment': total_investment,
        'Total Value': total_value,
        'Profit': total_value - total_investment
    }])
    
    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df = pd.concat([recommendations_df, totals], ignore_index=True)

    return recommendations_df

# Streamlit app
st.title('Stock Investment Suggestion App')

# User input for available cash
cash = st.number_input('Enter the amount of cash you have (in INR):', min_value=0.0, step=1000.0)

# List of stock tickers (Indian stocks)
tickers = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
    "KOTAKBANK.NS", "AXISBANK.NS", "WIPRO.NS", "ITC.NS", "SBIN.NS", 
    "YESBANK.NS", "EQUITAS.NS", "BAJAJFINSV.NS", "HDFCLIFE.NS", 
    "PNB.NS", "UNIONBANK.NS", "BANKBARODA.NS", "RBLBANK.NS", 
    "TATASTEEL.NS", "NHPC.NS", "ONGC.NS", "IOC.NS", "BPCL.NS"
]

if cash > 0:
    recommendations_df = suggest_stock_actions(tickers, cash)
    st.subheader('Investment Suggestions')
    st.dataframe(recommendations_df)
    
    # Option to download recommendations as a CSV file
    csv = recommendations_df.to_csv(index=False)
    st.download_button(label="Download Recommendations as CSV", data=csv, file_name='stock_recommendations.csv', mime='text/csv')
else:
    st.write('Please enter a valid amount of cash.')
