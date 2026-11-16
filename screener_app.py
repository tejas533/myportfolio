"""Hidden Compounders Screener - find niche Indian small and mid caps by your own metrics.

Run locally:   streamlit run screener_app.py
Deploy:        push this file and requirements.txt to GitHub, then create a new app on Streamlit Community Cloud.
"""
import json
import math

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hidden Compounders Screener", page_icon="📈", layout="wide")

YEARS = ["FY23", "FY24", "FY25", "FY26"]
CURATED = json.loads(r'''[
 {
  "n": "CARE Ratings",
  "t": "CARERATING",
  "moat": "Oligopoly",
  "cap": 4770,
  "pe": 24.7,
  "roce": 26.3,
  "sales": [
   279,
   332,
   402,
   473
  ],
  "np": 174,
  "bor": 26,
  "res": 902,
  "assets": [
   770,
   842,
   958,
   1105
  ],
  "cfo": [
   82,
   91,
   123,
   148
  ],
  "model": "Credit rating agency. Companies pay a fee to get their bank loans and bonds rated, then an annual surveillance fee for as long as the debt is outstanding.",
  "drivers": [
   "Corporate bond issuance and bank credit growth",
   "Recurring surveillance fees on already-rated debt",
   "Analytics and advisory arms, plus rating subsidiaries overseas"
  ],
  "watch": "Earnings follow the credit cycle; a slow year for bond issuance hits new-rating fees.",
  "src": "https://www.screener.in/company/CARERATING/consolidated/"
 },
 {
  "n": "ICRA",
  "t": "ICRA",
  "moat": "Oligopoly",
  "cap": 4346,
  "pe": 21.6,
  "roce": 23,
  "sales": [
   403,
   446,
   498,
   600
  ],
  "np": 183,
  "bor": 18,
  "res": 1171,
  "assets": [
   1101,
   1184,
   1292,
   1481
  ],
  "cfo": [
   99,
   107,
   145,
   157
  ],
  "model": "Moody's-backed credit rating agency. Earns rating and surveillance fees, and runs ICRA Analytics, which sells research, data and outsourced analytics work.",
  "drivers": [
   "Debt issuance and bank lending volumes",
   "Surveillance fees on the existing rated book",
   "Analytics and knowledge services for the Moody's group and banks"
  ],
  "watch": "Growth was only just above 10% in two of the last three years.",
  "src": "https://www.screener.in/company/ICRA/consolidated"
 },
 {
  "n": "eMudhra",
  "t": "EMUDHRA",
  "moat": "Oligopoly",
  "cap": 2931,
  "pe": 23.9,
  "roce": 15.7,
  "sales": [
   249,
   373,
   519,
   702
  ],
  "np": 110,
  "bor": 29,
  "res": 870,
  "assets": [
   460,
   750,
   868,
   1213
  ],
  "cfo": [
   34,
   73,
   102,
   133
  ],
  "model": "India's largest licensed issuer of digital signature certificates. Sells certificates through partners and sells identity, e-sign and encryption software to enterprises.",
  "drivers": [
   "Certificate volumes from tax, company-law and tender filings",
   "Enterprises moving to paperless signing and digital identity",
   "Overseas expansion, partly through acquisitions"
  ],
  "watch": "Net margin is 15.7%, barely over your line, and part of the growth is bought through acquisitions.",
  "src": "https://screener.in/company/EMUDHRA/consolidated"
 },
 {
  "n": "SJS Enterprises",
  "t": "SJS",
  "moat": "Niche",
  "cap": 6776,
  "pe": 33,
  "roce": 28.6,
  "sales": [
   433,
   628,
   760,
   955
  ],
  "np": 172,
  "bor": 23,
  "res": 836,
  "assets": [
   537,
   785,
   868,
   1101
  ],
  "cfo": [
   87,
   109,
   163,
   224
  ],
  "model": "Makes the decorative parts on vehicles and appliances: logos, decals, chrome-plated trim, in-mould parts and display cover glass. Supplies directly to two-wheeler, car and appliance makers. The closest match to Pricol on this list.",
  "drivers": [
   "More decorative content per vehicle as models go premium",
   "Growing share with passenger-car makers",
   "New products such as cover glass for dashboards, plus exports"
  ],
  "watch": "Tied to auto production volumes; a small number of large customers.",
  "src": "https://www.screener.in/company/SJS/consolidated/"
 },
 {
  "n": "Latent View Analytics",
  "t": "LATENTVIEW",
  "moat": "Niche",
  "cap": 4177,
  "pe": 20.9,
  "roce": 15.8,
  "sales": [
   539,
   641,
   848,
   1060
  ],
  "np": 202,
  "bor": 33,
  "res": 1735,
  "assets": [
   1263,
   1456,
   1789,
   2083
  ],
  "cfo": [
   97,
   115,
   130,
   165
  ],
  "model": "Pure-play data analytics firm. Bills large US technology, finance and consumer companies for analytics, data engineering and AI projects.",
  "drivers": [
   "Data and AI budgets of a few very large clients",
   "Selling more services into existing accounts",
   "Acquisitions that add new industries"
  ],
  "watch": "A services business with heavy dependence on its top clients, so the moat is thin.",
  "src": "https://www.screener.in/company/LATENTVIEW/consolidated/"
 },
 {
  "n": "Supriya Lifescience",
  "t": "SUPRIYA",
  "moat": "Niche",
  "cap": 6935,
  "pe": 33,
  "roce": 25,
  "sales": [
   461,
   570,
   696,
   828
  ],
  "np": 209,
  "bor": 5,
  "res": 1182,
  "assets": [
   820,
   921,
   1117,
   1357
  ],
  "cfo": [
   64,
   113,
   165,
   186
  ],
  "model": "Makes active drug ingredients in a few molecules where it is among the largest suppliers worldwide, such as anti-allergy, anaesthetic and asthma drugs. Mostly exported.",
  "drivers": [
   "Share gains in regulated markets like Europe and the US",
   "New molecules and contract manufacturing deals",
   "New capacity coming on stream"
  ],
  "watch": "Drug ingredients are the nearest thing to a commodity on this list. Market cap is from a different source (28 Oct 2026) and P/E is worked out on FY26 profit.",
  "src": "https://www.screener.in/company/SUPRIYA/consolidated/"
 },
 {
  "n": "Sika Interplant Systems",
  "t": "SIKA",
  "moat": "Niche",
  "cap": 1873,
  "pe": 54.6,
  "roce": 34.6,
  "sales": [
   60,
   106,
   148,
   211
  ],
  "np": 36,
  "bor": 0,
  "res": 151,
  "assets": [
   103,
   122,
   153,
   175
  ],
  "cfo": [
   -3,
   20,
   8,
   47
  ],
  "model": "Aerospace and defence engineering company. Builds engineered systems and wiring assemblies, and repairs and overhauls aircraft parts with foreign partners.",
  "drivers": [
   "Defence indigenisation and offset orders",
   "Order flow from Indian defence public-sector units and foreign makers",
   "Repair and overhaul work"
  ],
  "watch": "Orders are lumpy: trailing twelve-month sales are below FY26, and the P/E is 55.",
  "src": "https://www.screener.in/company/SIKA/consolidated/"
 },
 {
  "n": "Prevest Denpro",
  "t": "PREVEST",
  "moat": "Niche",
  "cap": 495,
  "pe": 22,
  "roce": 24.2,
  "sales": [
   null,
   56,
   63,
   72
  ],
  "np": 20,
  "bor": 0,
  "res": 113,
  "assets": [
   null,
   95,
   113,
   133
  ],
  "cfo": [
   null,
   12,
   15,
   15
  ],
  "model": "Jammu-based maker of dental materials such as cements, composites and impression materials, sold through distributors in India and abroad.",
  "drivers": [
   "Adding export distributors and countries",
   "New product launches",
   "More people getting dental treatment in India"
  ],
  "watch": "Very small company. The source has only three years of data, and cash flow was flat in FY26.",
  "src": "https://www.screener.in/company/543363/consolidated/"
 },
 {
  "n": "Indian Energy Exchange",
  "t": "IEX",
  "moat": "Monopoly",
  "cap": 10378,
  "pe": 19.8,
  "roce": 51.4,
  "sales": [
   401,
   449,
   537,
   616
  ],
  "np": 493,
  "bor": 11,
  "res": 1275,
  "assets": [
   1453,
   1774,
   2196,
   2436
  ],
  "cfo": [
   -23,
   298,
   427,
   433
  ],
  "model": "India's dominant power exchange. Charges a small fee on every unit of electricity bought and sold on its platform.",
  "drivers": [
   "More electricity being traded on exchanges instead of long-term contracts",
   "Real-time and green power markets",
   "Renewable energy certificate trading"
  ],
  "watch": "Market cap is just over ₹10,000 Cr. The regulator's market-coupling plan could weaken its monopoly.",
  "src": "https://www.screener.in/company/IEX/consolidated"
 },
 {
  "n": "Nesco",
  "t": "NESCO",
  "moat": "Niche",
  "cap": 7482,
  "pe": 18.6,
  "roce": 18.5,
  "sales": [
   546,
   678,
   732,
   932
  ],
  "np": 413,
  "bor": 272,
  "res": 2982,
  "assets": [
   2263,
   2650,
   3016,
   3689
  ],
  "cfo": [
   297,
   377,
   349,
   388
  ],
  "model": "Owns the Bombay Exhibition Centre and an IT park on one large plot in Mumbai. Earns exhibition rentals, office rents and food service income.",
  "drivers": [
   "Exhibition days booked and rates",
   "Office rents and new towers",
   "Food business and new roadside-amenity projects"
  ],
  "watch": "Revenue grew only 8% in FY25, and it took on debt in FY26 for expansion.",
  "src": "https://www.screener.in/company/NESCO/consolidated"
 },
 {
  "n": "Ksolves India",
  "t": "KSOLVES",
  "moat": "Niche",
  "cap": 505,
  "pe": 14.1,
  "roce": 132,
  "sales": [
   78,
   109,
   137,
   163
  ],
  "np": 34,
  "bor": 6,
  "res": 18,
  "assets": [
   34,
   40,
   56,
   62
  ],
  "cfo": [
   21,
   33,
   34,
   31
  ],
  "model": "Small IT services firm specialising in big-data tools, Salesforce and AI work for overseas clients.",
  "drivers": [
   "New client wins",
   "Billing rates and headcount",
   "AI and data projects"
  ],
  "watch": "Profit has been stuck at ₹34 Cr for three years while sales grew. IT services is not a protected niche.",
  "src": "https://www.screener.in/company/KSOLVES/consolidated"
 },
 {
  "n": "Voltamp Transformers",
  "t": "VOLTAMP",
  "moat": "Niche",
  "cap": 9650,
  "pe": 29.8,
  "roce": 23.5,
  "sales": [
   1385,
   1616,
   1934,
   2154
  ],
  "np": 305,
  "bor": 1,
  "res": 1782,
  "assets": [
   1223,
   1521,
   1776,
   2018
  ],
  "cfo": [
   168,
   216,
   219,
   140
  ],
  "model": "Makes industrial transformers, mostly for private-sector factories, buildings and power projects rather than state utilities.",
  "drivers": [
   "Private capital spending",
   "Data centres and renewable projects",
   "New factory capacity"
  ],
  "watch": "Net margin slipped to 14.2% in FY26 and cash flow fell.",
  "src": "https://www.screener.in/company/VOLTAMP/"
 },
 {
  "n": "Paras Defence",
  "t": "PARAS",
  "moat": "Niche",
  "cap": 10269,
  "pe": 101,
  "roce": 17.2,
  "sales": [
   222,
   254,
   365,
   477
  ],
  "np": 89,
  "bor": 27,
  "res": 685,
  "assets": [
   520,
   640,
   852,
   964
  ],
  "cfo": [
   46,
   -46,
   45,
   25
  ],
  "model": "Makes optics for defence and space, defence electronics and electromagnetic-pulse protection systems.",
  "drivers": [
   "Defence and space programme orders",
   "Optical and electro-optic systems",
   "Drones and newer products"
  ],
  "watch": "P/E of 101, market cap just over your ceiling, and cash flow is uneven.",
  "src": "https://www.screener.in/company/PARAS/consolidated/"
 },
 {
  "n": "Raghav Productivity Enhancers",
  "t": "RPEL",
  "moat": "Niche",
  "cap": 9084,
  "pe": 129,
  "roce": 30.3,
  "sales": [
   137,
   133,
   200,
   257
  ],
  "np": 55,
  "bor": 5,
  "res": 199,
  "assets": [
   161,
   186,
   231,
   284
  ],
  "cfo": [
   20,
   21,
   39,
   37
  ],
  "model": "Makes silica ramming mass, the lining material used inside induction furnaces that melt steel. Sells to steel makers in India and abroad.",
  "drivers": [
   "Steel made in induction furnaces",
   "Customers switching from unbranded material",
   "Exports"
  ],
  "watch": "P/E of 129. Sales dipped in FY24.",
  "src": "https://www.screener.in/company/RPEL/consolidated/"
 },
 {
  "n": "Shilchar Technologies",
  "t": "SHILCTECH",
  "moat": "Niche",
  "cap": 4070,
  "pe": 32.7,
  "roce": 50.7,
  "sales": [
   280,
   397,
   623,
   652
  ],
  "np": 158,
  "bor": 0,
  "res": 479,
  "assets": [
   178,
   292,
   490,
   591
  ],
  "cfo": [
   39,
   76,
   40,
   192
  ],
  "model": "Makes transformers for solar and wind projects and for export customers.",
  "drivers": [
   "Renewable capacity additions",
   "Export orders",
   "New capacity"
  ],
  "watch": "Growth stalled to under 5% in FY26 and trailing profit is down.",
  "src": "https://www.screener.in/company/SHILCTECH/"
 },
 {
  "n": "Jyoti Resins and Adhesives",
  "t": "JYOTIRES",
  "moat": "Niche",
  "cap": 1098,
  "pe": 16.7,
  "roce": 36.5,
  "sales": [
   261,
   257,
   284,
   315
  ],
  "np": 70,
  "bor": 0,
  "res": 277,
  "assets": [
   211,
   292,
   373,
   426
  ],
  "cfo": [
   1,
   27,
   15,
   48
  ],
  "model": "Sells Euro 7000 wood adhesive to carpenters through dealers, competing with one very large rival.",
  "drivers": [
   "Adding dealers and new states",
   "Furniture and housing demand",
   "Carpenter loyalty schemes"
  ],
  "watch": "Sales fell slightly in FY24 and profit dipped in FY26.",
  "src": "https://www.screener.in/company/JYOTIRES/"
 },
 {
  "n": "CE Info Systems (MapmyIndia)",
  "t": "MAPMYINDIA",
  "moat": "Monopoly",
  "cap": 4798,
  "pe": 31.1,
  "roce": 19.1,
  "sales": [
   281,
   379,
   463,
   474
  ],
  "np": 134,
  "bor": 7,
  "res": 894,
  "assets": [
   673,
   794,
   944,
   1038
  ],
  "cfo": [
   90,
   76,
   117,
   93
  ],
  "model": "Licenses digital maps and navigation software to car makers, companies and government, and sells tracking devices.",
  "drivers": [
   "Cars sold with built-in navigation",
   "Enterprise and government mapping contracts",
   "Connected devices"
  ],
  "watch": "Revenue grew only 2% in FY26.",
  "src": "https://www.screener.in/company/MAPMYINDIA/consolidated/"
 },
 {
  "n": "MPS",
  "t": "MPSLTD",
  "moat": "Niche",
  "cap": 3865,
  "pe": 20.3,
  "roce": 38.7,
  "sales": [
   501,
   545,
   727,
   768
  ],
  "np": 173,
  "bor": 61,
  "res": 579,
  "assets": [
   551,
   736,
   670,
   912
  ],
  "cfo": [
   113,
   118,
   101,
   197
  ],
  "model": "Provides content production, platforms and e-learning services to academic publishers and companies.",
  "drivers": [
   "Publishers outsourcing more work",
   "Acquisitions",
   "Platform subscriptions"
  ],
  "watch": "Growth comes in bursts from acquisitions: under 10% in two of three years.",
  "src": "https://www.screener.in/company/MPSLTD/consolidated/"
 },
 {
  "n": "Shivalik Bimetal Controls",
  "t": "SBCL",
  "moat": "Niche",
  "cap": 5963,
  "pe": 51.1,
  "roce": 26.6,
  "sales": [
   470,
   509,
   508,
   571
  ],
  "np": 96,
  "bor": 71,
  "res": 470,
  "assets": [
   390,
   443,
   508,
   636
  ],
  "cfo": [
   66,
   69,
   94,
   55
  ],
  "model": "Makes thermostatic bimetal strips and shunt resistors used in switchgear, smart meters and electric-vehicle battery systems.",
  "drivers": [
   "Smart meter rollout",
   "Electric vehicles",
   "Switchgear demand and exports"
  ],
  "watch": "Sales were flat in FY25 and the P/E is 51.",
  "src": "https://www.screener.in/company/SBCL/consolidated/"
 },
 {
  "n": "Shanthi Gears",
  "t": "SHANTIGEAR",
  "moat": "Niche",
  "cap": 3994,
  "pe": 64.9,
  "roce": 25.6,
  "sales": [
   446,
   536,
   605,
   519
  ],
  "np": 77,
  "bor": 0,
  "res": 432,
  "assets": [
   377,
   443,
   504,
   556
  ],
  "cfo": [
   63,
   36,
   91,
   70
  ],
  "model": "Makes industrial gearboxes for steel, cement, power and other heavy industries.",
  "drivers": [
   "Industrial capital spending",
   "Replacement and service demand",
   "Exports"
  ],
  "watch": "Sales fell 14% in FY26.",
  "src": "https://www.screener.in/company/SHANTIGEAR/"
 },
 {
  "n": "Saregama India",
  "t": "SAREGAMA",
  "moat": "Oligopoly",
  "cap": 12967,
  "pe": 52.1,
  "roce": 17.3,
  "sales": [
   737,
   803,
   1171,
   985
  ],
  "np": 206,
  "bor": 73,
  "res": 1673,
  "assets": [
   1704,
   2034,
   2095,
   2319
  ],
  "cfo": [
   93,
   93,
   331,
   100
  ],
  "model": "Music label that licenses its song catalogue to streaming apps, video platforms and broadcasters, and also makes films and runs events.",
  "drivers": [
   "Paid streaming and video platform payouts",
   "New music acquisitions",
   "Films, series and live events"
  ],
  "watch": "Above your market-cap ceiling and sales fell in FY26.",
  "src": "https://www.screener.in/company/SAREGAMA/consolidated/"
 }
]''')

