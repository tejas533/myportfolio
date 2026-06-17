# DCF Valuation Tool

A modern, interactive Discounted Cash Flow (DCF) valuation application built with Streamlit, Python, and `yfinance`. It calculates the intrinsic value, Margin of Safety (MOS) buy price, and growth forecasts for US and Indian stocks using live market and financial statement data.

## Features
- **Ticker Auto-Resolution**: Supports US tickers (e.g., `AAPL`, `MSFT`) and Indian exchange tickers (e.g., `RELIANCE.NS`, `TCS.NS`, `500325.BO`).
- **Interactive DCF Parameters**: Customize forecast years, discount rate (WACC), terminal growth rate, and margin of safety.
- **Historical Analysis & Forecasting**: Computes historical compound annual growth rate (CAGR) of Free Cash Flows (FCF) and forecasts future cash flows with recovery handling for negative FCFs.
- **Valuation Dashboard**: Clearly displays Intrinsic Value, MOS Buy Price, and potential Upside/Downside percent.

---

## 🚀 How to Run Locally

### 1. Set Up Your Environment
Navigate to this project directory in your terminal and create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit App
```bash
streamlit run app.py
```

---

## 🌐 How to Host on GitHub & Streamlit Community Cloud

Streamlit apps require a Python server, so they **cannot** be hosted directly as static pages on GitHub Pages. Instead, the best and easiest way to host it for free is using **Streamlit Community Cloud**, which links to your GitHub repository.

### Step 1: Push Your Code to GitHub
1. Go to [GitHub](https://github.com/) and create a new public repository (e.g., `dcf-valuation-app`).
2. Run the following commands in your local terminal:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of DCF Valuation App"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/dcf-valuation-app.git
   git push -u origin main
   ```
   *(Be sure to replace `YOUR_GITHUB_USERNAME` and the repository name with your actual details).*

### Step 2: Deploy to Streamlit Community Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click the **"New app"** button.
3. Select your repository (`dcf-valuation-app`), the branch (`main`), and set the main file path to `app.py`.
4. Click **"Deploy!"** 🚀

Streamlit will set up the container, install the dependencies listed in `requirements.txt`, and deploy your live app. Whenever you `git push` new changes to GitHub, your live website will automatically update!
