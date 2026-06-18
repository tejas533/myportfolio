import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="DCF Valuation App", layout="wide")

st.title("DCF Valuation Tool - US & Indian Stocks")

ticker = st.text_input(
    "Enter ticker",
    value="AAPL",
    help="US: AAPL, MSFT, TSLA | India NSE: RELIANCE.NS, TCS.NS, INFY.NS | BSE: 500325.BO"
)

forecast_years = st.slider("Forecast years", 5, 10, 5)
discount_rate = st.number_input("Discount Rate / WACC (%)", value=10.0) / 100
terminal_growth = st.number_input("Terminal Growth (%)", value=3.0) / 100
margin_of_safety = st.number_input("Margin of Safety (%)", value=20.0) / 100

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)

    # Check if history is empty to detect invalid/non-existent tickers
    history = stock.history(period="1d")
    if history.empty:
        raise ValueError(
            f"No data found for ticker '{ticker}'. For Indian stocks, please append '.NS' (NSE) or '.BO' (BSE) - e.g., 'RELIANCE.NS', 'TCS.NS', or '500180.BO'."
        )

    try:
        price = stock.fast_info["last_price"]
        if price is None or np.isnan(price):
            price = history["Close"].iloc[-1]
    except:
        price = history["Close"].iloc[-1]

    cashflow = stock.cashflow
    balance_sheet = stock.balance_sheet
    info = stock.info

    if not isinstance(info, dict):
        info = {}

    shares = info.get("sharesOutstanding", None)
    currency = info.get("currency", "N/A")
    name = info.get("longName", ticker)

    return stock, price, cashflow, balance_sheet, shares, currency, name

def safe_get_statement_value(statement, possible_names):
    if statement is None or not hasattr(statement, "index") or statement.empty:
        return None
    for name in possible_names:
        if name in statement.index:
            values = statement.loc[name].dropna()
            if len(values) > 0:
                return values
    return None

def calculate_reasonable_growth(fcf_series):
    fcf_series = fcf_series.sort_index()

    if len(fcf_series) < 2:
        return 0.05

    oldest = fcf_series.iloc[-1]
    latest = fcf_series.iloc[0]

    if oldest <= 0 or latest <= 0:
        return 0.03

    historical_cagr = (latest / oldest) ** (1 / (len(fcf_series) - 1)) - 1

    historical_cagr = max(min(historical_cagr, 0.18), -0.05)

    return historical_cagr

def forecast_fcf(latest_fcf, oldest_fcf, years, growth_rate):
    forecast = []

    if latest_fcf < oldest_fcf:
        recovery_gap = oldest_fcf - latest_fcf
        annual_recovery = recovery_gap / years

        for year in range(1, years + 1):
            recovered_base = latest_fcf + annual_recovery * year
            value = recovered_base * ((1 + max(growth_rate, 0.02)) ** year)
            forecast.append(value)
    else:
        for year in range(1, years + 1):
            value = latest_fcf * ((1 + growth_rate) ** year)
            forecast.append(value)

    return forecast

try:
    stock, price, cashflow, balance_sheet, shares, currency, name = get_stock_data(ticker)

    st.subheader(f"{name}")
    st.metric("Latest Stock Price", f"{price:.2f} {currency}")

    operating_cf = safe_get_statement_value(
        cashflow,
        ["Operating Cash Flow", "Total Cash From Operating Activities"]
    )

    capex = safe_get_statement_value(
        cashflow,
        ["Capital Expenditure", "Capital Expenditures"]
    )

    total_debt = safe_get_statement_value(
        balance_sheet,
        ["Total Debt", "Long Term Debt", "Total Liabilities Net Minority Interest"]
    )

    cash = safe_get_statement_value(
        balance_sheet,
        ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]
    )

    if operating_cf is None or capex is None:
        st.error("Cash flow data not available for this company.")
        st.stop()

    fcf = operating_cf + capex
    fcf = fcf.dropna()

    latest_fcf = fcf.iloc[0]
    oldest_fcf = fcf.iloc[-1]

    growth_rate = calculate_reasonable_growth(fcf)
    forecast = forecast_fcf(latest_fcf, oldest_fcf, forecast_years, growth_rate)

    discount_factors = [(1 / ((1 + discount_rate) ** year)) for year in range(1, forecast_years + 1)]
    present_values = [forecast[i] * discount_factors[i] for i in range(forecast_years)]

    terminal_value = forecast[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    terminal_pv = terminal_value / ((1 + discount_rate) ** forecast_years)

    enterprise_value = sum(present_values) + terminal_pv

    latest_cash = cash.iloc[0] if cash is not None else 0
    latest_debt = total_debt.iloc[0] if total_debt is not None else 0

    equity_value = enterprise_value + latest_cash - latest_debt

    if shares is None or shares == 0:
        st.error("Shares outstanding data not available.")
        st.stop()

    intrinsic_value = equity_value / shares
    mos_price = intrinsic_value * (1 - margin_of_safety)

    upside = (intrinsic_value / price - 1) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Intrinsic Value", f"{intrinsic_value:.2f} {currency}")
    col2.metric("MOS Buy Price", f"{mos_price:.2f} {currency}")
    col3.metric("Upside / Downside", f"{upside:.2f}%")

    st.subheader("DCF Forecast")

    dcf_table = pd.DataFrame({
        "Year": [f"Year {i}" for i in range(1, forecast_years + 1)],
        "Forecast FCF": forecast,
        "Discount Factor": discount_factors,
        "Present Value": present_values
    })

    st.dataframe(dcf_table)

    st.subheader("Historical Free Cash Flow")

    hist_table = pd.DataFrame({
        "Free Cash Flow": fcf
    })

    st.dataframe(hist_table)

    st.subheader("Valuation Summary")

    st.write(f"""
    Latest FCF used: {latest_fcf:,.0f} {currency}

    Oldest FCF used: {oldest_fcf:,.0f} {currency}

    Reasonable growth rate used: {growth_rate * 100:.2f}%

    Enterprise Value: {enterprise_value:,.0f} {currency}

    Cash: {latest_cash:,.0f} {currency}

    Debt: {latest_debt:,.0f} {currency}

    Equity Value: {equity_value:,.0f} {currency}
    """)

except Exception as e:
    st.error(f"Error: {e}")
