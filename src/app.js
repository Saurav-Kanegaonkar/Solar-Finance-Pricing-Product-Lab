import { appData } from "./data.js";

const {
  summary,
  productSummary,
  stateSummary,
  rateCardActions,
  qaQueue,
  stakeholderActions,
  assumptionLedger,
  sensitivityTests,
  launchGates,
} = appData;

const formatMoney = (value) =>
  Number(value).toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

const formatPct = (value) => `${Number(value).toFixed(1)}%`;
const formatBps = (value) => `${Number(value).toFixed(0)} bps`;

function productBars() {
  const maxMargin = Math.max(...productSummary.map((row) => Number(row.avg_margin_bps)));
  return productSummary
    .map((row) => {
      const width = Math.max(10, (Number(row.avg_margin_bps) / maxMargin) * 100);
      return `
        <li>
          <span>${row.product}</span>
          <div class="bar-track"><i style="width:${width}%"></i></div>
          <b>${formatBps(row.avg_margin_bps)}</b>
        </li>
      `;
    })
    .join("");
}

function stateBars() {
  return stateSummary
    .map((row) => `
      <li>
        <span>${row.state}</span>
        <div class="state-score">
          <i style="width:${Math.max(18, Number(row.avg_readiness))}%"></i>
        </div>
        <b>${Number(row.avg_readiness).toFixed(1)}</b>
      </li>
    `)
    .join("");
}

function renderRateRows(rows) {
  return rows
    .slice(0, 8)
    .map((row) => `
      <tr>
        <td><strong>${row.scenario_id}</strong><span>${row.state} | ${row.channel}</span></td>
        <td>${row.product}<span>${row.credit_band}, ${row.dealer_tier}</span></td>
        <td>${row.rate_card}</td>
        <td>${formatMoney(row.npv)}<span>${formatPct(Number(row.irr_pct) * 100)} IRR</span></td>
        <td>${formatBps(row.margin_gap_bps)}<span>${formatBps(row.competitor_gap_bps)} comp gap</span></td>
        <td>${row.recommendation}</td>
      </tr>
    `)
    .join("");
}

function renderQaRows(rows) {
  return rows
    .slice(0, 7)
    .map((row) => `
      <tr>
        <td><strong>${row.test_area}</strong><span>${row.scenario_id} | ${row.state}</span></td>
        <td><mark class="${row.severity.toLowerCase()}">${row.severity}</mark></td>
        <td>${row.open_defects}</td>
        <td>${Number(row.data_quality_score).toFixed(1)}</td>
        <td>${row.owner}</td>
      </tr>
    `)
    .join("");
}

function renderActions(rows) {
  return rows
    .slice(0, 6)
    .map((row) => `
      <article>
        <span>${row.meeting}</span>
        <h3>${row.action}</h3>
        <p>${row.scenario_id} owned by ${row.owner}. Estimated margin impact ${formatMoney(row.estimated_margin_impact)} by ${row.due_week}.</p>
      </article>
    `)
    .join("");
}

function renderAssumptions(rows) {
  return rows
    .map((row) => `
      <tr>
        <td><strong>${row.state}</strong><span>${row.region}</span></td>
        <td>${Number(row.residential_rate_cents_kwh).toFixed(1)} cents<span>residential rate anchor</span></td>
        <td>${Number(row.annual_yield_kwh_per_kw).toLocaleString()}<span>kWh per kW-year</span></td>
        <td>${row.policy_score}<span>policy score</span></td>
        <td>${row.model_use}</td>
      </tr>
    `)
    .join("");
}

function renderSensitivity(rows) {
  return rows
    .slice(0, 8)
    .map((row) => `
      <tr>
        <td><strong>${row.scenario_id}</strong><span>${row.state} | ${row.product}</span></td>
        <td>${row.test}<span>${row.channel}</span></td>
        <td>${formatBps(row.baseline_margin_bps)}<span>baseline</span></td>
        <td>${formatBps(row.stressed_margin_bps)}<span>${formatBps(row.margin_delta_bps)} delta</span></td>
        <td><mark class="${row.decision_signal.toLowerCase()}">${row.decision_signal}</mark></td>
        <td>${row.action}</td>
      </tr>
    `)
    .join("");
}

function renderLaunchGates(rows) {
  return rows
    .map((row) => `
      <article>
        <div>
          <span>${row.channel}</span>
          <h3>${row.launch_gate}</h3>
          <p>${row.blocker}</p>
        </div>
        <dl>
          <div><dt>Status</dt><dd>${row.status}</dd></div>
          <div><dt>Readiness</dt><dd>${Number(row.avg_readiness).toFixed(1)}</dd></div>
          <div><dt>Margin</dt><dd>${formatBps(row.avg_margin_bps)}</dd></div>
          <div><dt>QA defects</dt><dd>${row.open_qa_defects}</dd></div>
        </dl>
        <p>${row.next_step}</p>
      </article>
    `)
    .join("");
}