COMMODITY_WORDS = [
    "steel", "aluminum", "copper", "metals & mining", "coal", "oil & gas", "gold", "silver",
    "chemicals", "agricultural inputs", "paper", "lumber", "building materials", "textile",
    "farm products", "sugar", "coking",
]


# ---------- screening logic ----------
def clean(values):
    return [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]


def evaluate(c, f):
    """Test one company against the filters. Lists run oldest to newest."""
    sales = c["sales"]
    growth = [
        (sales[i] / sales[i - 1] - 1) * 100
        for i in range(1, len(sales))
        if sales[i] is not None and sales[i - 1] not in (None, 0)
    ]
    last_sales = clean(sales)[-1] if clean(sales) else None
    margin = c["np"] / last_sales * 100 if last_sales and c.get("np") is not None else None
    equity = c.get("equity")
    de = (c.get("debt") or 0) / equity if equity and equity > 0 else None
    assets = clean(c.get("assets", []))
    cfo = clean(c.get("cfo", []))
    assets_up = len(assets) >= 2 and all(b > a for a, b in zip(assets, assets[1:]))
    cash_every = len(cfo) >= 2 and all(b > a for a, b in zip(cfo, cfo[1:]))
    cash_two = len(cfo) >= 3 and cfo[-1] > cfo[-3]
    pe = c.get("pe")

    checks = {
        "Size": c.get("cap") is not None and f["cap_min"] <= c["cap"] <= f["cap_max"],
        "Growth": bool(growth) and min(growth) >= f["growth"],
        "Margin": margin is not None and margin >= f["margin"],
        "Debt": de is not None and de <= f["debt"],
        "P/E": f["pe"] >= 150 or (pe is not None and pe <= f["pe"]),
    }
    if f["assets"]:
        checks["Assets"] = assets_up
    if f["cash"] or f["cash_strict"]:
        checks["Cash flow"] = cash_every if f["cash_strict"] else cash_two
    if c.get("moat") and f.get("moats") is not None:
        checks["Moat type"] = c["moat"] in f["moats"]
    if f.get("hide_commodity") and c.get("industry"):
        checks["Not commodity"] = not any(w in c["industry"].lower() for w in COMMODITY_WORDS)
    fails = [k for k, ok in checks.items() if not ok]
    return {"growth": growth, "margin": margin, "de": de, "checks": checks, "fails": fails}


