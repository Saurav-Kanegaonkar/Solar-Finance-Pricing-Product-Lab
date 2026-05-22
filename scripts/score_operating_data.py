import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ANALYSIS_DIR = ROOT / "analysis"
OUTPUT_DIR = ANALYSIS_DIR / "outputs"
SRC_DIR = ROOT / "src"

RNG = random.Random(42)


def money(value):
    return round(value, 2)


def pct(value):
    return round(value, 3)


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def npv(rate, cash_flows):
    return sum(cash / ((1 + rate) ** idx) for idx, cash in enumerate(cash_flows))


def irr(cash_flows):
    if not any(cash < 0 for cash in cash_flows) or not any(cash > 0 for cash in cash_flows):
        return 0.0
    low = -0.95
    high = 1.0
    for _ in range(80):
        mid = (low + high) / 2
        value = npv(mid, cash_flows)
        if value > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def loan_payment(principal, annual_rate, months):
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def weighted_choice(options):
    total = sum(weight for _, weight in options)
    point = RNG.uniform(0, total)
    running = 0
    for value, weight in options:
        running += weight
        if point <= running:
            return value
    return options[-1][0]


def build_scenarios():
    states = [
        {"state": "CA", "policy_score": 88, "yield": 1510, "utility_rate": 0.31, "nem_friction": 16},
        {"state": "AZ", "policy_score": 73, "yield": 1705, "utility_rate": 0.18, "nem_friction": 9},
        {"state": "TX", "policy_score": 66, "yield": 1515, "utility_rate": 0.15, "nem_friction": 8},
        {"state": "FL", "policy_score": 69, "yield": 1490, "utility_rate": 0.17, "nem_friction": 7},
        {"state": "NJ", "policy_score": 81, "yield": 1260, "utility_rate": 0.22, "nem_friction": 5},
        {"state": "NY", "policy_score": 77, "yield": 1190, "utility_rate": 0.24, "nem_friction": 6},
        {"state": "CO", "policy_score": 75, "yield": 1500, "utility_rate": 0.16, "nem_friction": 6},
        {"state": "NV", "policy_score": 71, "yield": 1730, "utility_rate": 0.16, "nem_friction": 10},
    ]
    products = [
        {"product": "Solar loan", "type": "Loan", "term": 25, "base_apr": 0.079, "base_fee": 0.115},
        {"product": "Solar plus storage loan", "type": "Loan", "term": 25, "base_apr": 0.084, "base_fee": 0.135},
        {"product": "Operating lease", "type": "Lease", "term": 25, "base_apr": 0.0, "base_fee": 0.075},
        {"product": "Levelized PPA", "type": "PPA", "term": 25, "base_apr": 0.0, "base_fee": 0.085},
        {"product": "Prepaid lease", "type": "Lease", "term": 20, "base_apr": 0.0, "base_fee": 0.05},
    ]
    channels = [
        {"channel": "Dealer partner", "complexity": 9, "volume_weight": 1.2},
        {"channel": "Installer platform", "complexity": 7, "volume_weight": 1.0},
        {"channel": "New homes", "complexity": 12, "volume_weight": 0.7},
        {"channel": "Direct homeowner", "complexity": 5, "volume_weight": 0.55},
    ]
    credit_bands = [
        {"credit_band": "Super prime", "loss": 0.007, "approval": 0.88, "cost_adj": -0.004},
        {"credit_band": "Prime", "loss": 0.014, "approval": 0.79, "cost_adj": 0.0},
        {"credit_band": "Near prime", "loss": 0.027, "approval": 0.62, "cost_adj": 0.011},
    ]
    dealer_tiers = [
        {"dealer_tier": "National", "rebate": 0.018, "defect": 0.75},
        {"dealer_tier": "Regional", "rebate": 0.012, "defect": 1.0},
        {"dealer_tier": "Emerging", "rebate": 0.006, "defect": 1.35},
    ]

    scenario_rows = []
    competitive_rows = []
    qa_rows = []
    action_rows = []
    scenario_id = 1

    for state in states:
        for product in products:
            for channel in channels:
                credit = weighted_choice(
                    [(credit_bands[0], 0.34), (credit_bands[1], 0.46), (credit_bands[2], 0.2)]
                )
                tier = weighted_choice(
                    [(dealer_tiers[0], 0.32), (dealer_tiers[1], 0.48), (dealer_tiers[2], 0.2)]
                )
                system_kw = RNG.uniform(6.2, 12.8)
                battery = "storage" in product["product"].lower() or RNG.random() < 0.28
                cost_per_watt = RNG.uniform(2.65, 3.55) + (0.38 if battery else 0)
                system_cost = system_kw * 1000 * cost_per_watt
                dealer_fee = max(0.02, product["base_fee"] + RNG.uniform(-0.018, 0.026) - tier["rebate"])
                funding_cost = 0.052 + credit["cost_adj"] + RNG.uniform(-0.004, 0.006)
                service_cost = RNG.uniform(310, 560) + (95 if battery else 0)
                annual_kwh = system_kw * state["yield"] * RNG.uniform(0.94, 1.06)
                margin_floor = 0.036 + credit["loss"] + RNG.uniform(0.0, 0.015)
                competitor_rate = 0.072 + credit["cost_adj"] + RNG.uniform(-0.011, 0.018)
                competitor_fee = dealer_fee + RNG.uniform(-0.025, 0.028)
                apr = max(0.039, product["base_apr"] + credit["cost_adj"] + RNG.uniform(-0.007, 0.012))
                escalator = weighted_choice([(0.0, 0.36), (0.0299, 0.42), (0.035, 0.22)])
                upfront_incentive = system_cost * (0.3 if product["type"] in {"Lease", "PPA"} else 0.0)
                rec_value = annual_kwh * RNG.uniform(0.006, 0.018) if state["state"] in {"NJ", "NY", "CA"} else annual_kwh * RNG.uniform(0.001, 0.006)

                if product["type"] == "Loan":
                    financed_amount = system_cost * (1 + dealer_fee)
                    customer_payment = loan_payment(financed_amount, apr, product["term"] * 12)
                    monthly_cash = customer_payment * 12
                    investor_cash_flows = [-financed_amount * (1 - dealer_fee)]
                    for year in range(1, product["term"] + 1):
                        defaults = financed_amount * credit["loss"] * (1.15 - min(year, 10) * 0.035)
                        investor_cash_flows.append(monthly_cash - service_cost - defaults)
                    product_irr = irr(investor_cash_flows)
                    product_npv = npv(funding_cost, investor_cash_flows)
                    contribution_margin = (product_irr - funding_cost - credit["loss"]) * 10000
                    rate_card = f"{apr * 100:.2f}% APR, {dealer_fee * 100:.1f}% dealer fee"
                    customer_savings = annual_kwh * state["utility_rate"] - customer_payment * 12
                elif product["product"] == "Prepaid lease":
                    prepaid = system_cost * RNG.uniform(0.5, 0.64)
                    investor_cash_flows = [-system_cost]
                    investor_cash_flows[0] += upfront_incentive + prepaid
                    for year in range(1, product["term"] + 1):
                        investor_cash_flows.append(annual_kwh * state["utility_rate"] * 0.18 + rec_value - service_cost * 0.38)
                    product_irr = irr(investor_cash_flows)
                    product_npv = npv(funding_cost, investor_cash_flows)
                    contribution_margin = (product_irr - funding_cost) * 10000
                    customer_payment = 0
                    rate_card = f"${prepaid / system_kw:.0f}/kW prepaid, {dealer_fee * 100:.1f}% dealer fee"
                    customer_savings = annual_kwh * state["utility_rate"] * 0.78
                else:
                    base_ppkwh = state["utility_rate"] * RNG.uniform(0.64, 0.82)
                    lease_factor = 0.0105 + RNG.uniform(-0.0015, 0.002)
                    customer_payment = (system_cost * lease_factor) if product["type"] == "Lease" else (annual_kwh * base_ppkwh / 12)
                    investor_cash_flows = [-system_cost * (1 + dealer_fee) + upfront_incentive]
                    for year in range(1, product["term"] + 1):
                        annual_payment = customer_payment * 12 * ((1 + escalator) ** (year - 1))
                        degradation = 1 - min(year - 1, 24) * 0.006
                        investor_cash_flows.append(annual_payment + rec_value * degradation - service_cost - system_cost * credit["loss"] * 0.18)
                    product_irr = irr(investor_cash_flows)
                    product_npv = npv(funding_cost, investor_cash_flows)
                    contribution_margin = (product_irr - funding_cost - credit["loss"] * 0.35) * 10000
                    if product["type"] == "PPA":
                        rate_card = f"${base_ppkwh:.3f}/kWh, {escalator * 100:.2f}% escalator"
                    else:
                        rate_card = f"${customer_payment:.0f}/mo, {escalator * 100:.2f}% escalator"
                    customer_savings = annual_kwh * state["utility_rate"] - customer_payment * 12

                approval_lift = (credit["approval"] - 0.58) * 100 + RNG.uniform(-2.5, 4.5)
                competitor_gap = (apr - competitor_rate) * 10000 if product["type"] == "Loan" else RNG.uniform(-18, 38)
                margin_gap = contribution_margin - margin_floor * 10000
                qa_defects = max(0, int(RNG.gauss(3.5 + channel["complexity"] / 7 * tier["defect"], 2)))
                readiness = (
                    26
                    + state["policy_score"] * 0.34
                    + approval_lift * 0.42
                    + max(-16, min(24, margin_gap / 36))
                    + max(0, 24 - state["nem_friction"]) * 0.72
                    - channel["complexity"] * 0.62
                )
                priority_score = (
                    max(0, -margin_gap) * 0.16
                    + max(0, competitor_gap) * 0.24
                    + qa_defects * 3.4
                    + channel["complexity"] * 1.6
                    + max(0, 72 - readiness) * 0.9
                )
                if margin_gap < -40:
                    recommendation = "Raise rate or reduce dealer incentive"
                elif competitor_gap > 32:
                    recommendation = "Reprice to defend installer proposal flow"
                elif qa_defects >= 7:
                    recommendation = "Hold launch until pricing QA clears"
                elif readiness > 74 and contribution_margin > 260:
                    recommendation = "Expand into next operating review"
                else:
                    recommendation = "Monitor in weekly pricing digest"

                scenario = {
                    "scenario_id": f"SCN-{scenario_id:03d}",
                    "state": state["state"],
                    "channel": channel["channel"],
                    "product": product["product"],
                    "product_type": product["type"],
                    "credit_band": credit["credit_band"],
                    "dealer_tier": tier["dealer_tier"],
                    "system_kw": pct(system_kw),
                    "battery_attach": "Yes" if battery else "No",
                    "annual_kwh": int(annual_kwh),
                    "project_cost": money(system_cost),
                    "dealer_fee_pct": pct(dealer_fee),
                    "funding_cost_pct": pct(funding_cost),
                    "loss_reserve_pct": pct(credit["loss"]),
                    "customer_monthly_payment": money(customer_payment),
                    "rate_card": rate_card,
                    "npv": money(product_npv),
                    "irr_pct": pct(product_irr),
                    "contribution_margin_bps": pct(contribution_margin),
                    "margin_gap_bps": pct(margin_gap),
                    "competitor_gap_bps": pct(competitor_gap),
                    "approval_lift_pts": pct(approval_lift),
                    "readiness_score": pct(readiness),
                    "qa_defects": qa_defects,
                    "priority_score": pct(priority_score),
                    "customer_savings_year_1": money(customer_savings),
                    "recommendation": recommendation,
                }
                scenario_rows.append(scenario)

                competitive_rows.append(
                    {
                        "scenario_id": scenario["scenario_id"],
                        "state": state["state"],
                        "channel": channel["channel"],
                        "product": product["product"],
                        "competitor": weighted_choice(
                            [("National solar lender", 0.36), ("Regional credit union", 0.2), ("TPO specialist", 0.28), ("Installer captive offer", 0.16)]
                        ),
                        "competitor_rate_or_price": pct(competitor_rate if product["type"] == "Loan" else state["utility_rate"] * RNG.uniform(0.62, 0.84)),
                        "competitor_dealer_fee_pct": pct(max(0, competitor_fee)),
                        "dealer_incentive_pct": pct(tier["rebate"] + RNG.uniform(0.0, 0.012)),
                        "proposal_win_risk": "High" if competitor_gap > 35 else "Medium" if competitor_gap > 10 else "Low",
                    }
                )

                qa_rows.append(
                    {
                        "scenario_id": scenario["scenario_id"],
                        "state": state["state"],
                        "channel": channel["channel"],
                        "test_area": weighted_choice(
                            [("Rate card import", 0.26), ("Dealer proposal sync", 0.25), ("Credit prequal", 0.22), ("Escalator display", 0.15), ("Funding milestone", 0.12)]
                        ),
                        "severity": "High" if qa_defects >= 8 else "Medium" if qa_defects >= 4 else "Low",
                        "open_defects": qa_defects,
                        "data_quality_score": pct(max(58, 99 - qa_defects * 4.5 - RNG.uniform(0, 8))),
                        "owner": weighted_choice([("Pricing", 0.34), ("Product", 0.26), ("Operations", 0.24), ("Analytics", 0.16)]),
                    }
                )

                action_rows.append(
                    {
                        "action_id": f"ACT-{scenario_id:03d}",
                        "scenario_id": scenario["scenario_id"],
                        "action": recommendation,
                        "owner": weighted_choice([("Pricing manager", 0.36), ("Product lead", 0.22), ("Analytics", 0.2), ("Dealer ops", 0.22)]),
                        "meeting": weighted_choice([("Weekly pricing review", 0.44), ("S&OP", 0.24), ("Platform QA standup", 0.18), ("Product council", 0.14)]),
                    "estimated_margin_impact": money(min(425000, max(12000, abs(margin_gap) * system_kw * 14))),
                        "due_week": weighted_choice([("2026-06-05", 0.34), ("2026-06-12", 0.34), ("2026-06-19", 0.22), ("2026-06-26", 0.1)]),
                    }
                )

                scenario_id += 1

    return scenario_rows, competitive_rows, qa_rows, action_rows


