import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="DCF Valuation App", layout="wide")

st.title("DCF Valuation Tool - Global Stocks")

ticker = st.text_input(
    "Enter ticker",
    value="AAPL",
    help="US: AAPL, MSFT | India: RELIANCE.NS, 500325.BO | UK: BP.L, LLOY.L | Europe: SAP.DE, MC.PA, ASML.AS"
)

forecast_years = st.slider("Forecast years", 5, 10, 5)
discount_rate = st.number_input("Discount Rate / WACC (%)", value=10.0) / 100
terminal_growth = st.number_input("Terminal Growth (%)", value=3.0) / 100
margin_of_safety = st.number_input("Margin of Safety (%)", value=20.0) / 100

@st.cache_data(ttl=3600)
def get_currency_conversion_factor(from_curr, to_curr):
    if not from_curr or not to_curr:
        return 1.0
        
    def normalize(c):
        if c in ['GBp', 'GBX', 'GBx', 'gbp', 'gbx']:
            return 'GBP', 100.0
        return c.upper(), 1.0

    from_base, from_mult = normalize(from_curr)
    to_base, to_mult = normalize(to_curr)
    
    if from_base == to_base:
        rate = 1.0
    else:
        ticker_name = f"{from_base}{to_base}=X"
        try:
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            rate = yf.Ticker(ticker_name, session=session).fast_info['last_price']
            if rate is None or np.isnan(rate):
                hist = yf.Ticker(ticker_name, session=session).history(period="1d")
                if not hist.empty:
                    rate = hist["Close"].iloc[-1]
                else:
                    rate = 1.0
        except Exception:
            rate = 1.0
            
    return (1.0 / from_mult) * rate * to_mult

@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    stock = yf.Ticker(ticker, session=session)

    # Check if history is empty to detect invalid/non-existent tickers
    history = stock.history(period="1d")
    if history.empty:
        raise ValueError(
            f"No data found for ticker '{ticker}'. Please append the correct exchange suffix if applicable:\n"
            f"- Indian stocks: append '.NS' (NSE) or '.BO' (BSE) - e.g., 'RELIANCE.NS', '500325.BO'\n"
            f"- UK stocks: append '.L' - e.g., 'BP.L', 'LLOY.L'\n"
            f"- German stocks: append '.DE' - e.g., 'SAP.DE'\n"
            f"- French stocks: append '.PA' - e.g., 'MC.PA'\n"
            f"- Dutch stocks: append '.AS' - e.g., 'ASML.AS'"
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
    financial_currency = info.get("financialCurrency", currency)

    return price, cashflow, balance_sheet, shares, currency, name, financial_currency

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
    price, cashflow, balance_sheet, shares, currency, name, financial_currency = get_stock_data(ticker)

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

    conv_factor = get_currency_conversion_factor(financial_currency, currency)
    if conv_factor != 1.0:
        if operating_cf is not None:
            operating_cf = operating_cf * conv_factor
        if capex is not None:
            capex = capex * conv_factor
        if total_debt is not None:
            total_debt = total_debt * conv_factor
        if cash is not None:
            cash = cash * conv_factor
        st.info(
            f"💱 **Currency Conversion Applied:** Financials are reported in **{financial_currency}**, but the stock trades in **{currency}**. "
            f"Values have been converted at 1 {financial_currency} = {conv_factor:.4f} {currency}."
        )

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
