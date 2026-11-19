"""Hidden Compounders Screener (US & UK) - find niche US and UK small and mid caps by your own metrics.

Run locally:   streamlit run global_screener_app.py
Deploy:        push this file and requirements.txt to GitHub, then create a new app on Streamlit Community Cloud
               with global_screener_app.py as the main file.

All money figures are in the company's home currency: US dollars for US stocks, pounds for UK stocks.
Statement figures are in millions ($m or £m). Prices are per share in $ or £ (UK prices are converted from pence).
"""
import math

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hidden Compounders Screener - US & UK", page_icon="📈", layout="wide")

MARKETS = {
    "United States": {"code": "US", "cur": "$", "suffix": "", "cap": (300, 10000),
                      "example": "MANH, ROL, AAON, EXPO, CSWI, FICO", "exchange": "US tickers",
                      "src_label": "Check the numbers in the SEC filings"},
    "United Kingdom": {"code": "UK", "cur": "£", "suffix": ".L", "cap": (50, 5000),
                       "example": "JDG, DPLM, HWDN, KNOS, GAMA, FDM", "exchange": "London (LSE and AIM) tickers",
                       "src_label": "Check the numbers on Stock Analysis"},
}

# Figures in millions of the home currency. Lists run oldest to newest, with the fiscal years in "fy".
# price is per share in $ or £ (a fallback, replaced by the live price when Yahoo answers); shares in millions.
CURATED = {
    "US": [
        {
            "n": "Badger Meter", "t": "BMI", "moat": "Oligopoly", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 120.0, "shares": 29.19,
            "sales": [566, 704, 827, 917], "np": 142, "debt": 0, "equity": 713,
            "assets": [603, 717, 816, 974], "cfo": [82, 110, 155, 184],
            "model": "Badger Meter makes the water meters that US cities and water utilities use to bill households and "
                     "businesses, plus the radio network and BEACON software that read those meters remotely. A handful "
                     "of companies (Badger, Xylem's Sensus, Neptune, Itron, Mueller) supply most of the market, and once a "
                     "utility picks a system it tends to stay with it for decades because swapping meters and software is "
                     "slow and costly. Badger earns on the meter, then keeps earning yearly software and data fees.",
            "drivers": ["Utilities replacing old manual meters with smart, remotely read meters",
                        "Recurring software, cellular reading and data fees (BEACON)",
                        "Water quality and pipe monitoring sensors sold to the same utilities"],
            "watch": "Sales depend on city and utility budgets, and growth may slow once the current smart-meter "
                     "replacement wave is done.",
            "src": "https://app.edgar.tools/companies/BMI",
        },
        {
            "n": "Doximity", "t": "DOCS", "moat": "Monopoly", "rare": True,
            "fy": ["FY23", "FY24", "FY25", "FY26"], "price": 21.6, "shares": 188,
            "sales": [419.05, 475.42, 570.4, 644.86], "np": 196.05, "debt": 0, "equity": 951,
            "assets": [1137, 1079, 1264, 1124], "cfo": [179.6, 184.1, 273.3, 326.5],
            "model": "Doximity is the professional network for US doctors, often called LinkedIn for physicians, and most "
                     "US doctors are members. Doctors use it free for news, secure messaging, telehealth calls, faxing "
                     "and AI writing tools. Drug companies and hospitals pay Doximity to reach those doctors with "
                     "marketing and job ads, and no rival platform has the same reach among verified physicians.",
            "drivers": ["Pharma companies' digital marketing budgets aimed at doctors",
                        "Hospital and health-system recruiting subscriptions",
                        "New paid workflow and AI tools built on its daily users"],
            "watch": "Most revenue comes from pharma marketing budgets, and growth slowed to about 13% in the latest year "
                     "with profit falling, so the market is questioning how much more it can grow.",
            "src": "https://app.edgar.tools/companies/DOCS",
        },
        {
            "n": "Qualys", "t": "QLYS", "moat": "Oligopoly", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 200.0, "shares": 35.73,
            "sales": [490, 554, 608, 669], "np": 198, "debt": 0, "equity": 561,
            "assets": [701, 813, 974, 1095], "cfo": [199, 245, 244, 309],
            "model": "Qualys sells cloud software that scans a company's computers, servers and cloud accounts for security "
                     "holes and tells IT teams which ones to fix first. Customers pay a yearly subscription, usually "
                     "priced by how many devices are scanned. Vulnerability management is dominated by three players "
                     "(Qualys, Tenable and Rapid7), and once a security team builds its processes around one scanner it "
                     "rarely switches.",
            "drivers": ["More devices and cloud workloads per customer to scan",
                        "Selling extra modules (patching, compliance, cloud security) to existing customers",
                        "Price rises on renewals"],
            "watch": "Growth has slowed to around 10% a year, and big platforms such as Microsoft and CrowdStrike are "
                     "bundling similar features.",
            "src": "https://app.edgar.tools/companies/QLYS",
        },
        {
            "n": "LeMaitre Vascular", "t": "LMAT", "moat": "Niche", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 84.0, "shares": 22.77,
            "sales": [162, 193, 220, 250], "np": 58, "debt": 169, "equity": 394,
            "assets": [310, 347, 552, 616], "cfo": [25, 37, 44, 81],
            "model": "LeMaitre makes devices for vascular surgeons, such as patches, shunts, catheters and human-tissue "
                     "grafts used in artery and vein surgery. These are small, low-volume products that big medical "
                     "companies ignore, so LeMaitre is often the main supplier. Hospitals buy them per operation, and "
                     "the company raises prices steadily because a surgeon will not switch a trusted device to save a "
                     "few dollars.",
            "drivers": ["Yearly price increases on products with few competitors",
                        "Buying small device lines from bigger companies and selling them through its own sales team",
                        "Tissue grafts and new country approvals"],
            "watch": "Part of the growth comes from acquisitions, and it carries convertible notes, so check debt "
                     "and how well bought-in products do.",
            "src": "https://app.edgar.tools/companies/LMAT",
        },
        {
            "n": "Corcept Therapeutics", "t": "CORT", "moat": "Niche", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 105.0, "shares": 106,
            "sales": [402, 482, 675, 761], "np": 100, "debt": 0, "equity": 648,
            "assets": [583, 622, 841, 837], "cfo": [120, 127, 198, 142],
            "model": "Corcept sells medicines that block cortisol, the stress hormone, for patients with Cushing's syndrome, "
                     "a rare disease where the body makes too much of it. Its drug Korlym is a specialty medicine sold "
                     "through specialist pharmacies, and Corcept is developing newer cortisol blockers such as "
                     "relacorilant for Cushing's and some cancers. Very few companies work in this area.",
            "drivers": ["More Cushing's patients being diagnosed and treated",
                        "Approval and launch of newer cortisol modulators such as relacorilant",
                        "Possible use of its drugs in ovarian cancer and other diseases"],
            "watch": "Sales rest on one drug family. Generic copies of Korlym and regulators' decisions on its newer "
                     "drugs will decide the next few years, and profit fell in 2025.",
            "src": "https://app.edgar.tools/companies/CORT",
        },
        {
            "n": "Halozyme Therapeutics", "t": "HALO", "moat": "Monopoly", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 128.0, "shares": 117.8,
            "sales": [660, 829, 1015, 1397], "np": 317, "debt": 2143, "equity": 49,
            "assets": [1842, 1733, 2063, 2525], "cfo": [240, 389, 479, 652],
            "model": "Halozyme owns ENHANZE, an enzyme that lets big drugs normally given by a slow drip into a vein be "
                     "injected under the skin in a few minutes instead. Drug giants such as Roche, J&J, Bristol Myers "
                     "and Pfizer license it for their blockbusters and pay Halozyme milestones and a royalty on every "
                     "sale. It is effectively the only widely used platform of its kind.",
            "drivers": ["Royalties on partner drugs such as Darzalex, Phesgo and Opdivo given under the skin",
                        "New partner deals and milestone payments",
                        "Its own auto-injector devices and specialty products"],
            "watch": "Equity is tiny because of buybacks funded with convertible debt, so debt to equity looks extreme. "
                     "Key patents start to expire towards the end of the decade.",
            "src": "https://app.edgar.tools/companies/HALO",
        },
        {
            "n": "Kinsale Capital", "t": "KNSL", "moat": "Niche", "rare": False,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 370.0, "shares": 23.15,
            "sales": [839, 1224, 1588, 1874], "np": 504, "debt": 224, "equity": 1960,
            "assets": [2747, 3773, 4887, 6044], "cfo": [558, 860, 976, 1044],
            "model": "Kinsale is an insurer that only writes excess and surplus lines: hard-to-place risks that standard "
                     "insurers turn down, such as small contractors, bars, vacant buildings or unusual properties. "
                     "Because these policies are not tightly price-regulated, Kinsale can set its own prices and terms. "
                     "It runs on its own technology with low costs, and also earns investment income on the premiums "
                     "it holds before claims are paid.",
            "drivers": ["More risks pushed out of the standard insurance market into E&S",
                        "Premium rate increases",
                        "Investment income on its growing float"],
            "watch": "Revenue is mostly premiums, so margins are not comparable with other businesses, and a bad "
                     "catastrophe year or reserve hit can cut profit sharply.",
            "src": "https://app.edgar.tools/companies/KNSL",
        },
        {
            "n": "ADMA Biologics", "t": "ADMA", "moat": "Oligopoly", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 10.7, "shares": 237.9,
            "sales": [154, 258, 426, 510], "np": 147, "debt": 72, "equity": 477,
            "assets": [348, 329, 489, 624], "cfo": [-60, 9, 119, 50],
            "model": "ADMA collects blood plasma at its own US centres and turns it into immune globulin medicines for "
                     "patients whose immune systems do not work properly, led by its high-strength product ASCENIV. "
                     "Only a few companies worldwide can fractionate plasma at scale, because it needs FDA-licensed "
                     "plants and a steady donor network.",
            "drivers": ["ASCENIV sales to immune-deficient patients",
                        "More plasma collected and higher yields from each litre",
                        "Bigger manufacturing output at its Florida plant"],
            "watch": "2024 profit was lifted by a one-off tax benefit, operating cash flow swings a lot, and the "
                     "business depends on plasma supply.",
            "src": "https://app.edgar.tools/companies/ADMA",
        },
    ],
    "UK": [
        {
            "n": "Games Workshop", "t": "GAW", "moat": "Monopoly", "rare": True,
            "fy": ["FY23", "FY24", "FY25", "FY26"], "price": 197.0, "shares": 32.98,
            "sales": [470.8, 525.7, 617.5, 659.7], "np": 206.0, "debt": 56.0, "equity": 335.3,
            "assets": [326.8, 351.3, 383.0, 466.6], "cfo": [192.7, 196.2, 247.4, 267.7],
            "model": "Games Workshop owns Warhammer. It designs and makes plastic miniatures, paints, rulebooks and "
                     "codexes in Nottingham, and sells them through its own Warhammer stores, its website and "
                     "independent shops. Fans build and paint whole armies, so they keep buying for years, and no one "
                     "else can sell Warhammer. It also licenses the worlds to video games and an Amazon TV deal.",
            "drivers": ["New model releases and edition launches",
                        "More stores and trade accounts, especially in the US",
                        "Licensing income from video games and screen deals"],
            "watch": "It is bigger than the default size range, licensing income is lumpy, and growth depends on fans "
                     "accepting regular price rises.",
            "src": "https://stockanalysis.com/quote/lon/GAW/financials/",
        },
        {
            "n": "Rightmove", "t": "RMV", "moat": "Monopoly", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 4.68, "shares": 772,
            "sales": [332.62, 364.32, 389.88, 425.13], "np": 217.07, "debt": 0, "equity": 82.3,
            "assets": [101.76, 104.87, 118.5, 128.18], "cfo": [198.09, 206.71, 211.27, 236.30],
            "model": "Rightmove is the UK's biggest property website, where most people start when they look for a home "
                     "to buy or rent. Home buyers use it free; estate agents and new-home builders pay a monthly "
                     "subscription to list their properties, because an agent who is not on Rightmove loses sellers. "
                     "It costs little to run, so most of each pound of revenue becomes profit.",
            "drivers": ["Higher average revenue per agent through price rises and premium products",
                        "More agent and developer advertisers",
                        "New areas such as mortgages and rental services"],
            "watch": "Equity is small because it returns almost all its cash to shareholders, so price to book looks huge. "
                     "Agents push back on price rises, and its new AI spending is squeezing margins.",
            "src": "https://stockanalysis.com/quote/lon/RMV/financials/",
        },
        {
            "n": "AJ Bell", "t": "AJB", "moat": "Oligopoly", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 5.96, "shares": 403.57,
            "sales": [163.08, 217.28, 268.53, 316.92], "np": 105.12, "debt": 12.06, "equity": 217.45,
            "assets": [165.48, 234.32, 288.88, 303.08], "cfo": [45.80, 101.41, 96.29, 86.49],
            "model": "AJ Bell runs investment platforms where UK savers and financial advisers hold ISAs, SIPPs and "
                     "dealing accounts. It earns a yearly fee on the money held, a fee per trade, and interest on cash "
                     "left in accounts. A few platforms (Hargreaves Lansdown, AJ Bell, interactive investor) hold most "
                     "of the DIY market, and people rarely move their pension once it is set up.",
            "drivers": ["New customers and money moving onto the platform",
                        "Rising stock markets, which lift the value of assets it charges on",
                        "Interest earned on customer cash"],
            "watch": "Profit moves with markets and interest rates, and price cuts by rivals could force fee cuts. "
                     "Operating cash flow has fallen for two years.",
            "src": "https://stockanalysis.com/quote/lon/AJB/financials/",
        },
        {
            "n": "Cerillion", "t": "CER", "moat": "Niche", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 10.50, "shares": 29.5,
            "sales": [32.73, 39.17, 43.75, 45.36], "np": 16.62, "debt": 3.31, "equity": 59.61,
            "assets": [42.63, 52.79, 63.10, 75.27], "cfo": [12.34, 9.75, 11.21, 13.23],
            "model": "Cerillion makes billing, charging and customer-management software for telecom operators, mostly "
                     "mid-sized mobile, broadband and cable companies around the world. It charges for the initial "
                     "installation project and then earns recurring licence and support fees. Billing systems are hard "
                     "to replace, so customers stay for many years.",
            "drivers": ["New operator contracts for its billing platform",
                        "Recurring licence and support fees from installed customers",
                        "Extra modules and upgrades sold to existing clients"],
            "watch": "It is small and wins a few large contracts a year, so revenue is lumpy; profit over the "
                     "latest twelve months was lower.",
            "src": "https://stockanalysis.com/quote/aim/CER/financials/",
        },
        {
            "n": "Tatton Asset Management", "t": "TAM", "moat": "Niche", "rare": False,
            "fy": ["FY23", "FY24", "FY25", "FY26"], "price": 7.40, "shares": 61.3,
            "sales": [32.49, 35.62, 45.16, 54.35], "np": 18.84, "debt": 0.63, "equity": 55.05,
            "assets": [], "cfo": [13.23, 13.19, 18.75, 23.62],
            "assets_note": "Total assets were not available from the source, so that filter is skipped.",
            "model": "Tatton runs ready-made model portfolios that independent financial advisers put their clients into "
                     "on investment platforms. It charges a small yearly fee on the money managed, and its low price "
                     "has made it the UK's leading provider of these on-platform model portfolios. It also offers "
                     "compliance and support services to advisers through Paradigm.",
            "drivers": ["More advisers using its portfolios",
                        "Net new money and market growth lifting assets under management",
                        "Adviser support and mortgage services from Paradigm"],
            "watch": "Revenue follows stock markets, and fee pressure from rivals could squeeze it.",
            "src": "https://stockanalysis.com/quote/aim/TAM/financials/",
        },
        {
            "n": "Tristel", "t": "TSTL", "moat": "Niche", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 4.11, "shares": 48,
            "sales": [31.12, 36.01, 41.93, 46.46], "np": 6.64, "debt": 5.88, "equity": 32.99,
            "assets": [39.68, 41.37, 44.11, 45.33], "cfo": [5.42, 7.64, 9.75, 9.46],
            "cfo_note": "Cash flow figures are free cash flow; the source did not show operating cash flow.",
            "model": "Tristel makes chlorine dioxide disinfectant foams and wipes that hospitals use to clean ultrasound "
                     "probes and endoscopes between patients. Its products are approved in many countries and hospitals "
                     "buy them every day, so sales repeat. It recently gained US approval, opening the world's "
                     "biggest healthcare market.",
            "drivers": ["Repeat use of its wipes and foams in hospitals",
                        "US launch after FDA approval",
                        "New countries and new probe types"],
            "watch": "Net margin is lower than most companies here, and success in the US is not yet proven.",
            "src": "https://stockanalysis.com/quote/aim/TSTL/financials/",
        },
        {
            "n": "Bioventix", "t": "BVXP", "moat": "Niche", "rare": True,
            "fy": ["FY22", "FY23", "FY24", "FY25"], "price": 15.25, "shares": 5.22,
            "sales": [11.72, 12.82, 13.61, 13.12], "np": 7.58, "debt": 0, "equity": 11.55,
            "assets": [13.12, 13.28, 13.73, 12.86], "cfo": [7.56, 7.80, 8.34, 7.03],
            "model": "Bioventix creates sheep antibodies that diagnostic companies such as Roche and Siemens put inside "
                     "their blood tests, for things like vitamin D and heart attack markers. Once a test is approved "
                     "with Bioventix's antibody it is very hard to change, so Bioventix earns royalties for many years. "
                     "It has about a dozen staff and pays most profit out as dividends.",
            "drivers": ["Royalties on blood tests sold worldwide that use its antibodies",
                        "New antibodies, such as for Alzheimer's markers, reaching approved tests",
                        "Sales of antibody supplies to test makers"],
            "watch": "Revenue has stalled and fell in FY25, it depends on a few products, and with about £80m market cap "
                     "the shares trade thinly.",
            "src": "https://stockanalysis.com/quote/aim/BVXP/financials/",
        },
    ],
}