def summarize(scenarios, competitive, qa, actions):
    top = sorted(scenarios, key=lambda row: float(row["priority_score"]), reverse=True)
    profitable = [row for row in scenarios if float(row["contribution_margin_bps"]) > 0]
    ready = [row for row in scenarios if float(row["readiness_score"]) >= 74]
    high_win_risk = [row for row in competitive if row["proposal_win_risk"] == "High"]
    qa_high = [row for row in qa if row["severity"] == "High"]
    by_product = defaultdict(list)
    by_state = defaultdict(list)
    for row in scenarios:
        by_product[row["product"]].append(row)
        by_state[row["state"]].append(row)

    product_summary = []
    for product, rows in by_product.items():
        product_summary.append(
            {
                "product": product,
                "avg_irr_pct": pct(sum(float(r["irr_pct"]) for r in rows) / len(rows)),
                "avg_npv": money(sum(float(r["npv"]) for r in rows) / len(rows)),
                "avg_margin_bps": pct(sum(float(r["contribution_margin_bps"]) for r in rows) / len(rows)),
                "avg_payment": money(sum(float(r["customer_monthly_payment"]) for r in rows) / len(rows)),
                "ready_scenarios": sum(1 for r in rows if float(r["readiness_score"]) >= 74),
            }
        )
    product_summary.sort(key=lambda row: float(row["avg_margin_bps"]), reverse=True)

    state_summary = []
    for state, rows in by_state.items():
        state_summary.append(
            {
                "state": state,
                "avg_readiness": pct(sum(float(r["readiness_score"]) for r in rows) / len(rows)),
                "avg_margin_bps": pct(sum(float(r["contribution_margin_bps"]) for r in rows) / len(rows)),
                "avg_competitor_gap_bps": pct(sum(float(r["competitor_gap_bps"]) for r in rows) / len(rows)),
                "high_priority_count": sum(1 for r in rows if float(r["priority_score"]) >= 58),
            }
        )
    state_summary.sort(key=lambda row: float(row["avg_readiness"]), reverse=True)

    summary = {
        "scenario_count": len(scenarios),
        "state_count": len(by_state),
        "product_count": len(by_product),
        "profitable_pct": pct(len(profitable) / len(scenarios) * 100),
        "ready_count": len(ready),
        "high_win_risk_count": len(high_win_risk),
        "high_qa_count": len(qa_high),
        "top_scenario": top[0],
        "product_summary": product_summary,
        "state_summary": state_summary,
        "rate_card_actions": top[:18],
        "market_expansion_queue": state_summary,
        "qa_readiness_queue": sorted(qa, key=lambda row: (row["severity"], int(row["open_defects"])), reverse=True)[:18],
        "actions": sorted(actions, key=lambda row: float(row["estimated_margin_impact"]), reverse=True)[:18],
    }
    return summary


