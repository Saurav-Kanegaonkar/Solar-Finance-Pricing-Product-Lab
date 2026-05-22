# Data Sources

This folder contains deterministic synthetic data for a residential solar finance pricing and product workbench.

The data is modeled on common residential solar finance workflows: dealer rate cards, loan and third-party-owned product economics, state expansion research, competitor offer tracking, pricing-platform QA, and S&OP follow-up queues.

It does not represent real company performance, customer credit files, dealer contracts, or private pricing assumptions.

- `pricing_scenarios.csv`: Scenario-level product economics with NPV, IRR, margin gap, competitor gap, and recommended action.
- `competitive_intelligence.csv`: Synthetic competitor pricing, dealer incentive, and proposal win risk records.
- `platform_qa.csv`: Pricing-platform test results and data-quality checks by workflow area.
- `stakeholder_actions.csv`: Follow-up queue for pricing review, S&OP, product council, and QA standups.
- `analysis/outputs/assumption_ledger.csv`: State-level public-market anchors used by the synthetic model.
- `analysis/outputs/sensitivity_tests.csv`: Directional stress tests for funding cost, dealer fee, competitor matching, and production downside.
- `analysis/outputs/launch_gate_queue.csv`: New-product launch gates with readiness, margin, QA, and next-step signals.

The generator uses a fixed random seed. Ranges are documented in `analysis/methodology.md` and implemented in `scripts/score_operating_data.py`. Public-market anchors are used only to shape plausible state assumptions. Scenario-level economics are synthetic.