# ---------- live data from Yahoo Finance ----------
def _row(df, names):
    """Return a statement row, oldest to newest, last four years."""
    if df is None or df.empty:
        return []
    for name in names:
        if name in df.index:
            s = df.loc[name].dropna()
            s = s.sort_index()
            return [float(v) / 1e7 for v in s.tolist()][-4:]  # rupees to crore
    return []


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def fetch_company(symbol):
    import yfinance as yf

    tk = yf.Ticker(symbol)
    info = tk.info or {}
    inc, bal, cf = tk.income_stmt, tk.balance_sheet, tk.cashflow
    sales = _row(inc, ["Total Revenue", "Operating Revenue"])
    profit = _row(inc, ["Net Income", "Net Income Common Stockholders"])
    if not sales or not profit:
        raise ValueError("no financial statements returned")
    debt = _row(bal, ["Total Debt"])
    equity = _row(bal, ["Stockholders Equity", "Common Stock Equity"])
    cap = info.get("marketCap")
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    return {
        "price": price,
        "prev": info.get("previousClose") or info.get("regularMarketPreviousClose"),
        "n": info.get("longName") or info.get("shortName") or symbol,
        "t": symbol.split(".")[0],
        "cap": cap / 1e7 if cap else None,
        "pe": info.get("trailingPE"),
        "sales": sales,
        "np": profit[-1],
        "debt": debt[-1] if debt else 0.0,
        "equity": equity[-1] if equity else None,
        "assets": _row(bal, ["Total Assets"]),
        "cfo": _row(cf, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]),
        "industry": info.get("industry") or "",
        "summary": info.get("longBusinessSummary") or "",
    }