function render() {
  const top = summary.topScenario;
  document.querySelector("#app").innerHTML = `
    <header class="topbar">
      <div>
        <p class="eyebrow">Residential solar finance</p>
        <h1>Pricing and product workbench</h1>
      </div>
      <nav class="topnav" aria-label="Workbench sections">
        <a href="#scenario-model">Rate card</a>
        <a href="#sensitivity-lab">Sensitivity</a>
        <a href="#market-qa">Launch QA</a>
      </nav>
    </header>

    <main>
      <section class="hero-band" id="pricing-cockpit">
        <div class="hero-copy">
          <p class="eyebrow">Pricing cockpit</p>
          <h2>Turn product inputs into fund economics, dealer rate cards, and weekly operating actions.</h2>
          <p>The model connects project cost, credit band, APR or escalator, dealer fee, funding cost, loss reserve, competitor gap, and platform QA into one ranked pricing queue.</p>
        </div>
        <div class="top-action">
          <span>Highest-priority action</span>
          <h3>${top.scenario_id} | ${top.state} ${top.product}</h3>
          <p>${top.recommendation}</p>
          <dl>
            <div><dt>NPV</dt><dd>${formatMoney(top.npv)}</dd></div>
            <div><dt>IRR</dt><dd>${formatPct(Number(top.irr_pct) * 100)}</dd></div>
            <div><dt>Customer payment</dt><dd>${formatMoney(top.customer_monthly_payment)}</dd></div>
          </dl>
        </div>
      </section>

      <section class="metric-grid" aria-label="Portfolio summary">
        <article><span>Scenarios</span><strong>${summary.scenarioCount}</strong><em>${summary.stateCount} states</em></article>
        <article><span>Profitable</span><strong>${Number(summary.profitablePct).toFixed(0)}%</strong><em>positive margin</em></article>
        <article><span>Ready</span><strong>${summary.readyCount}</strong><em>expansion candidates</em></article>
        <article><span>Win risk</span><strong>${summary.highWinRiskCount}</strong><em>high competitor gap</em></article>
        <article><span>QA risk</span><strong>${summary.highQaCount}</strong><em>severe checks</em></article>
      </section>

      <section class="surface-grid">
        <article class="panel">
          <div class="panel-head">
            <p class="eyebrow">Product economics</p>
            <h2>Average margin by product</h2>
          </div>
          <ul class="bar-list">${productBars()}</ul>
        </article>
        <article class="panel">
          <div class="panel-head">
            <p class="eyebrow">Market research</p>
            <h2>State readiness score</h2>
          </div>
          <ul class="state-list">${stateBars()}</ul>
        </article>
      </section>

      <section class="table-surface" id="scenario-model">
        <div class="panel-head">
          <p class="eyebrow">Scenario model</p>
          <h2>Rate-card actions from cash-flow outputs</h2>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Product</th>
                <th>Rate card</th>
                <th>Economics</th>
                <th>Gap</th>
                <th>Move</th>
              </tr>
            </thead>
            <tbody>${renderRateRows(rateCardActions)}</tbody>
          </table>
        </div>
      </section>

      <section class="table-surface" id="sensitivity-lab">
        <div class="panel-head">
          <p class="eyebrow">Assumption ledger</p>
          <h2>Public-market anchors behind the synthetic model</h2>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>State</th>
                <th>Electric rate</th>
                <th>Production yield</th>
                <th>Policy</th>
                <th>Model use</th>
              </tr>
            </thead>
            <tbody>${renderAssumptions(assumptionLedger)}</tbody>
          </table>
        </div>
      </section>

      <section class="table-surface">
        <div class="panel-head">
          <p class="eyebrow">Sensitivity tests</p>
          <h2>Rate-card stress checks before launch approval</h2>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Stress test</th>
                <th>Base margin</th>
                <th>Stressed margin</th>
                <th>Signal</th>
                <th>Pricing action</th>
              </tr>
            </thead>
            <tbody>${renderSensitivity(sensitivityTests)}</tbody>
          </table>
        </div>
      </section>

      <section class="surface-grid" id="market-qa">
        <article class="panel launch-panel">
          <div class="panel-head">
            <p class="eyebrow">New-product gates</p>
            <h2>Launch readiness by product surface</h2>
          </div>
          <div class="launch-list">${renderLaunchGates(launchGates)}</div>
        </article>
        <article class="panel qa-panel">
          <div class="panel-head">
            <p class="eyebrow">Platform QA</p>
            <h2>Defects that block launch confidence</h2>
          </div>
          <div class="table-wrap compact">
            <table>
              <thead>
                <tr>
                  <th>Test area</th>
                  <th>Severity</th>
                  <th>Defects</th>
                  <th>Quality</th>
                  <th>Owner</th>
                </tr>
              </thead>
              <tbody>${renderQaRows(qaQueue)}</tbody>
            </table>
          </div>
        </article>
      </section>

      <section class="surface-grid">
        <article class="panel action-panel">
          <div class="panel-head">
            <p class="eyebrow">S&OP brief</p>
            <h2>Stakeholder follow-up queue</h2>
          </div>
          <div class="action-list">${renderActions(stakeholderActions)}</div>
        </article>
      </section>
    </main>
  `;
}

render();
