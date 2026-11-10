import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="DCF Valuation Platform", layout="wide")

st.title("DCF Valuation Platform - Global Stocks")
st.caption(
    "Free cash flow to firm (FCFF) valuation: operating forecast, WACC build-up, terminal value, "
    "equity bridge and sensitivity analysis, using live market and financial statement data."
)

ticker = st.text_input(
    "Enter ticker",
    value="AAPL",
    help="US: AAPL, MSFT | India: RELIANCE.NS, 500325.BO | UK: BP.L, LLOY.L | Europe: SAP.DE, MC.PA, ASML.AS",
).strip().upper()


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def get_currency_conversion_factor(from_curr, to_curr):
    """Factor that converts statement currency into the currency the share trades in."""
    if not from_curr or not to_curr:
        return 1.0

    def normalize(c):
        if c in ["GBp", "GBX", "GBx", "gbp", "gbx"]:
            return "GBP", 100.0
        return c.upper(), 1.0

    from_base, from_mult = normalize(from_curr)
    to_base, to_mult = normalize(to_curr)

    if from_base == to_base:
        rate = 1.0
    else:
        try:
            fx = yf.Ticker(f"{from_base}{to_base}=X")
            rate = fx.fast_info["last_price"]
            if rate is None or np.isnan(rate):
                hist = fx.history(period="1d")
                rate = hist["Close"].iloc[-1] if not hist.empty else 1.0
        except Exception:
            rate = 1.0

    return (1.0 / from_mult) * rate * to_mult


@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    # Let yfinance handle Yahoo's cookies itself (a custom requests session causes 401 errors)
    stock = yf.Ticker(ticker)

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
    except Exception:
        price = history["Close"].iloc[-1]

    # .info is the request Yahoo blocks most often, so treat it as optional
    try:
        info = stock.info
    except Exception:
        info = {}
    if not isinstance(info, dict):
        info = {}

    def fast(key):
        try:
            return stock.fast_info[key]
        except Exception:
            return None

    currency = info.get("currency") or fast("currency") or "N/A"
    return {
        "price": float(price),
        "income": stock.income_stmt,
        "cashflow": stock.cashflow,
        "balance": stock.balance_sheet,
        "shares": info.get("sharesOutstanding") or fast("shares"),
        "currency": currency,
        "financial_currency": info.get("financialCurrency") or currency,
        "name": info.get("longName") or info.get("shortName") or ticker,
        "beta": info.get("beta"),
        "sector": info.get("sector") or "",
    }


def row(statement, names):
    """Return a statement line as a numeric series, newest year first, or None."""
    if statement is None or not hasattr(statement, "index") or statement.empty:
        return None
    for name in names:
        if name in statement.index:
            values = pd.to_numeric(statement.loc[name], errors="coerce").dropna()
            if len(values) > 0:
                return values.sort_index(ascending=False)
    return None


def latest(series, default=0.0):
    return float(series.iloc[0]) if series is not None and len(series) > 0 else default


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def cagr(series):
    """Compound annual growth from the oldest to the latest year."""
    if series is None or len(series) < 2:
        return None
    s = series.sort_index()  # oldest first
    oldest, newest = float(s.iloc[0]), float(s.iloc[-1])
    if oldest <= 0 or newest <= 0:
        return None
    return (newest / oldest) ** (1 / (len(s) - 1)) - 1


def avg_ratio(num, den, default, lo, hi):
    """Average of num/den across the years both are reported, kept within sensible bounds."""
    if num is None or den is None:
        return default
    ratio = (num / den).replace([np.inf, -np.inf], np.nan).dropna()
    if ratio.empty:
        return default
    return clamp(float(ratio.mean()), lo, hi)


# ----------------------------------------------------------------------------
# Valuation engine
# ----------------------------------------------------------------------------
def run_dcf(base_revenue, growth, terminal_growth, years, fade, margin, tax, da, capex, nwc, wacc):
    """Forecast FCFF from revenue and margins, then discount it at the WACC."""
    rows = []
    revenue = base_revenue
    for t in range(1, years + 1):
        if fade and years > 1:
            g = growth + (terminal_growth - growth) * (t - 1) / (years - 1)
        else:
            g = growth
        previous = revenue
        revenue = previous * (1 + g)
        ebit = revenue * margin
        nopat = ebit * (1 - tax)
        d_and_a = revenue * da
        cap = revenue * capex
        nwc_investment = (revenue - previous) * nwc
        fcff = nopat + d_and_a - cap - nwc_investment
        factor = 1 / (1 + wacc) ** t
        rows.append({
            "Year": f"Year {t}", "Revenue": revenue, "Growth": g, "EBIT": ebit, "NOPAT": nopat,
            "D&A": d_and_a, "Capex": cap, "NWC investment": nwc_investment, "FCFF": fcff,
            "Discount factor": factor, "Present value": fcff * factor,
        })
    final_fcff = rows[-1]["FCFF"]
    terminal_value = final_fcff * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** years
    pv_forecast = sum(r["Present value"] for r in rows)
    return {
        "rows": rows, "terminal_value": terminal_value, "pv_terminal": pv_terminal,
        "pv_forecast": pv_forecast, "enterprise_value": pv_forecast + pv_terminal,
    }