@st.cache_data(ttl=15 * 60, show_spinner=False)
def fetch_quotes(tickers):
    """Live price, previous close and market cap (₹ Cr) for each ticker. Tries NSE, then BSE."""
    import yfinance as yf

    quotes, misses = {}, 0
    for t in tickers:
        for suffix in (".NS", ".BO"):
            try:
                fi = yf.Ticker(t + suffix).fast_info
                price = fi["last_price"]
                if price is None or price != price:
                    continue
                cap = fi["market_cap"]
                prev = fi["previous_close"]
                quotes[t] = {"price": float(price), "prev": float(prev) if prev else None,
                             "cap": float(cap) / 1e7 if cap else None}
                break
            except Exception:
                continue
        if t in quotes:
            misses = 0
        else:
            misses += 1
            if misses >= 4 and not quotes:  # Yahoo is not answering, stop waiting
                break
    return quotes


def to_symbol(raw):
    s = raw.strip().upper()
    if not s:
        return None
    return s if "." in s else s + ".NS"


# ---------- sidebar ----------
st.sidebar.header("Your filters")
c1, c2 = st.sidebar.columns(2)
cap_min = c1.number_input("Min market cap (₹ Cr)", min_value=0, value=300, step=50)
cap_max = c2.number_input("Max market cap (₹ Cr)", min_value=0, value=10000, step=500)
growth = st.sidebar.slider("Revenue growth every year, at least (%)", 0, 30, 10)
margin = st.sidebar.slider("Net profit margin, at least (%)", 0, 40, 15)
debt = st.sidebar.slider("Debt to equity, below (x)", 0.0, 2.0, 1.0, 0.1)
pe = st.sidebar.slider("P/E ceiling (150 = any)", 10, 150, 150, 5)
assets_on = st.sidebar.checkbox("Total assets rise every year", True)
cash_on = st.sidebar.checkbox("Operating cash flow higher than two years ago", True)
cash_strict = st.sidebar.checkbox("Stricter: cash flow up every single year", False)
moats = st.sidebar.multiselect("Type of moat (shortlist only)", ["Monopoly", "Oligopoly", "Niche"],
                               ["Monopoly", "Oligopoly", "Niche"])