COMMODITY_WORDS = [
    "steel", "aluminum", "copper", "metals & mining", "coal", "oil & gas", "gold", "silver",
    "chemicals", "agricultural inputs", "paper", "lumber", "building materials", "textile",
    "farm products", "sugar", "coking", "uranium", "other industrial metals",
]


# ---------- formatting ----------
def money(v, cur):
    """Per-share amount in $ or £: no decimals from 1,000 upwards, two decimals below."""
    if v is None or v != v:
        return "n/a"
    return f"{cur}{v:,.0f}" if abs(v) >= 1000 else f"{cur}{v:,.2f}"


def big_money(v, cur):
    """Amount already in millions: shows £450m or $2.2bn."""
    if v is None or v != v:
        return "n/a"
    return f"{cur}{v / 1000:,.1f}bn" if abs(v) >= 1000 else f"{cur}{v:,.0f}m"


def fmt(v, suffix="", digits=1):
    return "n/a" if v is None else f"{v:,.{digits}f}{suffix}"


# ---------- screening logic ----------
def intrinsic_value(c, a):
    """Simple DCF on the latest net profit. Returns value per share in $ or £, or None."""
    sales = [s for s in c["sales"] if s]
    profit, shares = c.get("np"), c.get("shares")
    if len(sales) < 2 or not profit or profit <= 0 or not shares:
        return None
    cagr = (sales[-1] / sales[0]) ** (1 / (len(sales) - 1)) - 1
    g1 = min(max(cagr, 0.0), a["g_cap"] / 100)
    r, gt = a["discount"] / 100, a["terminal"] / 100
    if r <= gt:
        return None
    cash, total = profit, 0.0
    for year in range(1, 11):
        g = g1 if year <= 5 else g1 + (gt - g1) * (year - 5) / 5
        cash *= 1 + g
        total += cash / (1 + r) ** year
    total += cash * (1 + gt) / (r - gt) / (1 + r) ** 10
    return total / shares  # millions / millions of shares = per share


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

    floor = min(f["margin"], f["rare_margin"]) if c.get("rare") else f["margin"]
    iv = intrinsic_value(c, f)
    checks = {
        "Size": c.get("cap") is not None and f["cap_min"] <= c["cap"] <= f["cap_max"],
        "Growth": bool(growth) and min(growth) >= f["growth"],
        "Margin": margin is not None and margin >= floor,
        "Debt": de is not None and de <= f["debt"],
        "P/E": f["pe"] >= 150 or (pe is not None and pe <= f["pe"]),
    }
    if f["assets"] and not c.get("assets_note"):  # skipped only when the shortlist has no asset data
        checks["Assets"] = assets_up
    if f["cash"] or f["cash_strict"]:
        checks["Cash flow"] = cash_every if f["cash_strict"] else cash_two
    if c.get("moat") and f.get("moats") is not None:
        checks["Moat type"] = c["moat"] in f["moats"]
    if f.get("hide_commodity") and c.get("industry"):
        checks["Not commodity"] = not any(w in c["industry"].lower() for w in COMMODITY_WORDS)
    if f.get("below_iv"):
        checks["Below intrinsic value"] = iv is not None and c.get("price") is not None and c["price"] <= iv
    fails = [k for k, ok in checks.items() if not ok]
    return {"growth": growth, "margin": margin, "de": de, "checks": checks, "fails": fails, "iv": iv}


