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
  "rare": true,
  "price": 1582,
  "bv": 333,
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
  "model": "CARE is one of the three big credit rating agencies in India. When a company wants a bank loan or wants to sell bonds, lenders and investors need an independent opinion on whether it can repay, and rules require most such debt to be rated. The borrower pays CARE a fee for the first rating and then a smaller surveillance fee every year the debt stays outstanding, so a large part of the income repeats. The business needs almost no factories or stock: the main cost is analysts' salaries, which is why over a third of revenue turns into profit. New rivals struggle because a rating is only worth something if investors and the regulator trust the name behind it, and that trust takes decades to build.",
  "drivers": [
   "Volume of corporate bonds issued and bank loans given",
   "Yearly surveillance fees on debt it has already rated",
   "Analytics and advisory arms, plus rating subsidiaries in other countries"
  ],
  "watch": "Earnings follow the credit cycle; a slow year for bond issuance hits new-rating fees.",
  "src": "https://www.screener.in/company/CARERATING/consolidated/"
 },
 {
  "n": "ICRA",
  "t": "ICRA",
  "moat": "Oligopoly",
  "rare": true,
  "price": 4499,
  "bv": 1233,
  "cap": 4346,
  "pe": 21.6,
  "roce": 23.0,
  "sales": [
   403,
   446,
   498,
   600
  ],
  "np": 183,
  "bor": 18,
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
  "model": "ICRA is the Indian arm of Moody's and another of the three big rating agencies. Its rating business works the same way as CARE's: borrowers pay an upfront fee and then a yearly surveillance fee. Its second business, ICRA Analytics, does research, data and risk-model work that Moody's group companies and banks outsource to it. That income is steadier because it does not depend on how much debt is raised in a given year. The Moody's name and rating methods give it credibility that a newcomer could not buy.",
  "drivers": [
   "Debt issuance and bank lending volumes",
   "Surveillance fees on the existing rated book",
   "Outsourced analytics and data work for the Moody's group and banks"
  ],
  "watch": "Growth was only just above 10% in two of the last three years.",
  "src": "https://www.screener.in/company/ICRA/consolidated"
 },
 {
  "n": "eMudhra",
  "t": "EMUDHRA",
  "moat": "Oligopoly",
  "rare": true,
  "price": 353,
  "bv": 118,
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
  "model": "A digital signature certificate is the electronic version of a signed and stamped paper. In India you need one for company filings, tax audits, government tenders and more. Only government-licensed certifying authorities can issue them, and eMudhra is the largest. It sells certificates through a wide network of partners, and each one expires after one to three years, so customers come back to renew. Its second and faster-growing business sells software to banks, governments and large companies for digital identity, e-signing and encryption, in India and overseas. The licence, the security audits and the international accreditations it holds take years to obtain, which keeps the number of serious competitors small.",
  "drivers": [
   "Certificate sales and renewals driven by tax, company-law and tender filings",
   "Enterprises and governments moving to paperless signing and digital identity",
   "Overseas expansion, partly through buying other companies"
  ],
  "watch": "Net margin is 15.7%, barely over the 15% line, and part of the growth is bought through acquisitions.",
  "src": "https://www.screener.in/company/EMUDHRA/consolidated"
 },
 {
  "n": "SJS Enterprises",
  "t": "SJS",
  "moat": "Niche",
  "rare": true,
  "price": 2100,
  "bv": 309,
  "cap": 6776,
  "pe": 33.0,
  "roce": 28.6,
  "sales": [
   433,
   628,
   760,
   955
  ],
  "np": 172,
  "bor": 23,
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
  "model": "SJS makes the parts of a vehicle or appliance that carry its look and brand: logos and badges, dashboard dials and overlays, chrome-plated trim, decorative films and, more recently, cover glass for large touchscreens. Makers of two-wheelers, cars and home appliances pay per part for the whole life of a model. SJS is designed into a model with the customer long before launch, so once approved it is rarely replaced midway. As vehicles become more premium, the value of decorative parts per vehicle rises, and SJS has bought two companies (chrome plating and in-mould parts) so it can sell more per vehicle. Few rivals offer the whole range under one roof. This is the closest match to Pricol on the list.",
  "drivers": [
   "More decorative content per vehicle as models go premium",
   "Winning more business from passenger-car makers",
   "New products such as display cover glass, plus exports"
  ],
  "watch": "Tied to auto production volumes, and a small number of large customers bring most of the sales.",
  "src": "https://www.screener.in/company/SJS/consolidated/"
 },
 {
  "n": "Latent View Analytics",
  "t": "LATENTVIEW",
  "moat": "Niche",
  "rare": false,
  "price": 202,
  "bv": 90.0,
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
  "model": "Latent View helps large companies make decisions from their data. It builds dashboards, forecasting models and AI tools for marketing, supply-chain and finance teams. Clients, mostly big US technology companies, pay for teams of analysts by time or by project. Most of the work is done from India, so the company earns the gap between US billing rates and Indian salaries. Clients stay because its teams become part of their daily work, but this is a people business that others can copy, and a handful of clients bring most of the revenue.",
  "drivers": [
   "Data and AI budgets of a few very large clients",
   "Selling more services into existing accounts",
   "Acquisitions that add new industries"
  ],
  "watch": "A services business that depends heavily on its top clients, so the moat is thin.",
  "src": "https://www.screener.in/company/LATENTVIEW/consolidated/"
 },
 {
  "n": "Supriya Lifescience",
  "t": "SUPRIYA",
  "moat": "Niche",
  "rare": true,
  "price": 862,
  "bv": 149,
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
  "model": "Supriya makes the active ingredient, the chemical that actually does the work, for a small number of established medicines. It sells that ingredient to drug companies, which turn it into tablets, syrups and injections. It focuses on molecules where only a few factories in the world are approved, such as chlorpheniramine (anti-allergy), ketamine (anaesthetic) and salbutamol (asthma), and it is among the largest suppliers of these globally. It makes many of its own starting materials, which protects its margin. Most of its output is exported. A drug maker has to go back to the regulator to change its ingredient supplier, so customers rarely switch.",
  "drivers": [
   "Share gains in regulated markets such as Europe and the US",
   "New molecules and contract manufacturing deals",
   "New factory capacity coming on stream"
  ],
  "watch": "Drug ingredients are the nearest thing to a commodity on this list. Price, book value and market cap here are my estimates from late-October figures, not taken directly from Screener.",
  "src": "https://www.screener.in/company/SUPRIYA/consolidated/"
 },
 {
  "n": "Sika Interplant Systems",
  "t": "SIKA",
  "moat": "Niche",
  "rare": true,
  "price": 883,
  "bv": 77.9,
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
  "model": "Sika is a Bengaluru engineering company that works only for aerospace and defence. It designs and builds engineered systems for aircraft, ships and land platforms, makes electrical wiring assemblies, repairs and overhauls aircraft components under tie-ups with the foreign companies that originally made them, and supplies imported components with local engineering added. Its customers are India's defence public-sector companies, the armed forces and foreign aerospace makers that must source part of their work in India. Approvals and certifications in this field take years, which keeps competition limited. Revenue arrives in lumps as orders are delivered.",
  "drivers": [
   "Defence indigenisation and offset orders",
   "Order flow from defence public-sector units and foreign makers",
   "Repair and overhaul work, which repeats"
  ],
  "watch": "Orders are lumpy: trailing twelve-month sales are below FY26, and the P/E is about 55.",
  "src": "https://www.screener.in/company/SIKA/consolidated/"
 },
 {
  "n": "Prevest Denpro",
  "t": "PREVEST",
  "moat": "Niche",
  "rare": true,
  "price": 413,
  "bv": 114,
  "cap": 495,
  "pe": 22.0,
  "roce": 24.2,
  "sales": [
   null,
   56,
   63,
   72
  ],
  "np": 20,
  "bor": 0,
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
  "model": "Prevest makes the consumable materials a dentist uses every day: filling materials, cements, impression materials, root-canal products and polishing and hygiene items, more than a hundred products in all. It sells under its own brand through dealers in India and distributors in many countries, and also manufactures for other brands. Dentists use these materials up and reorder them, so sales repeat. Its edge is price against European and American brands, and each country requires product registrations that take time for a new entrant to obtain.",
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
  "rare": true,
  "price": 116,
  "bv": 16.4,
  "cap": 10319,
  "pe": 19.7,
  "roce": 51.4,
  "sales": [
   401,
   449,
   537,
   616
  ],
  "np": 493,
  "bor": 11,
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
  "model": "IEX runs the marketplace where electricity is bought and sold for delivery the same day, the next day or a few weeks ahead. The sellers are power generators with spare output; the buyers are state distribution companies and large factories. IEX matches the bids and charges a small fee per unit to both the buyer and the seller. It never owns the power and needs almost no capital, which is why about 80% of revenue becomes profit. Buyers go where the sellers are and sellers go where the buyers are, so the largest exchange keeps getting most of the volume. It also owns part of the Indian Gas Exchange.",
  "drivers": [
   "More electricity traded on exchanges instead of long-term contracts",
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
  "rare": true,
  "price": 1062,
  "bv": 447,
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
  "model": "Nesco owns a large plot beside the Western Express Highway in Goregaon, Mumbai. On it sit the Bombay Exhibition Centre, the city's main venue for trade fairs, where organisers rent halls by the day, and an IT park whose buildings are rented to companies on multi-year leases. Nesco Foods caters to the events and offices. The land was bought decades ago, so there is little cost against the rent, and more than 40% of revenue becomes profit. Nobody can copy it because there is no comparable land left in Mumbai. It is now using the cash to build more towers and roadside amenities on expressways.",
  "drivers": [
   "Exhibition days booked and hall rates",
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
  "rare": false,
  "price": 213,
  "bv": 17.2,
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
  "model": "Ksolves is a small IT services company. Its engineers set up and maintain big-data software such as Apache Kafka and Spark, customise Salesforce and Odoo, and build AI tools, mainly for overseas clients who are billed for the engineers' time. Costs are Indian salaries and revenue is in dollars. It pays out most of its profit as dividends, which keeps its equity small and makes its return on capital look extremely high. There is nothing stopping other IT firms from offering the same services.",
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
  "rare": false,
  "price": 9538,
  "bv": 1845,
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
  "model": "Voltamp makes transformers, the equipment that steps electricity voltage up or down, at its plants in Vadodara. Unlike most rivals it sells mainly to private industry (factories, commercial buildings, data centres and renewable projects) and not to state utilities, so it gets paid faster and carries no debt. Each transformer is built to order. Copper and steel are the main costs and are largely passed on in the price, so profit depends on how strong demand is and how full its factories are.",
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
  "rare": true,
  "price": 1275,
  "bv": 95.6,
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
  "model": "Paras makes highly specialised equipment for defence and space: large precision optics such as mirrors and lenses for satellites and surveillance systems, defence electronics and control consoles, and shielding that protects equipment from electromagnetic pulses. Its customers are India's space agency, defence research labs and defence public-sector companies. For some of its optics there is no other Indian maker, so it competes mainly with imports. It is paid project by project and the government pays slowly, which is why cash flow jumps around.",
  "drivers": [
   "Defence and space programme orders",
   "Optical and electro-optic systems",
   "Drones and newer products"
  ],
  "watch": "P/E of about 100, market cap just over ₹10,000 Cr, and cash flow is uneven.",
  "src": "https://www.screener.in/company/PARAS/consolidated/"
 },
 {
  "n": "Raghav Productivity Enhancers",
  "t": "RPEL",
  "moat": "Niche",
  "rare": true,
  "price": 1977,
  "bv": 61.3,
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
  "model": "When scrap is melted into steel in an induction furnace, the furnace wall has to be lined with a heat-resistant material that wears out and is replaced every few days. Raghav makes this lining material, called silica ramming mass, from quartz in Rajasthan and is the largest maker in the world. It sells to steel plants in India and exports to many countries. Because the product is used up constantly, orders repeat. Its pitch is that its material lasts longer per lining, so the customer saves on downtime and is willing to pay more than for unbranded material from small local suppliers.",
  "drivers": [
   "Steel made in induction furnaces",
   "Customers switching from unbranded material",
   "Exports"
  ],
  "watch": "P/E of 129, so a lot of future growth is already in the price. Sales dipped in FY24.",
  "src": "https://www.screener.in/company/RPEL/consolidated/"
 },
 {
  "n": "Shilchar Technologies",
  "t": "SHILCTECH",
  "moat": "Niche",
  "rare": false,
  "price": 3431,
  "bv": 464,
  "cap": 3919,
  "pe": 31.5,
  "roce": 50.7,
  "sales": [
   280,
   397,
   623,
   652
  ],
  "np": 158,
  "bor": 0,
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
  "model": "Shilchar makes medium-sized transformers in Vadodara, mainly the kind used in solar and wind farms, and exports a large share of them. Each unit is made to order and it is known for quick delivery. It uses little capital for the sales it generates, which gives it a very high return on capital. Demand rises and falls with renewable project orders in India and abroad.",
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
  "rare": false,
  "price": 915,
  "bv": 254,
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
  "model": "Jyoti makes white wood glue under the Euro 7000 brand, the glue carpenters use to stick laminate and plywood. The market is dominated by one giant brand, and Jyoti is the second-largest in the retail segment. Carpenters choose the glue, so Jyoti wins them with a reward-points scheme and sells through hardware dealers. The product is simple to make and needs little capital, so the money goes into the dealer network and the carpenter scheme.",
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
  "rare": true,
  "price": 876,
  "bv": 177,
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
  "model": "MapmyIndia has built its own digital map of India over more than two decades, covering roads, addresses and places. It earns by licensing that map and the software around it. Car makers pay per vehicle for built-in navigation and connected features. Delivery, e-commerce and finance companies, and government departments, pay subscriptions or usage fees for maps and location software. It also sells tracking devices, which earn a lower margin. A detailed map of India is very hard to recreate, and Indian rules on map data favour a domestic owner.",
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
  "rare": false,
  "price": 2259,
  "bv": 411,
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
  "model": "Publishers of academic journals and textbooks outsource their production work (editing, typesetting and converting to digital formats) to MPS. It also sells the software platforms publishers use to host and sell content, and builds e-learning courses for companies. It is paid per page, per project or by subscription. Publishers rarely change supplier once their workflow is set up. Much of its growth comes from buying smaller firms and improving their margins.",
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
  "rare": true,
  "price": 986,
  "bv": 93.1,
  "cap": 5679,
  "pe": 48.7,
  "roce": 26.6,
  "sales": [
   470,
   509,
   508,
   571
  ],
  "np": 96,
  "bor": 71,
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
  "model": "Shivalik makes two small but critical parts. The first is thermostatic bimetal, a strip of two bonded metals that bends when it heats up: it is what trips a circuit breaker or switches off an iron. The second is shunt resistors, precision parts that measure current inside smart electricity meters and electric-vehicle batteries. It sells to switchgear, meter and auto-parts makers in India and abroad. Only a handful of companies in the world make these, and a customer takes years to approve a new supplier.",
  "drivers": [
   "Smart meter rollout",
   "Electric vehicles",
   "Switchgear demand and exports"
  ],
  "watch": "Sales were flat in FY25 and the P/E is about 49.",
  "src": "https://www.screener.in/company/SBCL/consolidated/"
 },
 {
  "n": "Shanthi Gears",
  "t": "SHANTIGEAR",
  "moat": "Niche",
  "rare": false,
  "price": 521,
  "bv": 58.6,
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
  "model": "Shanthi Gears, part of the Murugappa group, makes custom industrial gearboxes and gears in Coimbatore for steel, cement, power and other heavy industries. Each gearbox is designed for a specific machine, and the company also earns from servicing and replacing them. Orders depend on how much heavy industry is spending on new plants.",
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
  "rare": true,
  "price": 673,
  "bv": 94.4,
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
  "model": "Saregama owns one of India's largest catalogues of film and non-film songs, going back many decades. Each time one of its songs is streamed, used in a video or an advertisement, or broadcast, it collects a licence fee. It spends part of that income buying the music of new films to keep the catalogue fresh. It also makes films and series and runs live events, which earn lower margins. Only a few labels own most Indian music, and old hits cannot be recreated.",
  "drivers": [
   "Payouts from streaming and video platforms",
   "New music acquisitions",
   "Films, series and live events"
  ],
  "watch": "Above the ₹10,000 Cr ceiling and sales fell in FY26.",
  "src": "https://www.screener.in/company/SAREGAMA/consolidated/"
 },
 {
  "n": "Esab India",
  "t": "ESABINDIA",
  "moat": "Oligopoly",
  "rare": true,
  "price": 5166,
  "bv": 323,
  "cap": 7953,
  "pe": 39.6,
  "roce": 64.7,
  "sales": [
   1091,
   1243,
   1373,
   1508
  ],
  "np": 207,
  "bor": 3,
  "assets": [
   474,
   551,
   649,
   699
  ],
  "cfo": [
   129,
   141,
   199,
   181
  ],
  "model": "Esab sells what is needed to weld and cut metal. Most of its income is from consumables (electrodes, wires and fluxes) that are used up every time two pieces of metal are joined, so customers reorder constantly. It also sells welding and cutting machines. Buyers are shipyards, railways, construction and auto companies and thousands of fabrication workshops, reached through dealers. It also earns service income for engineering work it does for its global parent. Organised welding in India is shared among a handful of brands, and welders tend to stay with the brand they trust for safety-critical joints.",
  "drivers": [
   "Infrastructure, railways, shipbuilding and factory construction",
   "Shift from unbranded to branded consumables",
   "Service income from the global parent"
  ],
  "watch": "Net margin is 13.7%, in the 12–15% band. Revenue growth slipped to 9.8% in FY26 and the P/E is about 40.",
  "src": "https://www.screener.in/company/ESABINDIA/"
 },
 {
  "n": "Disa India",
  "t": "DISAQ",
  "moat": "Monopoly",
  "rare": true,
  "price": 11115,
  "bv": 2031,
  "cap": 1616,
  "pe": 32.0,
  "roce": 26.6,
  "sales": [
   262,
   329,
   390,
   425
  ],
  "np": 54,
  "bor": 0,
  "assets": [
   355,
   420,
   437,
   475
  ],
  "cfo": [
   39,
   56,
   33,
   13
  ],
  "model": "Foundries make metal castings by pouring molten metal into sand moulds. Disa, part of a Danish group, supplies the machines that make those moulds, the plant that prepares the sand, the shot-blasting machines that clean the castings and the filters that control dust. It sells complete lines to foundries that serve the auto, tractor and railway industries, and then earns from spare parts and service for decades afterwards. For high-speed moulding lines it has very few rivals in India.",
  "drivers": [
   "Foundries adding capacity for autos, tractors and railways",
   "Spare parts and service on installed machines",
   "Exports to group companies"
  ],
  "watch": "Net margin is 12.7%, in the 12–15% band. Growth slowed to 9% in FY26 and cash flow has fallen for two years.",
  "src": "https://www.screener.in/company/DISAQ/consolidated/"
 },
 {
  "n": "CMS Info Systems",
  "t": "CMSINFO",
  "moat": "Oligopoly",
  "rare": true,
  "price": 212,
  "bv": 148,
  "cap": 3388,
  "pe": 11.0,
  "roce": 17.9,
  "sales": [
   1915,
   2265,
   2425,
   2487
  ],
  "np": 303,
  "bor": 0,
  "assets": [
   2101,
   2659,
   3120,
   3238
  ],
  "cfo": [
   407,
   440,
   483,
   390
  ],
  "model": "Banks outsource the handling of physical cash. CMS vans load cash into ATMs, collect cash from shops and move it between bank branches. CMS also runs entire ATM networks for banks, including the software and remote monitoring. It is paid per ATM per month or per pickup. Two companies handle most of this market, because it needs a nationwide fleet of armoured vans, vaults, guards and insurance that a newcomer cannot build quickly. Growth is slow because the number of ATMs in India is no longer rising much.",
  "drivers": [
   "Banks outsourcing more ATM and cash operations",
   "Retail cash pickups",
   "Remote monitoring and ATM software"
  ],
  "watch": "Net margin is 12.2%, in the 12–15% band. Growth has dropped to under 3% and cash flow fell in FY26. Cheapest P/E on the list.",
  "src": "https://www.screener.in/company/CMSINFO/consolidated"
 },
 {
  "n": "Control Print",
  "t": "CONTROLPR",
  "moat": "Oligopoly",
  "rare": true,
  "price": 589,
  "bv": 294,
  "cap": 942,
  "pe": 28.1,
  "roce": 16.4,
  "sales": [
   304,
   359,
   425,
   482
  ],
  "np": 44,
  "bor": 7,
  "assets": [
   374,
   434,
   508,
   581
  ],
  "cfo": [
   55,
   50,
   50,
   50
  ],
  "model": "Every packaged product has to carry a batch number, an expiry date and a price. Control Print makes the printers fitted on factory lines that print these, and the inks and fluids those printers use up every day. The printer is sold once; the fluids are bought for as long as the printer runs, and that is where most of the profit is. It is the only Indian company among the four that dominate this market in India. Profit has fallen recently because it is spending on new packaging and overseas businesses.",
  "drivers": [
   "More printers installed in factories",
   "Ink and fluid sales on the installed base",
   "New packaging and overseas ventures"
  ],
  "watch": "Net margin has fallen to 9%, below even the 12% floor, and cash flow has been flat for three years.",
  "src": "https://www.screener.in/company/CONTROLPR/consolidated"
 },
 {
  "n": "Tips Music",
  "t": "TIPSMUSIC",
  "moat": "Oligopoly",
  "rare": true,
  "price": 807,
  "bv": 25.4,
  "cap": 10264,
  "pe": 45.2,
  "roce": 118,
  "sales": [
   187,
   242,
   311,
   376
  ],
  "np": 217,
  "bor": 5,
  "assets": [
   193,
   339,
   339,
   362
  ],
  "cfo": [
   81,
   233,
   120,
   197
  ],
  "model": "Tips owns a large catalogue of Hindi, Punjabi and regional film songs, including many 1990s hits. It licenses these songs to streaming apps, video platforms and broadcasters, often with a guaranteed minimum payment. One more stream of an old song costs Tips nothing, which is why more than half of revenue becomes profit. Each year it spends part of its income buying new songs to keep the catalogue growing. Only a few labels own most Indian music.",
  "drivers": [
   "Payouts from streaming and video platforms",
   "Growth of paid streaming in India",
   "New song acquisitions"
  ],
  "watch": "Market cap is just over ₹10,000 Cr, the P/E is 45, and cash flow swings with the timing of licensing deals.",
  "src": "https://www.screener.in/company/TIPSMUSIC"
 }
]''')

COMMODITY_WORDS = [
    "steel", "aluminum", "copper", "metals & mining", "coal", "oil & gas", "gold", "silver",
    "chemicals", "agricultural inputs", "paper", "lumber", "building materials", "textile",
    "farm products", "sugar", "coking",
]


# ---------- screening logic ----------
def money(v):
    """Rupee amount: no decimals from 1,000 upwards, two decimals below."""
    if v is None or v != v:
        return "n/a"
    return f"₹{v:,.0f}" if abs(v) >= 1000 else f"₹{v:,.2f}"


def intrinsic_value(c, a):
    """Simple DCF on the latest net profit. Returns value per share, or None."""
    sales = [s for s in c["sales"] if s]
    profit, cap, price = c.get("np"), c.get("cap"), c.get("price")
    if len(sales) < 2 or not profit or profit <= 0 or not cap or not price:
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
    shares = cap / price  # crore shares
    return total / shares


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
    if f["assets"]:
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
        "bv": info.get("bookValue"),
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


def fmt(v, suffix="", digits=1):
    return "n/a" if v is None else f"{v:,.{digits}f}{suffix}"


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
        m[0].metric("Live price" if c.get("live") else "Price", money(price), change)
        m[1].metric("Intrinsic value", money(iv), gap)
        m[2].metric("Book value per share", money(bv))
        m[3].metric("Market cap", "n/a" if c.get("cap") is None else f"₹{c['cap']:,.0f} Cr")
        m = st.columns(4)
        m[0].metric("P/E", fmt(c.get("pe")))
        m[1].metric("Price to book", fmt(price / bv if price and bv and bv > 0 else None, "x"))
        m[2].metric("Net margin", fmt(r["margin"], "%"))
        m[3].metric("Debt / equity", fmt(r["de"], "x", 2))
        n = len(c["sales"])
        labels = YEARS[-n:] if c.get("moat") else [f"Y{i + 1}" for i in range(n)]
        trend = "  →  ".join(f"{labels[i]} {s:,.0f}" for i, s in enumerate(c["sales"]) if s is not None)
        gtxt = " · ".join(f"{g:+.0f}%" for g in r["growth"])
        st.write(f"**Revenue (₹ Cr):** {trend}  |  **Yearly growth:** {gtxt}")
        if c.get("model"):
            st.markdown("**How the business makes money**\n\n" + c["model"])
            st.markdown("**Revenue drivers**\n\n" + "\n".join(f"- {d}" for d in c["drivers"]))
            st.markdown(f"**Watch out:** {c['watch']}  \n[Check the numbers on Screener]({c['src']})")
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
        st.caption(f"{len(CURATED)} niche, monopoly and oligopoly companies. Live price and market cap from Yahoo Finance "
                   f"for {len(quotes)} of {len(CURATED)}, refreshed every 15 minutes. "
                   "Annual figures to March 2026.")
    else:
        st.caption(f"{len(CURATED)} niche, monopoly and oligopoly companies. Live prices are not available right now, "
                   "so price, market cap and P/E are from mid-November 2026. Annual figures to March 2026.")
    rows = []
    for c in CURATED:
        item = dict(c, debt=c["bor"], equity=c["bv"] * c["cap"] / c["price"])
        q = quotes.get(c["t"])
        if q:
            item["price"], item["prev"], item["live"] = q["price"], q["prev"], True
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
        """
**What the filters test**

- **Size:** market cap inside your range.
- **Growth:** revenue grew by at least your percentage in every one of the last three years.
- **Margin:** latest net profit divided by latest revenue.
- **Debt:** borrowings divided by shareholders' equity.
- **Assets:** total assets rose every year.
- **Cash flow:** operating cash flow is higher than two years ago, or up every year in strict mode.
- **P/E:** a rough check on whether the price is still reasonable.
- **Rare businesses:** monopoly, oligopoly and rare-niche companies on the shortlist may pass with a lower margin (12% by default).

**Intrinsic value**

A simple discounted cash flow on the latest net profit. Profit grows at the company's three-year revenue growth rate
(capped, 15% by default) for five years, slows to the long-term rate over the next five, and is discounted at 12%.
You can change all three numbers in the sidebar. It is a rough guide, not a price target: it ignores debt, cash and
how much the company must reinvest.

Commodity businesses such as metals, bulk chemicals, sugar, cement and yarn are left out.

**Data:** the shortlist uses annual results from Screener.in. Live search uses Yahoo Finance.

This is a research tool, not investment advice. Check the latest filings before investing.
"""
    )

st.caption("Built by Tejas Sharma.")