hide_commodity = st.sidebar.checkbox("Hide commodity industries (live search only)", True)
sort_by = st.sidebar.selectbox("Sort by", ["P/E, cheapest first", "Net margin, highest first",
                                           "Latest revenue growth", "Market cap, smallest first"])

FILTERS = dict(cap_min=cap_min, cap_max=cap_max, growth=growth, margin=margin, debt=debt, pe=pe,
               assets=assets_on, cash=cash_on, cash_strict=cash_strict, moats=moats,
               hide_commodity=hide_commodity)


def sort_key(row):
    c, r = row
    if sort_by.startswith("P/E"):
        return c.get("pe") if c.get("pe") is not None else 1e9
    if sort_by.startswith("Net margin"):
        return -(r["margin"] or -1e9)
    if sort_by.startswith("Latest"):
        return -(r["growth"][-1] if r["growth"] else -1e9)
    return c.get("cap") or 1e9


def fmt(v, suffix="", digits=1):
    return "n/a" if v is None else f"{v:,.{digits}f}{suffix}"


def show_card(c, r):
    status = "✅ Passes every filter" if not r["fails"] else "⚠️ Misses: " + ", ".join(r["fails"])
    with st.container(border=True):
        tag = f" · {c['moat']}" if c.get("moat") else (f" · {c['industry']}" if c.get("industry") else "")
        st.subheader(f"{c['n']} ({c['t']}){tag}")
        st.caption(status)
        m = st.columns(5)
        price, prev = c.get("price"), c.get("prev")
        change = f"{(price / prev - 1) * 100:+.2f}% today" if price and prev else None
        m[0].metric("Live price" if price else "Price", (f"₹{price:,.0f}" if price >= 1000 else f"₹{price:,.2f}") if price else "n/a", change)
        m[1].metric("Market cap", "n/a" if c.get("cap") is None else f"₹{c['cap']:,.0f} Cr")
        m[2].metric("P/E", fmt(c.get("pe")))
        m[3].metric("Net margin", fmt(r["margin"], "%"))
        m[4].metric("Debt / equity", fmt(r["de"], "x", 2))
        n = len(c["sales"])
        labels = YEARS[-n:] if c.get("moat") else [f"Y{i + 1}" for i in range(n)]
        trend = "  →  ".join(f"{labels[i]} {s:,.0f}" for i, s in enumerate(c["sales"]) if s is not None)
        gtxt = " · ".join(f"{g:+.0f}%" for g in r["growth"])
        st.write(f"**Revenue (₹ Cr):** {trend}  |  **Yearly growth:** {gtxt}")
        if c.get("model"):
            a, b = st.columns(2)
            a.markdown("**Business model**\n\n" + c["model"])
            b.markdown("**Revenue drivers**\n\n" + "\n".join(f"- {d}" for d in c["drivers"]))
            st.markdown(f"**Watch out:** {c['watch']}  \n[Check the numbers on Screener]({c['src']})")
        elif c.get("summary"):
            with st.expander("What the company does"):
                st.write(c["summary"])


