# Methodology

The model is deterministic and synthetic. It is designed to be interview-safe because it does not use private rate cards, dealer contracts, customer credit files, or fund economics.

Loan scenarios compute amortizing customer payments from financed amount, APR, dealer fee, and term. Investor cash flows subtract servicing cost and loss reserve, then calculate NPV at funding cost and IRR.

Lease and PPA scenarios model owner cash flows using project cost, tax-credit proxy, SREC or REC value, escalator, service cost, and production degradation. The model calculates monthly payment or price per kWh, NPV, IRR, and margin gap.

Priority score increases when margin gap is negative, competitor gap is high, QA defects are open, channel complexity is high, or state readiness is weak.
