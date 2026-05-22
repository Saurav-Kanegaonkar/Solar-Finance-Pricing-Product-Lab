-- SQL examples for validating a residential solar finance pricing workbench.

-- 1. Rate-card moves with margin or competitiveness pressure.
select
  scenario_id,
  state,
  channel,
  product,
  margin_gap_bps,
  competitor_gap_bps,
  recommendation
from pricing_scenarios
where margin_gap_bps < 0 or competitor_gap_bps > 30
order by priority_score desc;

-- 2. State readiness for expansion planning.
select
  state,
  avg(readiness_score) as avg_readiness,
  avg(contribution_margin_bps) as avg_margin_bps,
  sum(case when qa_defects >= 7 then 1 else 0 end) as severe_qa_scenarios
from pricing_scenarios
group by state
order by avg_readiness desc;

-- 3. Platform QA checks by pricing workflow area.
select
  test_area,
  severity,
  count(*) as checks,
  sum(open_defects) as open_defects
from platform_qa
group by test_area, severity
order by open_defects desc;