def show_results(rows):
    rows.sort(key=sort_key)
    passed = [x for x in rows if not x[1]["fails"]]
    near = [x for x in rows if len(x[1]["fails"]) == 1]
    out = [x for x in rows if len(x[1]["fails"]) > 1]
    k = st.columns(3)
    k[0].metric("Pass every filter", f"{len(passed)} of {len(rows)}")
    k[1].metric("Miss by one filter", len(near))
    k[2].metric("Miss by two or more", len(out))
    st.markdown("### Pass every filter")
    if not passed:
        st.info("Nothing passes with these settings. Loosen one filter in the sidebar.")
    for c, r in passed:
        show_card(c, r)
    if near:
        st.markdown("### Miss by one filter")
        for c, r in near:
            show_card(c, r)
    if out:
        with st.expander(f"Miss two or more filters ({len(out)})"):
            st.dataframe(pd.DataFrame([{"Company": c["n"], "Misses": ", ".join(r["fails"])} for c, r in out]),
                         hide_index=True)


# ---------- page ----------
st.title("Hidden Compounders Screener")
st.write("Find Indian small and mid caps in niche, monopoly or oligopoly businesses. "
         "Set your own rules in the sidebar and the list updates.")

tab1, tab2, tab3 = st.tabs(["Researched shortlist", "Screen your own stocks", "How it works"])

