import yfinance as yf
import pandas as pd

def get_live_price(ticker, fallback_price):
    try:
        stock = yf.Ticker(ticker)
        # Handle custom ticker changes (e.g. Tata Motors tracking)
        if ticker == "TATAMOTORS.NS": 
            ticker = "TMCV.NS"
            stock = yf.Ticker(ticker)
            
        df = stock.history(period="1d")
        if not df.empty:
            return round(df['Close'].iloc[-1], 2)
    except:
        pass
    return fallback_price

def generate_financial_plan(available_capital):
    # Base asset metadata with estimated fallback pricing metrics
    asset_catalog = {
        "stocks": [
            {"name": "Reliance Industries", "ticker": "RELIANCE.NS", "base": 1350.0},
            {"name": "Tata Consultancy Services", "ticker": "TCS.NS", "base": 2315.0},
            {"name": "Infosys Ltd", "ticker": "INFY.NS", "base": 1170.0}
        ],
        "etfs": [
            {"name": "Nifty 50 ETF (NIFTYBEES)", "ticker": "NIFTYBEES.NS", "base": 250.0},
            {"name": "Junior Nifty ETF (JUNIORBEES)", "ticker": "JUNIORBEES.NS", "base": 60.0},
            {"name": "Bank Nifty ETF (BANKBEES)", "ticker": "BANKBEES.NS", "base": 510.0}
        ],
        "mutual_funds": [
            {"name": "Parag Parikh Flexi Cap Fund", "min_sip": 1000, "type": "Flexi-Cap"},
            {"name": "Quant Small Cap Fund", "min_sip": 500, "type": "Aggressive Growth"},
            {"name": "HDFC Index Nifty 50 Plan", "min_sip": 100, "type": "Safe Index"}
        ]
    }
    
    plan = {
        "meta": {"total_capital": available_capital, "allocation_strategy": ""},
        "recommendations": []
    }
    
    # ─── STRATEGY ROUTER BASED ON CAPACITIES ───
    if available_capital < 1000:
        plan["meta"]["allocation_strategy"] = "Micro Investment Portfolio (Focus on Fractional Indexing)"
        # Capital too low for individual blue-chip stocks; push micro ETF bundles and low SIP minimums
        for etf in asset_catalog["etfs"]:
            price = get_live_price(etf["ticker"], etf["base"])
            if price <= available_capital:
                max_qty = int(available_capital // price)
                if max_qty > 0:
                    plan["recommendations"].append({
                        "asset_class": "ETF", "name": etf["name"], "ticker": etf["ticker"],
                        "action": f"Buy {max_qty} units", "estimated_cost": round(max_qty * price, 2)
                    })
        for mf in asset_catalog["mutual_funds"]:
            if mf["min_sip"] <= available_capital:
                plan["recommendations"].append({
                    "asset_class": "Mutual Fund Plan", "name": mf["name"], "ticker": "Direct Plan",
                    "action": f"Start Monthly SIP", "estimated_cost": mf["min_sip"]
                })
                
    elif 1000 <= available_capital < 10000:
        plan["meta"]["allocation_strategy"] = "Balanced Growth Portfolio (Mid-Tier Budget)"
        # Allocate 40% Mutual Funds (SIP/Lumpsum), 40% ETFs, 20% Individual Stocks
        allocated_mf = available_capital * 0.40
        allocated_etf = available_capital * 0.40
        allocated_stock = available_capital * 0.20
        
        # Select one high-health stock fitting within individual sub-budget allocation
        for stock in asset_catalog["stocks"]:
            price = get_live_price(stock["ticker"], stock["base"])
            if price <= allocated_stock:
                plan["recommendations"].append({
                    "asset_class": "Stock", "name": stock["name"], "ticker": stock["ticker"],
                    "action": "Buy 1 Share", "estimated_cost": price
                })
                break
        
        # Maximize target ETF liquidity units
        target_etf = asset_catalog["etfs"][0] # Default to main NiftyBees
        etf_price = get_live_price(target_etf["ticker"], target_etf["base"])
        qty = int(allocated_etf // etf_price)
        if qty > 0:
            plan["recommendations"].append({
                "asset_class": "ETF", "name": target_etf["name"], "ticker": target_etf["ticker"],
                "action": f"Buy {qty} Units for Market Stability", "estimated_cost": round(qty * etf_price, 2)
            })

        # Recommend suitable Mutual Fund matching capital allocation constraints
        for mf in asset_catalog["mutual_funds"]:
            if mf["min_sip"] <= allocated_mf:
                plan["recommendations"].append({
                    "asset_class": "Mutual Fund Portfolio", "name": mf["name"], "ticker": "Lump/SIP",
                    "action": "Allocate Capital Reserves", "estimated_cost": round(allocated_mf, 2)
                })
                break
    else:
        plan["meta"]["allocation_strategy"] = "Premium High Alpha Execution Setup"
        # High Budget Capital Configuration Strategy
        for stock in asset_catalog["stocks"]:
            price = get_live_price(stock["ticker"], stock["base"])
            qty = int((available_capital * 0.15) // price) # 15% individual asset limits
            if qty > 0:
                plan["recommendations"].append({
                    "asset_class": "Stock", "name": stock["name"], "ticker": stock["ticker"],
                    "action": f"Buy {qty} Shares", "estimated_cost": round(qty * price, 2)
                })

    return plan

if __name__ == "__main__":
    print("\n--- Asset Strategy Capital Calculation Engine ---")
    try:
        user_input = float(input("Enter available budget amount to simulate (INR/₹): "))
        output = generate_financial_plan(user_input)
        
        print(f"\n🎯 ANALYSIS BASED ON BUDGET MATRIX ({output['meta']['allocation_strategy']}):")
        print("============================================================================")
        for rec in output["recommendations"]:
            print(f"🔹 [{rec['asset_class']}] {rec['name']} ({rec['ticker']}) -> Mode: {rec['action']} | Allocating: ₹{rec['estimated_cost']}")
    except ValueError:
        print("Invalid input value.")
