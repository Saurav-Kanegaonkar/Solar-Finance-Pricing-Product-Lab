# Methodology

The model is deterministic and synthetic. It is designed to be interview-safe because it does not use private rate cards, dealer contracts, customer credit files, or fund economics.

State-level assumptions use public-market structure as anchors: residential electric-rate ranges, production-yield bands, policy friction, and market maturity. The scenario outputs remain synthetic because actual dealer terms, competitor offers, credit policy, and investor economics are private.

Loan scenarios compute amortizing customer payments from financed amount, APR, dealer fee, and term. Investor cash flows subtract servicing cost and loss reserve, then calculate NPV at funding cost and IRR.

Lease and PPA scenarios model owner cash flows using project cost, tax-credit proxy, SREC or REC value, escalator, service cost, and production degradation. The model calculates monthly payment or price per kWh, NPV, IRR, and margin gap.

Sensitivity tests are directional pricing-review checks. They estimate the margin and NPV effect of funding-cost movement, dealer incentive changes, competitor repricing, and production downside. They are not represented as audited investor cash-flow recalculations.

Priority score increases when margin gap is negative, competitor gap is high, QA defects are open, channel complexity is high, or state readiness is weak.