def write_analysis(summary):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUTPUT_DIR / "rate_card_actions.csv",
        summary["rate_card_actions"],
        list(summary["rate_card_actions"][0].keys()),
    )
    write_csv(
        OUTPUT_DIR / "market_expansion_queue.csv",
        summary["market_expansion_queue"],
        list(summary["market_expansion_queue"][0].keys()),
    )
    write_csv(
        OUTPUT_DIR / "qa_readiness_queue.csv",
        summary["qa_readiness_queue"],
        list(summary["qa_readiness_queue"][0].keys()),
    )
    write_csv(
        OUTPUT_DIR / "stakeholder_actions.csv",
        summary["actions"],
        list(summary["actions"][0].keys()),
    )
    with (OUTPUT_DIR / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)

    top = summary["top_scenario"]
    (ANALYSIS_DIR / "executive_findings.md").write_text(
        "\n".join(
            [
                "# Executive Findings",
                "",
                "## What I analyzed",
                "",
                f"I modeled {summary['scenario_count']} synthetic residential solar finance pricing scenarios across {summary['state_count']} states, {summary['product_count']} product structures, dealer channels, credit bands, competitive offers, and pricing-platform QA checks.",
                "",
                "## Findings",
                "",
                f"- The highest-priority rate-card action is {top['scenario_id']}, a {top['state']} {top['product']} scenario in the {top['channel']} channel.",
                f"- The scenario combines {top['competitor_gap_bps']} bps of competitor gap, {top['margin_gap_bps']} bps of margin gap, {top['qa_defects']} QA defects, and a {top['readiness_score']} readiness score.",
                f"- {summary['ready_count']} scenarios clear the expansion-readiness threshold while {summary['high_win_risk_count']} scenarios show high proposal win risk.",
                f"- Product economics are strongest for {summary['product_summary'][0]['product']} with an average margin of {summary['product_summary'][0]['avg_margin_bps']} bps.",
                "",
                "## Recommendation",
                "",
                "Use the rate-card queue to separate pricing moves from product-readiness issues. Reprice scenarios with negative margin or high competitor gap, hold launches with severe QA defects, and move ready states into the next operating review.",
                "",
            ]
        )
    )

    (ANALYSIS_DIR / "analysis_plan.md").write_text(
        "\n".join(
            [
                "# Analysis Plan",
                "",
                "1. Generate product scenarios by state, channel, product type, credit band, and dealer tier.",
                "2. Convert pricing inputs into customer payment, dealer fee, NPV, IRR, contribution margin, and funding-cost gap.",
                "3. Join competitor offers and dealer incentives to estimate proposal win risk.",
                "4. Score state and channel readiness using policy fit, approval lift, margin gap, and product complexity.",
                "5. Rank rate-card actions, market expansion opportunities, QA risks, and stakeholder follow-ups.",
                "",
            ]
        )
    )

    (ANALYSIS_DIR / "methodology.md").write_text(
        "\n".join(
            [
                "# Methodology",
                "",
                "The model is deterministic and synthetic. It is designed to be interview-safe because it does not use private rate cards, dealer contracts, customer credit files, or fund economics.",
                "",
                "Loan scenarios compute amortizing customer payments from financed amount, APR, dealer fee, and term. Investor cash flows subtract servicing cost and loss reserve, then calculate NPV at funding cost and IRR.",
                "",
                "Lease and PPA scenarios model owner cash flows using project cost, tax-credit proxy, SREC or REC value, escalator, service cost, and production degradation. The model calculates monthly payment or price per kWh, NPV, IRR, and margin gap.",
                "",
                "Priority score increases when margin gap is negative, competitor gap is high, QA defects are open, channel complexity is high, or state readiness is weak.",
                "",
            ]
        )
    )

    (ANALYSIS_DIR / "sql_checks.sql").write_text(
        "\n".join(
            [
                "-- SQL examples for validating a residential solar finance pricing workbench.",
                "",
                "-- 1. Rate-card moves with margin or competitiveness pressure.",
                "select",
                "  scenario_id,",
                "  state,",
                "  channel,",
                "  product,",
                "  margin_gap_bps,",
                "  competitor_gap_bps,",
                "  recommendation",
                "from pricing_scenarios",
                "where margin_gap_bps < 0 or competitor_gap_bps > 30",
                "order by priority_score desc;",
                "",
                "-- 2. State readiness for expansion planning.",
                "select",
                "  state,",
                "  avg(readiness_score) as avg_readiness,",
                "  avg(contribution_margin_bps) as avg_margin_bps,",
                "  sum(case when qa_defects >= 7 then 1 else 0 end) as severe_qa_scenarios",
                "from pricing_scenarios",
                "group by state",
                "order by avg_readiness desc;",
                "",
                "-- 3. Platform QA checks by pricing workflow area.",
                "select",
                "  test_area,",
                "  severity,",
                "  count(*) as checks,",
                "  sum(open_defects) as open_defects",
                "from platform_qa",
                "group by test_area, severity",
                "order by open_defects desc;",
                "",
            ]
        )
    )


