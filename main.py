from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

# Enable CORS so your Lovable front end can securely read this data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_live_price(ticker, fallback_price):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1d")
        if not df.empty:
            return round(df['Close'].iloc[-1], 2)
    except:
        pass
    return fallback_price

# 🟢 NEW ROOT ROUTE: This handles the basic home URL directly!
@app.get("/")
def home_allocation(capital: float = 5000.0):
    # Updated ticker list reflecting the modern NSE ticker symbols
    asset_catalog = {
        "stocks": [
            {"name": "Reliance Industries", "ticker": "RELIANCE.NS", "base": 1350.0},
            {"name": "Tata Consumer / Passenger", "ticker": "TMPV.NS", "base": 355.0},
            {"name": "Infosys Ltd", "ticker": "INFY.NS", "base": 1170.0}
        ],
        "etfs": [
            {"name": "Nifty 50 ETF (NIFTYBEES)", "ticker": "NIFTYBEES.NS", "base": 250.0},
            {"name": "Junior Nifty ETF (JUNIORBEES)", "ticker": "JUNIORBEES.NS", "base": 60.0},
            {"name": "Bank Nifty ETF (BANKBEES)", "ticker": "BANKBEES.NS", "base": 510.0}
        ],
        "mutual_funds": [
            {"name": "Parag Parikh Flexi Cap Fund", "min_sip": 1000},
            {"name": "Quant Small Cap Fund", "min_sip": 500},
            {"name": "HDFC Index Nifty 50 Plan", "min_sip": 100}
        ]
    }
    
    recommendations = []
    
    if capital < 1000:
        strategy = "Micro Investment Plan"
        for etf in asset_catalog["etfs"]:
            price = get_live_price(etf["ticker"], etf["base"])
            if price <= capital:
                qty = int(capital // price)
                if qty > 0:
                    recommendations.append({"type": "ETF", "name": etf["name"], "action": f"Buy {qty} Units", "cost": round(qty * price, 2)})
        for mf in asset_catalog["mutual_funds"]:
            if mf["min_sip"] <= capital:
                recommendations.append({"type": "Mutual Fund", "name": mf["name"], "action": "Start Monthly SIP", "cost": mf["min_sip"]})
                
    else:
        strategy = "Balanced Allocation Plan"
        # 40% Stocks, 30% ETFs, 30% Mutual Funds
        alloc_stock = capital * 0.40
        alloc_etf = capital * 0.30
        alloc_mf = capital * 0.30
        
        for stock in asset_catalog["stocks"]:
            price = get_live_price(stock["ticker"], stock["base"])
            qty = int(alloc_stock // price)
            if qty > 0:
                recommendations.append({"type": "Stock", "name": stock["name"], "action": f"Buy {qty} Shares", "cost": round(qty * price, 2)})
                
        for etf in asset_catalog["etfs"]:
            price = get_live_price(etf["ticker"], etf["base"])
            qty = int(alloc_etf // price)
            if qty > 0:
                recommendations.append({"type": "ETF", "name": etf["name"], "action": f"Buy {qty} Units", "cost": round(qty * price, 2)})
                
        for mf in asset_catalog["mutual_funds"]:
            if mf["min_sip"] <= alloc_mf:
                recommendations.append({"type": "Mutual Fund", "name": mf["name"], "action": "Lumpsum Deposit", "cost": round(alloc_mf, 2)})
                break

    return {"strategy": strategy, "recommendations": recommendations}