with tab1:
    with st.spinner("Getting live prices"):
        try:
            quotes = fetch_quotes(tuple(c["t"] for c in CURATED))
        except Exception:
            quotes = {}
    if quotes:
        st.caption(f"21 niche, monopoly and oligopoly companies. Live price and market cap from Yahoo Finance "
                   f"for {len(quotes)} of {len(CURATED)}, refreshed every 15 minutes. "
                   "Annual figures to March 2026.")
    else:
        st.caption("21 niche, monopoly and oligopoly companies. Live prices are not available right now, "
                   "so market cap and P/E are from mid-November 2026. Annual figures to March 2026.")
    rows = []
    for c in CURATED:
        item = dict(c, debt=c["bor"], equity=c["res"])
        q = quotes.get(c["t"])
        if q:
            item["price"], item["prev"] = q["price"], q["prev"]
            if q["cap"]:
                item["pe"] = round(c["pe"] * q["cap"] / c["cap"], 1)  # same earnings, new price
                item["cap"] = q["cap"]
        rows.append((item, evaluate(item, FILTERS)))
    show_results(rows)

with tab2:
    st.caption("Type NSE symbols separated by commas. Data comes live from Yahoo Finance, "
               "so it can be slow and some symbols may not load.")
    raw = st.text_area("NSE symbols", "PRICOL, CAMS, CDSL, TIPSMUSIC, CONTROLPR, KPITTECH")
    if st.button("Screen these stocks", type="primary"):
        symbols = [s for s in (to_symbol(x) for x in raw.replace("\n", ",").split(",")) if s][:25]
        rows, errors = [], []
        bar = st.progress(0.0, "Fetching data")
        for i, sym in enumerate(symbols):
            try:
                c = fetch_company(sym)
                rows.append((c, evaluate(c, dict(FILTERS, moats=None))))
            except Exception as e:  # one bad symbol should not stop the rest
                errors.append(f"{sym}: {e}")
            bar.progress((i + 1) / len(symbols), f"Fetched {i + 1} of {len(symbols)}")
        bar.empty()
        if errors:
            st.warning("Could not load: " + "; ".join(errors))
        if rows:
            show_results(rows)

with tab3:
    st.markdown(
        """
**What the filters test**

- **Size:** market cap inside your range.
- **Growth:** revenue grew by at least your percentage in every one of the last three years.
- **Margin:** latest net profit divided by latest revenue.
- **Debt:** borrowings divided by shareholders' equity.
- **Assets:** total assets rose every year.
- **Cash flow:** operating cash flow is higher than two years ago, or up every year in strict mode.
- **P/E:** a rough check on whether the price is still reasonable.

Commodity businesses such as metals, bulk chemicals, sugar, cement and yarn are left out.

**Data:** the shortlist uses annual results from Screener.in. Live search uses Yahoo Finance.

This is a research tool, not investment advice. Check the latest filings before investing.
"""
    )

st.caption("Built by Tejas Sharma.")