def write_docs(scenarios, competitive, qa, actions, summary):
    (DATA_DIR / "README.md").write_text(
        "\n".join(
            [
                "# Data Sources",
                "",
                "This folder contains deterministic synthetic data for a residential solar finance pricing and product workbench.",
                "",
                "The data is modeled on common residential solar finance workflows: dealer rate cards, loan and third-party-owned product economics, state expansion research, competitor offer tracking, pricing-platform QA, and S&OP follow-up queues.",
                "",
                "It does not represent real company performance, customer credit files, dealer contracts, or private pricing assumptions.",
                "",
                "- `pricing_scenarios.csv`: Scenario-level product economics with NPV, IRR, margin gap, competitor gap, and recommended action.",
                "- `competitive_intelligence.csv`: Synthetic competitor pricing, dealer incentive, and proposal win risk records.",
                "- `platform_qa.csv`: Pricing-platform test results and data-quality checks by workflow area.",
                "- `stakeholder_actions.csv`: Follow-up queue for pricing review, S&OP, product council, and QA standups.",
                "",
                "The generator uses a fixed random seed. Ranges are documented in `analysis/methodology.md` and implemented in `scripts/score_operating_data.py`.",
                "",
            ]
        )
    )

    (ROOT / "data_dictionary.md").write_text(
        "\n".join(
            [
                "# Data Dictionary",
                "",
                "| File | Grain | Description |",
                "| --- | --- | --- |",
                "| `pricing_scenarios.csv` | State x channel x product scenario | Pricing inputs and modeled economics for loans, leases, PPAs, and prepaid leases. |",
                "| `competitive_intelligence.csv` | Scenario x competitor check | Competitor price proxy, dealer incentive, and proposal win risk. |",
                "| `platform_qa.csv` | Scenario x QA test area | Open pricing-platform defects, severity, owner, and data-quality score. |",
                "| `stakeholder_actions.csv` | Scenario x action | Recommended follow-up, meeting venue, owner, due week, and estimated margin impact. |",
                "| `analysis/outputs/rate_card_actions.csv` | Scenario | Highest-priority pricing and rate-card moves. |",
                "| `analysis/outputs/market_expansion_queue.csv` | State | State readiness, average margin, competitor gap, and high-priority count. |",
                "| `analysis/outputs/qa_readiness_queue.csv` | QA check | Highest-risk pricing-platform QA items. |",
                "",
                "Key modeled fields:",
                "",
                "- `npv`: Net present value of modeled investor cash flows at funding cost.",
                "- `irr_pct`: Internal rate of return from modeled product cash flows.",
                "- `contribution_margin_bps`: IRR less funding cost and risk reserve, expressed in basis-point style units.",
                "- `margin_gap_bps`: Difference between contribution margin and modeled margin floor.",
                "- `competitor_gap_bps`: Positive values indicate the scenario is less competitive than the synthetic market reference.",
                "- `readiness_score`: Composite state and product readiness score.",
                "- `priority_score`: Composite score used to rank pricing actions.",
                "",
            ]
        )
    )

    app_data = {
        "summary": {
            "scenarioCount": summary["scenario_count"],
            "stateCount": summary["state_count"],
            "productCount": summary["product_count"],
            "profitablePct": summary["profitable_pct"],
            "readyCount": summary["ready_count"],
            "highWinRiskCount": summary["high_win_risk_count"],
            "highQaCount": summary["high_qa_count"],
            "topScenario": summary["top_scenario"],
        },
        "productSummary": summary["product_summary"],
        "stateSummary": summary["state_summary"],
        "rateCardActions": summary["rate_card_actions"][:12],
        "qaQueue": summary["qa_readiness_queue"][:12],
        "stakeholderActions": summary["actions"][:10],
    }
    (SRC_DIR / "data.js").write_text(
        "export const appData = "
        + json.dumps(app_data, indent=2)
        + ";\n"
    )

    readme = [
        "# Solar Finance Pricing Product Lab",
        "",
        "An interactive portfolio artifact for a residential solar financing pricing and new product team. The lab shows how pricing inputs flow into fund economics, dealer rate cards, competitive intelligence, market expansion decisions, and platform QA follow-up.",
        "",
        "## What this project demonstrates",
        "",
        "- Excel-style pricing model logic for loan, lease, PPA, and prepaid lease scenarios.",
        "- NPV, IRR, discounted cash-flow, contribution margin, dealer fee, customer payment, and funding-cost calculations.",
        "- Competitive intelligence tracking across states, channels, dealer tiers, and product structures.",
        "- New-product and market readiness scoring for operating reviews.",
        "- Pricing-platform QA and stakeholder action queues for S&OP and launch support.",
        "",
        "## Screenshots",
        "",
        "![Pricing cockpit](docs/images/pricing-cockpit.png)",
        "",
        "Pricing cockpit showing portfolio KPIs, product economics, and the highest-priority rate-card action.",
        "",
        "![Scenario model](docs/images/scenario-model.png)",
        "",
        "Scenario model surface with rate-card recommendations, NPV, IRR, margin gap, competitor gap, and monthly payment outputs.",
        "",
        "![Market and QA queue](docs/images/market-qa.png)",
        "",
        "Market and QA surface showing state expansion readiness, pricing-platform defects, and stakeholder follow-ups.",
        "",
        "## Data",
        "",
        "All data is synthetic and generated by `scripts/score_operating_data.py` with a fixed random seed. The structure is modeled on common residential solar finance workflows, including dealer rate cards, loan and third-party-owned economics, competitor offer tracking, state expansion research, platform QA, and operating review follow-ups.",
        "",
        "The synthetic generator creates scenarios across eight states, four dealer channels, five product structures, three credit bands, and three dealer tiers. It assigns project cost per watt, system size, production yield, dealer fee, funding cost, loss reserve, servicing cost, APR or escalator, tax-credit proxy, REC value, competitor offer, approval lift, and QA defects.",
        "",
        "Loan scenarios use amortizing payment logic. Lease and PPA scenarios use owner cash flows with production, escalator, service cost, incentive value, and degradation assumptions. The model then calculates NPV, IRR, contribution margin, margin gap, competitiveness gap, readiness score, and priority score.",
        "",
        "## Repository guide",
        "",
        "- `data/pricing_scenarios.csv`: Scenario-level pricing model output.",
        "- `data/competitive_intelligence.csv`: Competitor offer and dealer incentive checks.",
        "- `data/platform_qa.csv`: Pricing-platform QA and data-quality checks.",
        "- `data/stakeholder_actions.csv`: S&OP, product, pricing, and QA follow-up queue.",
        "- `analysis/outputs/rate_card_actions.csv`: Ranked pricing and rate-card recommendations.",
        "- `analysis/outputs/market_expansion_queue.csv`: State readiness summary.",
        "- `analysis/outputs/qa_readiness_queue.csv`: Highest-risk QA items.",
        "- `src/app.js` and `src/data.js`: Interactive static workbench.",
        "",
        "## Role connection",
        "",
        "This artifact is designed for a pricing development and new product role in residential solar finance. It demonstrates the core work called for in the role: maintaining pricing model logic, explaining how inputs affect fund economics and dealer rate cards, organizing competitive intelligence, supporting market and product research, preparing operating-review materials, and documenting platform QA issues.",
        "",
        "## Run locally",
        "",
        "```bash",
        "npm run analyze",
        "npm start",
        "```",
        "",
        "Then open `http://localhost:4173`.",
        "",
        "## Scope",
        "",
        "This is a public portfolio artifact, not a production pricing system. It does not use real customer data, private dealer terms, live rate cards, credit policy, investor documents, or company performance data. It does show a defensible workflow for connecting pricing assumptions, finance outputs, market intelligence, product readiness, and QA follow-up into one decision artifact.",
        "",
    ]
    (ROOT / "README.md").write_text("\n".join(readme))

    (ROOT / "STATUS.md").write_text(
        "\n".join(
            [
                "# Status",
                "",
                "- Status: upgraded through the Portfolio Artifact Upgrade Workflow.",
                "- Artifact type: residential solar finance pricing and product workbench.",
                "- Data: deterministic synthetic scenario model with documented assumptions.",
                "- Verification: regenerate data with `npm run analyze`, serve with `npm start`, and inspect the three README screenshots.",
                "",
            ]
        )
    )


def main():
    DATA_DIR.mkdir(exist_ok=True)
    ANALYSIS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    SRC_DIR.mkdir(exist_ok=True)

    scenarios, competitive, qa, actions = build_scenarios()
    write_csv(DATA_DIR / "pricing_scenarios.csv", scenarios, list(scenarios[0].keys()))
    write_csv(DATA_DIR / "competitive_intelligence.csv", competitive, list(competitive[0].keys()))
    write_csv(DATA_DIR / "platform_qa.csv", qa, list(qa[0].keys()))
    write_csv(DATA_DIR / "stakeholder_actions.csv", actions, list(actions[0].keys()))

    summary = summarize(scenarios, competitive, qa, actions)
    write_analysis(summary)
    write_docs(scenarios, competitive, qa, actions, summary)
    print(
        f"Generated {len(scenarios)} scenarios, {len(competitive)} competitor checks, "
        f"{len(qa)} QA checks, and {len(actions)} actions."
    )


if __name__ == "__main__":
    main()