def with_valuation(c):
    """Add market cap, P/E and book value per share from price, shares and the statements."""
    item = dict(c)
    price, shares = item.get("price"), item.get("shares")
    item["cap"] = price * shares if price and shares else None
    item["pe"] = item["cap"] / item["np"] if item["cap"] and item.get("np") and item["np"] > 0 else None
    item["bv"] = item["equity"] / shares if item.get("equity") is not None and shares else None
    return item


# ---------- live data from Yahoo Finance ----------
def _pence_to_pounds(currency):
    """Yahoo quotes London shares in pence (GBp or GBX). Returns (divisor, major currency)."""
    if currency in ("GBp", "GBX", "GBx"):
        return 100.0, "GBP"
    return 1.0, currency


def _fx(from_cur, to_cur):
    """Exchange rate to turn from_cur amounts into to_cur. 1.0 when they match."""
    if not from_cur or not to_cur or from_cur == to_cur:
        return 1.0
    import yfinance as yf

    rate = yf.Ticker(f"{from_cur}{to_cur}=X").fast_info["last_price"]
    if not rate or rate != rate:
        raise ValueError(f"no exchange rate for {from_cur} to {to_cur}")
    return float(rate)


def _row(df, names, scale):
    """Return a statement row, oldest to newest, last four years, in millions of the home currency."""
    if df is None or df.empty:
        return [], []
    for name in names:
        if name in df.index:
            s = df.loc[name].dropna().sort_index()
            years = [f"FY{str(d.year)[-2:]}" for d in s.index][-4:]
            return [float(v) / 1e6 * scale for v in s.tolist()][-4:], years
    return [], []


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def fetch_company(symbol):
    import yfinance as yf

    tk = yf.Ticker(symbol)
    info = tk.info or {}
    divisor, home = _pence_to_pounds(info.get("currency"))
    fin = info.get("financialCurrency") or home
    scale = _fx(fin, home)  # statements are converted into the trading currency (e.g. USD reports for a UK listing)
    inc, bal, cf = tk.income_stmt, tk.balance_sheet, tk.cashflow
    sales, years = _row(inc, ["Total Revenue", "Operating Revenue"], scale)
    profit, _ = _row(inc, ["Net Income", "Net Income Common Stockholders"], scale)
    if not sales or not profit:
        raise ValueError("no financial statements returned")
    debt, _ = _row(bal, ["Total Debt"], scale)
    equity, _ = _row(bal, ["Stockholders Equity", "Common Stock Equity"], scale)
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
    shares = info.get("sharesOutstanding")
    item = {
        "price": price / divisor if price else None,
        "prev": prev / divisor if prev else None,
        "shares": shares / 1e6 if shares else None,
        "n": info.get("longName") or info.get("shortName") or symbol,
        "t": symbol.split(".")[0] if symbol.endswith(".L") else symbol,
        "fy": years,
        "sales": sales,
        "np": profit[-1],
        "debt": debt[-1] if debt else 0.0,
        "equity": equity[-1] if equity else None,
        "assets": _row(bal, ["Total Assets"], scale)[0],
        "cfo": _row(cf, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"], scale)[0],
        "industry": info.get("industry") or "",
        "summary": info.get("longBusinessSummary") or "",
        "home": home,
    }
    return with_valuation(item)


@st.cache_data(ttl=15 * 60, show_spinner=False)
def fetch_quotes(symbols):
    """Live price and previous close in $ or £ for each Yahoo symbol."""
    import yfinance as yf

    quotes, misses = {}, 0
    for sym in symbols:
        try:
            fi = yf.Ticker(sym).fast_info
            price = fi["last_price"]
            if price is not None and price == price:
                divisor, _ = _pence_to_pounds(fi["currency"])
                prev = fi["previous_close"]
                quotes[sym] = {"price": float(price) / divisor,
                               "prev": float(prev) / divisor if prev else None}
        except Exception:
            pass
        if sym in quotes:
            misses = 0
        else:
            misses += 1
            if misses >= 4 and not quotes:  # Yahoo is not answering, stop waiting
                break
    return quotes


def to_symbol(raw, market):
    s = raw.strip().upper()
    if not s:
        return None
    if market["code"] == "UK":
        return s if s.endswith(".L") else s.split(".")[0] + ".L"
    return s.replace(".", "-")  # Yahoo writes BRK.B as BRK-B


# ---------- sidebar ----------
st.sidebar.header("Market")
market_name = st.sidebar.radio("Choose a market", list(MARKETS), horizontal=True, label_visibility="collapsed")
MK = MARKETS[market_name]
CUR = MK["cur"]

st.sidebar.header("Your filters")
c1, c2 = st.sidebar.columns(2)
cap_min = c1.number_input(f"Min market cap ({CUR}m)", min_value=0, value=MK["cap"][0], step=50,
                          key=f"cap_min_{MK['code']}")
cap_max = c2.number_input(f"Max market cap ({CUR}m)", min_value=0, value=MK["cap"][1], step=500,
                          key=f"cap_max_{MK['code']}")
growth = st.sidebar.slider("Revenue growth every year, at least (%)", 0, 30, 10)
margin = st.sidebar.slider("Net profit margin, at least (%)", 0, 40, 15)
rare_margin = st.sidebar.slider("Margin floor for rare businesses (%)", 0, 40, 12,
                                help="Monopoly, oligopoly or rare-niche companies on the shortlist pass with this lower margin.")
debt = st.sidebar.slider("Debt to equity, below (x)", 0.0, 2.0, 1.0, 0.1)
pe = st.sidebar.slider("P/E ceiling (150 = any)", 10, 150, 150, 5)
assets_on = st.sidebar.checkbox("Total assets rise every year", True)
cash_on = st.sidebar.checkbox("Operating cash flow higher than two years ago", True)
cash_strict = st.sidebar.checkbox("Stricter: cash flow up every single year", False)
moats = st.sidebar.multiselect("Type of moat (shortlist only)", ["Monopoly", "Oligopoly", "Niche"],
                               ["Monopoly", "Oligopoly", "Niche"])
hide_commodity = st.sidebar.checkbox("Hide commodity industries (live search only)", True)
below_iv = st.sidebar.checkbox("Only stocks priced below intrinsic value", False)
with st.sidebar.expander("Intrinsic value assumptions"):
    discount = st.slider("Discount rate (%)", 8.0, 18.0, 12.0, 0.5)
    g_cap = st.slider("Highest growth allowed, years 1-5 (%)", 5, 30, 15)
    terminal = st.slider("Long-term growth (%)", 2.0, 7.0, 5.0, 0.5)
sort_by = st.sidebar.selectbox("Sort by", ["P/E, cheapest first", "Net margin, highest first",
                                           "Latest revenue growth", "Market cap, smallest first"])

FILTERS = dict(cap_min=cap_min, cap_max=cap_max, growth=growth, margin=margin, debt=debt, pe=pe,
               assets=assets_on, cash=cash_on, cash_strict=cash_strict, moats=moats,
               hide_commodity=hide_commodity, rare_margin=rare_margin, below_iv=below_iv,
               discount=discount, g_cap=g_cap, terminal=terminal)


def sort_key(row):
    c, r = row
    if sort_by.startswith("P/E"):
        return c.get("pe") if c.get("pe") is not None else 1e9
    if sort_by.startswith("Net margin"):
        return -(r["margin"] or -1e9)
    if sort_by.startswith("Latest"):
        return -(r["growth"][-1] if r["growth"] else -1e9)
    return c.get("cap") or 1e9


def show_card(c, r):
    status = "✅ Passes every filter" if not r["fails"] else "⚠️ Misses: " + ", ".join(r["fails"])
    with st.container(border=True):
        tag = f" · {c['moat']}" if c.get("moat") else (f" · {c['industry']}" if c.get("industry") else "")
        st.subheader(f"{c['n']} ({c['t']}){tag}")
        st.caption(status + ("  ·  Rare business" if c.get("rare") else ""))
        price, prev, bv, iv = c.get("price"), c.get("prev"), c.get("bv"), r.get("iv")
        change = f"{(price / prev - 1) * 100:+.2f}% today" if price and prev else None
        gap = f"{(iv / price - 1) * 100:+.0f}% vs price" if iv and price else None
        m = st.columns(4)
        m[0].metric("Live price" if c.get("live") else "Price", money(price, CUR), change)
        m[1].metric("Intrinsic value", money(iv, CUR), gap)
        m[2].metric("Book value per share", money(bv, CUR))
        m[3].metric("Market cap", big_money(c.get("cap"), CUR))
        m = st.columns(4)
        m[0].metric("P/E", fmt(c.get("pe")))
        m[1].metric("Price to book", fmt(price / bv if price and bv and bv > 0 else None, "x"))
        m[2].metric("Net margin", fmt(r["margin"], "%"))
        m[3].metric("Debt / equity", fmt(r["de"], "x", 2))
        n = len(c["sales"])
        labels = c.get("fy") if len(c.get("fy") or []) == n else [f"Y{i + 1}" for i in range(n)]
        trend = "  →  ".join(f"{labels[i]} {s:,.1f}" if s < 100 else f"{labels[i]} {s:,.0f}"
                             for i, s in enumerate(c["sales"]) if s is not None)
        gtxt = " · ".join(f"{g:+.0f}%" for g in r["growth"])
        st.write(f"**Revenue ({CUR}m):** {trend}  |  **Yearly growth:** {gtxt}  |  "
                 f"**Net profit:** {big_money(c.get('np'), CUR)}")
        for note in (c.get("assets_note"), c.get("cfo_note")):
            if note:
                st.caption(note)
        if c.get("model"):
            st.markdown("**How the business makes money**\n\n" + c["model"])
            st.markdown("**Revenue drivers**\n\n" + "\n".join(f"- {d}" for d in c["drivers"]))
            st.markdown(f"**Watch out:** {c['watch']}  \n[{MK['src_label']}]({c['src']})")
        elif c.get("summary"):
            with st.expander("What the company does"):
                st.write(c["summary"])


def show_results(rows):
    rows.sort(key=sort_key)
    groups = {0: [], 1: [], 2: [], 3: []}
    for row in rows:
        groups[min(len(row[1]["fails"]), 3)].append(row)
    k = st.columns(4)
    k[0].metric("Pass every filter", f"{len(groups[0])} of {len(rows)}")
    k[1].metric("Miss by one", len(groups[1]))
    k[2].metric("Miss by two", len(groups[2]))
    k[3].metric("Miss three or more", len(groups[3]))
    st.markdown("### Pass every filter")
    if not groups[0]:
        st.info("Nothing passes with these settings. Loosen one filter in the sidebar.")
    for c, r in groups[0]:
        show_card(c, r)
    for count, title in ((1, "Miss by one filter"), (2, "Miss by two filters")):
        if groups[count]:
            st.markdown(f"### {title}")
            for c, r in groups[count]:
                show_card(c, r)
    if groups[3]:
        with st.expander(f"Miss three or more filters ({len(groups[3])})"):
            st.dataframe(pd.DataFrame([{"Company": c["n"], "Misses": ", ".join(r["fails"])} for c, r in groups[3]]),
                         hide_index=True)


# ---------- page ----------
st.title("Hidden Compounders Screener - US & UK")
st.write(f"Find {'US' if MK['code'] == 'US' else 'UK'} small and mid caps in niche, monopoly or oligopoly businesses. "
         f"Prices, profit and market cap are shown in {'US dollars' if MK['code'] == 'US' else 'pounds sterling'}. "
         "Set your own rules in the sidebar and the list updates.")

tab1, tab2, tab3 = st.tabs(["Researched shortlist", "Screen your own stocks", "How it works"])

with tab1:
    shortlist = CURATED[MK["code"]]
    with st.spinner("Getting live prices"):
        try:
            quotes = fetch_quotes(tuple(c["t"] + MK["suffix"] for c in shortlist))
        except Exception:
            quotes = {}
    if quotes:
        st.caption(f"{len(shortlist)} niche, monopoly and oligopoly companies. Live prices from Yahoo Finance for "
                   f"{len(quotes)} of {len(shortlist)}, refreshed every 15 minutes; market cap and P/E are worked out "
                   "from the live price. Figures from each company's latest four annual reports.")
    else:
        st.caption(f"{len(shortlist)} niche, monopoly and oligopoly companies. Live prices are not available right now, "
                   "so prices are stored values from 2026 research and may be out of date. "
                   "Figures from each company's latest four annual reports.")
    rows = []
    for c in shortlist:
        q = quotes.get(c["t"] + MK["suffix"])
        if q:
            c = dict(c, price=q["price"], prev=q["prev"], live=True)
        item = with_valuation(c)
        rows.append((item, evaluate(item, FILTERS)))
    show_results(rows)

with tab2:
    st.caption(f"Type {MK['exchange']} separated by commas. Data comes live from Yahoo Finance, "
               "so it can be slow and some symbols may not load.")
    raw = st.text_area("Tickers", MK["example"], key=f"tickers_{MK['code']}")
    if st.button("Screen these stocks", type="primary"):
        symbols = [s for s in (to_symbol(x, MK) for x in raw.replace("\n", ",").split(",")) if s][:25]
        rows, errors = [], []
        bar = st.progress(0.0, "Fetching data")
        for i, sym in enumerate(symbols):
            try:
                c = dict(fetch_company(sym), live=True)
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
        f"""
**What the filters test**

- **Size:** market cap inside your range ({CUR}m). Defaults: $300m to $10bn for the US, £50m to £5bn for the UK.
- **Growth:** revenue grew by at least your percentage in every one of the last three years.
- **Margin:** latest net profit divided by latest revenue.
- **Debt:** borrowings (including leases where the source counts them) divided by shareholders' equity.
- **Assets:** total assets rose every year.
- **Cash flow:** operating cash flow is higher than two years ago, or up every year in strict mode.
- **P/E:** a rough check on whether the price is still reasonable.
- **Rare businesses:** monopoly, oligopoly and rare-niche companies on the shortlist may pass with a lower margin (12% by default).

**Currencies**

US stocks are shown in US dollars and UK stocks in pounds. Yahoo quotes London shares in pence, so the app divides by
100 to show pounds. If a London-listed company reports in another currency (some report in dollars), its figures are
converted into pounds at today's exchange rate.

**Intrinsic value**

A simple discounted cash flow on the latest net profit. Profit grows at the company's three-year revenue growth rate
(capped, 15% by default) for five years, slows to the long-term rate over the next five, and is discounted at 12%.
You can change all three numbers in the sidebar. It is a rough guide, not a price target: it ignores debt, cash and
how much the company must reinvest.

Commodity businesses such as metals, bulk chemicals, oil and gas, and paper are left out of the live search.

**Data:** the shortlist uses annual reports (SEC filings for US companies, Stock Analysis for UK companies).
Live search uses Yahoo Finance. Each company's own fiscal year is used, so years do not always line up.

This is a research tool, not investment advice. Check the latest filings before investing.
"""
    )

st.caption("Built by Tejas Sharma.")
