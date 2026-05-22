# Data Dictionary

| File | Grain | Description |
| --- | --- | --- |
| `pricing_scenarios.csv` | State x channel x product scenario | Pricing inputs and modeled economics for loans, leases, PPAs, and prepaid leases. |
| `competitive_intelligence.csv` | Scenario x competitor check | Competitor price proxy, dealer incentive, and proposal win risk. |
| `platform_qa.csv` | Scenario x QA test area | Open pricing-platform defects, severity, owner, and data-quality score. |
| `stakeholder_actions.csv` | Scenario x action | Recommended follow-up, meeting venue, owner, due week, and estimated margin impact. |
| `analysis/outputs/rate_card_actions.csv` | Scenario | Highest-priority pricing and rate-card moves. |
| `analysis/outputs/market_expansion_queue.csv` | State | State readiness, average margin, competitor gap, and high-priority count. |
| `analysis/outputs/qa_readiness_queue.csv` | QA check | Highest-risk pricing-platform QA items. |
| `analysis/outputs/assumption_ledger.csv` | State | Public-market assumption anchors used to shape synthetic state scenarios. |
| `analysis/outputs/sensitivity_tests.csv` | Scenario x stress test | Directional pricing stress tests for rate-card review. |
| `analysis/outputs/launch_gate_queue.csv` | Product launch gate | Product readiness, QA risk, blocker, and next step. |

Key modeled fields:

- `npv`: Net present value of modeled investor cash flows at funding cost.
- `irr_pct`: Internal rate of return from modeled product cash flows.
- `contribution_margin_bps`: IRR less funding cost and risk reserve, expressed in basis-point style units.
- `margin_gap_bps`: Difference between contribution margin and modeled margin floor.
- `competitor_gap_bps`: Positive values indicate the scenario is less competitive than the synthetic market reference.
- `readiness_score`: Composite state and product readiness score.
- `priority_score`: Composite score used to rank pricing actions.
- `decision_signal`: Sensitivity-test result used to flag pass, reprice, or block conditions.
- `launch_gate`: New-product operating decision area for product council or S&OP review.
