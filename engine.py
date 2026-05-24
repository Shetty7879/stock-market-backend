import yfinance as yf
import pandas as pd

def analyze_stocks(ticker_list):
    results = {"long_term": [], "short_term": [], "intraday": []}
    
    for ticker in ticker_list: 
        try:
            print(f"Analyzing data for {ticker}...")
            stock = yf.Ticker(ticker)
            
            # --- Fetch historical daily data for analysis ---
            df_daily = stock.history(period="6mo", interval="1d")
            if df_daily.empty or len(df_daily) < 20: 
                continue
                
            info = stock.info
            current_price = round(df_daily['Close'].iloc[-1], 2)
            
            # --- 🟢 ENGINE A: LONG TERM LOGIC (Fundamental Analysis) ---
            debt_to_equity = info.get("debtToEquity", 150)  # Fallback if missing
            profit_margin = info.get("profitMargins", 0)
            
            # Check for structurally safe, profitable companies
            if debt_to_equity < 100 and profit_margin > 0.05:
                results["long_term"].append({
                    "ticker": ticker, 
                    "price": current_price,
                    "status": "Safe Structure"
                })
                
            # --- 🟡 ENGINE B: SHORT TERM LOGIC (Daily Momentum) ---
            # Native Pandas implementation of a 14-period Relative Strength Index (RSI)
            delta = df_daily['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df_daily['RSI_14'] = 100 - (100 / (1 + rs))
            
            current_rsi = df_daily['RSI_14'].iloc[-1]
            
            # Check for buyer momentum breakout
            if not pd.isna(current_rsi) and current_rsi > 55:
                results["short_term"].append({
                    "ticker": ticker, 
                    "price": current_price, 
                    "rsi": round(current_rsi, 2)
                })
                
            # --- 🔴 ENGINE C: INTRADAY LOGIC (Volume Weighted Actions) ---
            # Native Pandas implementation of VWAP using typical price and volume matrices
            typical_price = (df_daily['High'] + df_daily['Low'] + df_daily['Close']) / 3
            df_daily['VWAP'] = (typical_price * df_daily['Volume']).cumsum() / df_daily['Volume'].cumsum()
            current_vwap = df_daily['VWAP'].iloc[-1]
            
            # Buy signal if current market price exceeds the rolling volume weighted baseline
            if current_price > current_vwap:
                results["intraday"].append({
                    "ticker": ticker, 
                    "price": current_price,
                    "status": "Above VWAP"
                })
                    
        except Exception as e:
            print(f"Skipping {ticker} due to data handling lag: {e}")
            
    return results

if __name__ == "__main__":
    sample_basket = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "TMPV.NS"]
    print("\n--- Running Custom Mathematics Stock Screening Calculation Engine ---")
    output = analyze_stocks(sample_basket)
    
    print("\n🎯 RUNTIME VERIFICATION MATRIX:")
    print("====================================")
    print("🟢 Long Term Targets:", output["long_term"])
    print("🟡 Short Term Breakouts:", output["short_term"])
    print("🔴 Intraday Live Spikes:", output["intraday"])
