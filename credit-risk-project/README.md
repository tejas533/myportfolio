# Credit Risk and Lending Profitability Analysis

**Author:** Tejas Sharma

Which loans are worth funding? This project analyses about 164,000 completed Lending Club personal loans to find what
drives default, estimate each loan's probability of default (PD), and turn that into a lending rule based on expected profit.

## Results

| On 49,139 test loans the model never saw | Fund every loan | Model policy |
|---|---|---|
| Loans funded | 49,139 | 38,998 (79%) |
| Amount lent | $642.7m | $521.8m |
| Bad loan rate | 18.3% | 16.5% |
| Actual profit | $34.0m | $37.6m |
| Return on amount lent | 5.3% | 7.2% |

- **Drivers of default:** interest rate, loan size relative to income, debt-to-income ratio, a 60-month term,
  small business purpose and credit card utilisation raise risk; higher income and longer credit records lower it.
- **Model quality:** logistic regression with AUC 0.70 (Gini 0.41) on unseen loans, and predicted default rates
  that closely match actual rates in every risk decile.
- **The riskiest loans were underpriced:** the riskiest tenth defaulted at about 41% and returned about 3% on the
  amount lent, against around 6.5% for mid-risk loans.
- **Lending on expected profit wins:** funding only loans with positive expected profit earned $3.6m (11%) more
  while lending $121m less. The gain grows as the assumed loss given default rises.

## Method

1. **SQL exploration:** loans loaded into SQLite and grouped by term, interest rate band, debt-to-income band,
   purpose and income verification.
2. **PD model:** logistic regression on application data, trained on 70% of loans and tested on 30%.
3. **Expected profit per loan:** (1 − PD) × (interest received − 4% cost of funds) − PD × 60% loss given default × loan amount.
4. **Policy test:** fund every loan vs fund only loans with positive expected profit, scored on actual outcomes.
   Loss given default is tested at 40%, 60% and 80%.

## Limitations

- One loss given default for all loans and no operating costs.
- Only approved loans are in the data, so declined applicants are never seen.
- No application dates, so the train/test split is random rather than by time.

## How to run

```bash
pip install -r requirements.txt
jupyter notebook Credit_Risk_Lending_Analysis.ipynb
```

The notebook downloads the data itself from the
[H2O consumer loan data set](https://github.com/h2oai/app-consumer-loan), a cleaned extract of Lending Club loans.