def millions(x):
    return f"{x / 1e6:,.0f}m"


# ----------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------
try:
    data = get_stock_data(ticker)
    price, currency = data["price"], data["currency"]
    income, cashflow, balance = data["income"], data["cashflow"], data["balance"]

    st.subheader(data["name"])
    st.metric("Latest Stock Price", f"{price:,.2f} {currency}")

    conv = get_currency_conversion_factor(data["financial_currency"], currency)
    if conv != 1.0:
        st.info(
            f"💱 **Currency conversion applied:** financials are reported in **{data['financial_currency']}**, "
            f"but the stock trades in **{currency}**. Values are converted at "
            f"1 {data['financial_currency']} = {conv:.4f} {currency}."
        )

    def money(series):
        return series * conv if series is not None else None

    # --- Historical statement lines -------------------------------------------------
    revenue = money(row(income, ["Total Revenue", "Operating Revenue"]))
    ebit = money(row(income, ["Operating Income", "EBIT"]))
    d_and_a = money(row(cashflow, ["Depreciation And Amortization", "Depreciation Amortization Depletion"]))
    if d_and_a is None:
        d_and_a = money(row(income, ["Reconciled Depreciation"]))
    capex_hist = money(row(cashflow, ["Capital Expenditure", "Capital Expenditures"]))
    capex_hist = capex_hist.abs() if capex_hist is not None else None
    wc_change = money(row(cashflow, ["Change In Working Capital"]))
    op_cf = money(row(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"]))

    if revenue is None or ebit is None:
        st.error(
            "Revenue or operating profit is not available for this company, so an FCFF valuation cannot be built. "
            "Banks, insurers and some funds do not report these lines."
        )
        st.stop()

    if "financial" in data["sector"].lower():
        st.warning(
            "This is a financial company. FCFF DCF is not well suited to banks and insurers, because debt is part "
            "of their operations. Treat the result with caution."
        )

    # --- Defaults taken from the company's own history -------------------------------
    hist_growth = cagr(revenue)
    default_growth = clamp(hist_growth, -0.05, 0.20) if hist_growth is not None else 0.05
    default_margin = avg_ratio(ebit, revenue, 0.15, -0.20, 0.60)
    default_da = avg_ratio(d_and_a, revenue, 0.03, 0.0, 0.30)
    default_capex = avg_ratio(capex_hist, revenue, 0.04, 0.0, 0.40)

    default_nwc = 0.05
    if wc_change is not None and len(revenue) >= 2:
        rev_increase = (revenue - revenue.shift(-1)).dropna()  # newest first
        common = rev_increase.index.intersection(wc_change.index)
        if len(common) > 0 and rev_increase[common].sum() > 0:
            default_nwc = clamp(float(-wc_change[common].sum() / rev_increase[common].sum()), -0.20, 0.30)

    tax_series = row(income, ["Tax Rate For Calcs"])
    if tax_series is not None:
        default_tax = clamp(latest(tax_series), 0.0, 0.40)
    else:
        default_tax = avg_ratio(row(income, ["Tax Provision"]), row(income, ["Pretax Income"]), 0.25, 0.0, 0.40)

    # --- Equity bridge items ---------------------------------------------------------
    cash = money(row(balance, ["Cash Cash Equivalents And Short Term Investments"]))
    if cash is not None:
        cash_value = latest(cash)
    else:
        cash_value = latest(money(row(balance, ["Cash And Cash Equivalents"]))) + latest(
            money(row(balance, ["Other Short Term Investments"]))
        )

    debt = money(row(balance, ["Total Debt"]))
    if debt is not None:
        debt_value = latest(debt)
    else:
        long_debt = money(row(balance, ["Long Term Debt And Capital Lease Obligation", "Long Term Debt"]))
        short_debt = money(row(balance, ["Current Debt And Capital Lease Obligation", "Current Debt"]))
        debt_value = latest(long_debt) + latest(short_debt)
        if long_debt is None and short_debt is None:
            st.warning("No debt figure was found for this company, so debt is treated as zero.")

    minority_value = latest(money(row(balance, ["Minority Interest"])))
    preferred_value = latest(money(row(balance, ["Preferred Stock"])))

    shares = data["shares"] or latest(row(income, ["Diluted Average Shares", "Basic Average Shares"]), None)
    if not shares:
        st.error("Shares outstanding data not available.")
        st.stop()

    market_cap = price * shares
    interest = money(row(income, ["Interest Expense", "Interest Expense Non Operating"]))
    default_kd = 0.055
    if interest is not None and debt_value > 0:
        default_kd = clamp(abs(latest(interest)) / debt_value, 0.02, 0.12)
    default_beta = clamp(float(data["beta"]), 0.3, 2.5) if data["beta"] else 1.0

    # --- Assumptions (sidebar; keyed by ticker so they reset for each company) -------
    k = ticker
    sb = st.sidebar
    sb.header("Assumptions")
    sb.caption("Defaults come from the company's reported history. Change any of them.")

    sb.subheader("Operating forecast")
    years = sb.slider("Forecast years", 5, 10, 5)
    growth = sb.number_input("Revenue growth, year 1 (%)", value=round(default_growth * 100, 1), step=0.5, key=f"{k}_g") / 100
    fade = sb.checkbox("Fade growth to the terminal rate by the final year", value=True)
    margin = sb.number_input("EBIT margin (%)", value=round(default_margin * 100, 1), step=0.5, key=f"{k}_m") / 100
    tax = sb.number_input("Tax rate (%)", value=round(default_tax * 100, 1), step=0.5, key=f"{k}_t") / 100
    da_pct = sb.number_input("D&A (% of revenue)", value=round(default_da * 100, 1), step=0.5, key=f"{k}_da") / 100
    capex_pct = sb.number_input("Capex (% of revenue)", value=round(default_capex * 100, 1), step=0.5, key=f"{k}_cx") / 100
    nwc_pct = sb.number_input(
        "Working capital investment (% of revenue increase)", value=round(default_nwc * 100, 1), step=0.5, key=f"{k}_nwc"
    ) / 100

    sb.subheader("Discount rate")
    wacc_mode = sb.radio("WACC", ["Build from CAPM", "Enter manually"])
    if wacc_mode == "Build from CAPM":
        rf = sb.number_input(
            "Risk-free rate (%)", value=4.5, step=0.1,
            help="Use the 10-year government bond yield for the company's currency.",
        ) / 100
        beta = sb.number_input("Beta", value=round(default_beta, 2), step=0.05, key=f"{k}_b")
        erp = sb.number_input("Equity risk premium (%)", value=5.0, step=0.1) / 100
        kd = sb.number_input("Pre-tax cost of debt (%)", value=round(default_kd * 100, 1), step=0.1, key=f"{k}_kd") / 100
        cost_of_equity = rf + beta * erp
        total_capital = market_cap + debt_value
        w_e = market_cap / total_capital if total_capital > 0 else 1.0
        w_d = 1 - w_e
        wacc = w_e * cost_of_equity + w_d * kd * (1 - tax)
    else:
        wacc = sb.number_input("Discount rate / WACC (%)", value=10.0, step=0.25) / 100

    sb.subheader("Terminal value and margin of safety")
    terminal_growth = sb.number_input("Terminal growth (%)", value=2.5, step=0.25) / 100
    margin_of_safety = sb.number_input("Margin of safety (%)", value=20.0, step=1.0) / 100

    if wacc <= terminal_growth:
        st.error(
            f"WACC ({wacc * 100:.2f}%) must be higher than terminal growth ({terminal_growth * 100:.2f}%). "
            "Otherwise the terminal value formula has no meaning. Raise the WACC or lower the terminal growth rate."
        )
        st.stop()

    # --- Valuation -------------------------------------------------------------------
    base_revenue = latest(revenue)

    def value_per_share(w, g):
        result = run_dcf(base_revenue, growth, g, years, fade, margin, tax, da_pct, capex_pct, nwc_pct, w)
        equity = result["enterprise_value"] + cash_value - debt_value - minority_value - preferred_value
        return equity / shares, equity, result

    intrinsic_value, equity_value, dcf = value_per_share(wacc, terminal_growth)
    mos_price = intrinsic_value * (1 - margin_of_safety)
    upside = (intrinsic_value / price - 1) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Intrinsic Value", f"{intrinsic_value:,.2f} {currency}")
    col2.metric("MOS Buy Price", f"{mos_price:,.2f} {currency}")
    col3.metric("Upside / Downside", f"{upside:,.2f}%")
    col4.metric("WACC", f"{wacc * 100:.2f}%")

    if dcf["rows"][-1]["FCFF"] <= 0:
        st.warning(
            "Free cash flow is negative in the final forecast year, so the terminal value is negative. "
            "Review the margin, capex and growth assumptions."
        )

    if wacc_mode == "Build from CAPM":
        st.subheader("WACC Build-up")
        st.dataframe(pd.DataFrame({
            "Component": [
                "Risk-free rate", "Beta", "Equity risk premium", "Cost of equity (CAPM)",
                "Pre-tax cost of debt", "After-tax cost of debt", "Weight of equity", "Weight of debt", "WACC",
            ],
            "Value": [
                f"{rf * 100:.2f}%", f"{beta:.2f}", f"{erp * 100:.2f}%", f"{cost_of_equity * 100:.2f}%",
                f"{kd * 100:.2f}%", f"{kd * (1 - tax) * 100:.2f}%", f"{w_e * 100:.1f}%", f"{w_d * 100:.1f}%",
                f"{wacc * 100:.2f}%",
            ],
        }), hide_index=True)

    st.subheader(f"Operating Forecast and Free Cash Flow ({currency} millions)")
    forecast_table = pd.DataFrame(dcf["rows"]).set_index("Year")
    money_cols = ["Revenue", "EBIT", "NOPAT", "D&A", "Capex", "NWC investment", "FCFF", "Present value"]
    shown = forecast_table.copy()
    shown[money_cols] = (shown[money_cols] / 1e6).round(0)
    shown["Growth"] = (shown["Growth"] * 100).round(1).astype(str) + "%"
    shown["Discount factor"] = shown["Discount factor"].round(3)
    st.dataframe(shown)
    st.caption("FCFF = EBIT x (1 - tax rate) + D&A - capex - investment in working capital.")

    st.subheader("Valuation Summary")
    tv_share = dcf["pv_terminal"] / dcf["enterprise_value"] * 100 if dcf["enterprise_value"] else 0
    st.dataframe(pd.DataFrame({
        "Item": [
            "Present value of forecast FCFF", "Present value of terminal value", "Enterprise value",
            "Plus: cash and short-term investments", "Less: total debt", "Less: minority interest",
            "Less: preferred stock", "Equity value", "Shares outstanding", "Intrinsic value per share",
        ],
        "Value": [
            millions(dcf["pv_forecast"]), millions(dcf["pv_terminal"]), millions(dcf["enterprise_value"]),
            millions(cash_value), millions(debt_value), millions(minority_value), millions(preferred_value),
            millions(equity_value), millions(shares), f"{intrinsic_value:,.2f} {currency}",
        ],
    }), hide_index=True)
    st.caption(
        f"Terminal value is {tv_share:.0f}% of enterprise value. Terminal value = final year FCFF x (1 + g) / (WACC - g)."
    )

    st.subheader(f"Sensitivity: Intrinsic Value per Share ({currency})")
    wacc_range = [wacc + d for d in (-0.01, -0.005, 0, 0.005, 0.01)]
    growth_range = [terminal_growth + d for d in (-0.01, -0.005, 0, 0.005, 0.01)]
    sensitivity = pd.DataFrame(
        [[value_per_share(w, g)[0] if w > g else np.nan for g in growth_range] for w in wacc_range],
        index=[f"WACC {w * 100:.2f}%" for w in wacc_range],
        columns=[f"g {g * 100:.2f}%" for g in growth_range],
    ).round(2)
    st.dataframe(sensitivity)
    st.caption("Rows change the WACC and columns change the terminal growth rate. The middle cell is the base case.")

    st.subheader(f"Historical Financials ({currency} millions)")
    history_table = pd.DataFrame({
        "Revenue": revenue, "EBIT": ebit, "D&A": d_and_a, "Capex": capex_hist, "Operating cash flow": op_cf,
    })
    if op_cf is not None and capex_hist is not None:
        history_table["Free cash flow"] = op_cf - capex_hist
    history_table = (history_table.sort_index(ascending=False) / 1e6).round(0)
    history_table["EBIT margin"] = ((ebit / revenue) * 100).round(1).astype(str) + "%"
    history_table.index = [getattr(i, "year", i) for i in history_table.index]
    st.dataframe(history_table)
    if hist_growth is not None:
        st.caption(f"Historical revenue growth (CAGR): {hist_growth * 100:.1f}%.")

    st.caption("For education and research only. This is not investment advice.")

except Exception as e:
    st.error(f"Error: {e}")
