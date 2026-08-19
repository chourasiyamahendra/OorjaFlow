import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="OorjaFlow - Hybrid System Simulation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

html_simulation = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  :root {
    --bg-main: #f8fafc;
    --pv-bg: #fffbeb;
    --pv-border: #f59e0b;
    --gti-bg: #fff7ed;
    --gti-border: #f97316;
    --bat-bg: #ecfdf5;
    --bat-border: #10b981;
    --grid-bg: #eff6ff;
    --grid-border: #3b82f6;
    --gload-bg: #f5f3ff;
    --gload-border: #8b5cf6;
    --bload-bg: #fdf4ff;
    --bload-border: #d946ef;
    --hub-border: #eab308;
    --text-dark: #1e293b;
    --text-muted: #64748b;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: var(--bg-main); color: var(--text-dark); display: flex; flex-direction: column; align-items: center; padding: 10px; }

  .header { text-align: center; margin-bottom: 12px; }
  .header h1 { font-size: 22px; font-weight: 800; color: var(--text-dark); display: flex; align-items: center; justify-content: center; gap: 8px; }
  .header p { font-size: 13px; color: var(--text-muted); margin-top: 2px; }

  .diagram-container {
    position: relative;
    width: 1020px;
    height: 720px;
    background: #ffffff;
    border-radius: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    padding: 24px 34px;
    border: 1px solid #e2e8f0;
  }

  svg.connections {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
  }

  .pipe-base { stroke: #e2e8f0; stroke-width: 6; fill: none; stroke-linecap: round; stroke-linejoin: round; }
  
  .pipe-flow {
    stroke-width: 5;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-dasharray: 8 14;
    animation: flowSlow 2.4s linear infinite;
  }

  @keyframes flowSlow {
    from { stroke-dashoffset: 44; }
    to { stroke-dashoffset: 0; }
  }

  .reverse-flow {
    animation: flowSlowRev 2.4s linear infinite !important;
  }

  @keyframes flowSlowRev {
    from { stroke-dashoffset: 0; }
    to { stroke-dashoffset: 44; }
  }

  .grid-layout {
    position: relative;
    display: grid;
    grid-template-columns: 330px 1fr 330px;
    grid-template-rows: 220px 170px 220px;
    gap: 20px 0;
    height: 100%;
    z-index: 2;
  }

  .card {
    border-radius: 24px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 14px rgba(0,0,0,0.02);
    border: 2px solid transparent;
  }

  .card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  .card-title { font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 6px; }

  .icon-circle {
    width: 58px;
    height: 58px;
    min-width: 58px;
    border-radius: 50%;
    background: #fff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    font-size: 11px;
    font-weight: 800;
    border: 2px solid;
    text-align: center;
  }

  .metric-lbl { font-size: 11px; color: var(--text-muted); }
  .slider-row { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; margin-top: 6px; }
  .slider-row input[type=range] { flex: 1; height: 4px; cursor: pointer; accent-color: #2563eb; }

  .scenario-deck {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
    margin-top: 8px;
  }
  .btn-scen {
    background: #ffffff;
    border: 1px solid #fcd34d;
    color: #b45309;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 2px;
    border-radius: 6px;
    cursor: pointer;
    text-align: center;
    transition: 0.15s;
  }
  .btn-scen:hover { background: #fef3c7; }

  .status-badge {
    font-size: 10px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 10px;
    width: fit-content;
    display: inline-block;
  }

  .bat-flow-readout {
    font-size: 11px;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 4px;
    padding: 3px 6px;
    background: #ffffff;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    width: fit-content;
  }

  .card-pv { background: var(--pv-bg); border-color: var(--pv-border); grid-column: 1; grid-row: 1; }
  .card-pv .icon-circle { border-color: var(--pv-border); color: #d97706; }

  .card-gti { background: var(--gti-bg); border-color: var(--gti-border); grid-column: 1; grid-row: 2; }
  .card-gti .icon-circle { border-color: var(--gti-border); color: #ea580c; }

  .card-bat { background: var(--bat-bg); border-color: var(--bat-border); grid-column: 1; grid-row: 3; }
  .card-bat .icon-circle { border-color: var(--bat-border); color: #059669; }

  .card-grid { background: var(--grid-bg); border-color: var(--grid-border); grid-column: 3; grid-row: 1; }
  .card-grid .icon-circle { border-color: var(--grid-border); color: #0284c7; }

  .card-gload { background: var(--gload-bg); border-color: var(--gload-border); grid-column: 3; grid-row: 2; }
  .card-gload .icon-circle { border-color: var(--gload-border); color: #7c3aed; }

  .card-bload { background: var(--bload-bg); border-color: var(--bload-border); grid-column: 3; grid-row: 3; }
  .card-bload .icon-circle { border-color: var(--bload-border); color: #c026d3; }

  .center-hub-wrapper {
    grid-column: 2;
    grid-row: 1 / span 3;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
  .center-hub {
    width: 114px;
    height: 114px;
    border-radius: 50%;
    background: #ffffff;
    border: 4px solid var(--hub-border);
    box-shadow: 0 0 20px rgba(234, 179, 8, 0.25);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 10;
    text-align: center;
    padding: 6px;
  }
  .center-hub .hub-icon { font-size: 22px; line-height: 1; }
  .center-hub .hub-title { font-size: 11px; font-weight: 800; color: #1e293b; margin-top: 3px; line-height: 1.1; }
  
  .freq-badge {
    position: absolute;
    transform: translateY(76px);
    background: #1e293b;
    color: #38bdf8;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
  }

  .btn-fault {
    background: #ef4444;
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 800;
    cursor: pointer;
  }
  .btn-fault.healthy { background: #0284c7; }
</style>
</head>
<body>

<div class="header">
  <h1>⚡ Oorja Flow: AC Microgrid Simulation</h1>
  <p>AC-Coupled Solar & Storage Power Flow Simulator</p>
</div>

<div class="diagram-container">
  <svg class="connections" viewBox="0 0 1020 720">
    <defs>
      <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b"/>
      </marker>
      <marker id="arrow-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#f97316"/>
      </marker>
      <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981"/>
      </marker>
      <marker id="arrow-cyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#06b6d4"/>
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
      </marker>
      <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5cf6"/>
      </marker>
      <marker id="arrow-pink" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#d946ef"/>
      </marker>
    </defs>

    <!-- Base Alignment Pipes -->
    <path class="pipe-base" d="M 195 220 V 260" />
    <path class="pipe-base" d="M 330 345 H 453" />
    <path class="pipe-base" d="M 330 610 H 480 V 417" />
    <path class="pipe-base" d="M 690 110 H 510 V 303" />
    <path class="pipe-base" d="M 567 345 H 690" />
    <path class="pipe-base" d="M 540 417 V 610 H 690" />

    <!-- Animated Flows -->
    <path id="flow-pv-gti" class="pipe-flow" d="M 195 220 V 260" stroke="#f59e0b" marker-end="url(#arrow-amber)" />
    <path id="flow-gti-hub" class="pipe-flow" d="M 330 345 H 453" stroke="#f97316" marker-end="url(#arrow-orange)" />
    <path id="flow-bat-hub" class="pipe-flow" d="M 330 610 H 480 V 417" stroke="#10b981" />
    <path id="flow-grid-hub" class="pipe-flow" d="M 690 110 H 510 V 303" stroke="#2563eb" />
    <path id="flow-hub-gload" class="pipe-flow" d="M 567 345 H 690" stroke="#8b5cf6" marker-end="url(#arrow-purple)" />
    <path id="flow-hub-bload" class="pipe-flow" d="M 540 417 V 610 H 690" stroke="#d946ef" marker-end="url(#arrow-pink)" />
  </svg>

  <div class="grid-layout">
    <!-- Solar PV Card -->
    <div class="card card-pv">
      <div class="card-top">
        <div>
          <div class="card-title">☀️ Solar PV Array</div>
          <div class="metric-lbl">DC Generation</div>
        </div>
        <div class="icon-circle">☀️<span id="pv-node-kw">26.0 kW</span></div>
      </div>
      <div>
        <div class="slider-row">
          <span>Solar:</span>
          <input type="range" id="slider-pv" min="0" max="50" step="0.5" value="26" oninput="updateSim()">
          <span id="lbl-pv">26.0 kW</span>
        </div>
        <div class="scenario-deck">
          <button class="btn-scen" onclick="setScenario(35, 80, 12, 8, true)">☀️ Peak</button>
          <button class="btn-scen" onclick="setScenario(6, 50, 16, 10, true)">⛅ Cloud</button>
          <button class="btn-scen" onclick="setScenario(0, 60, 14, 0, false)">🌙 Night</button>
          <button class="btn-scen" onclick="setScenario(30, 100, 8, 0, false)">🔋 Curtail</button>
        </div>
      </div>
    </div>

    <!-- Grid Tied Inverter -->
    <div class="card card-gti">
      <div class="card-top">
        <div>
          <div class="card-title">⚡ Grid Tied Inverter</div>
          <div class="metric-lbl">Smart Port AC Feed</div>
        </div>
        <div class="icon-circle">🔌<span id="gti-node-kw">26.0 kW</span></div>
      </div>
      <div class="metric-lbl" id="gti-status-msg">Synchronized to Microgrid</div>
    </div>

    <!-- Battery Bank -->
    <div class="card card-bat">
      <div class="card-top">
        <div>
          <div class="card-title">🔋 Battery Bank</div>
          <span id="bat-badge" class="status-badge" style="background:#dcfce7; color:#15803d;">STATUS: CHARGING ↑</span>
        </div>
        <div class="icon-circle">🔋<span id="bat-node-soc">65%</span></div>
      </div>
      <div>
        <div id="bat-flow-info" class="bat-flow-readout" style="color: #15803d;">
          Flow: <span id="bat-flow-val">+8.0 kW (Entering)</span>
        </div>
        <div class="slider-row">
          <span>SoC:</span>
          <input type="range" id="slider-soc" min="10" max="100" step="1" value="65" oninput="updateSim()">
          <span id="lbl-soc">65%</span>
        </div>
      </div>
    </div>

    <!-- Hybrid Inverter Hub -->
    <div class="center-hub-wrapper">
      <div class="center-hub">
        <div class="hub-icon">⚡</div>
        <div class="hub-title">HYBRID<br>INVERTER</div>
      </div>
      <div id="freq-meter" class="freq-badge">50.00 Hz</div>
    </div>

    <!-- Utility Grid -->
    <div class="card card-grid">
      <div class="card-top">
        <div>
          <div class="card-title">🗼 Utility Grid</div>
          <button id="btn-grid-fault" class="btn-fault healthy" onclick="toggleGridFault()">GRID: HEALTHY</button>
        </div>
        <div class="icon-circle">🗼<span id="grid-node-kw">0.0 kW</span></div>
      </div>
      <div>
        <span id="grid-badge" class="status-badge" style="background:#dbeafe; color:#1d4ed8;">EXPORT ➔</span>
      </div>
    </div>

    <!-- Grid Load -->
    <div class="card card-gload">
      <div class="card-top">
        <div>
          <div class="card-title">🏠 Grid Load</div>
          <div class="metric-lbl">Non-Critical Loads</div>
        </div>
        <div class="icon-circle">🏠<span id="gload-node-kw">8.0 kW</span></div>
      </div>
      <div class="slider-row">
        <span>Load:</span>
        <input type="range" id="slider-gload" min="0" max="30" step="0.5" value="8" oninput="updateSim()">
        <span id="lbl-gload">8.0 kW</span>
      </div>
    </div>

    <!-- Backup Load -->
    <div class="card card-bload">
      <div class="card-top">
        <div>
          <div class="card-title">🛡️ Backup Load</div>
          <div class="metric-lbl">Critical UPS Bus</div>
        </div>
        <div class="icon-circle">🛡️<span id="bload-node-kw">12.0 kW</span></div>
      </div>
      <div class="slider-row">
        <span>Load:</span>
        <input type="range" id="slider-bload" min="0" max="40" step="0.5" value="12" oninput="updateSim()">
        <span id="lbl-bload">12.0 kW</span>
      </div>
    </div>
  </div>
</div>

<script>
  let gridHealthy = true;

  function setScenario(pv, soc, bload, gload, grid) {
    document.getElementById('slider-pv').value = pv;
    document.getElementById('slider-soc').value = soc;
    document.getElementById('slider-bload').value = bload;
    document.getElementById('slider-gload').value = gload;
    gridHealthy = grid;
    updateGridBtn();
    updateSim();
  }

  function toggleGridFault() {
    gridHealthy = !gridHealthy;
    updateGridBtn();
    updateSim();
  }

  function updateGridBtn() {
    const btn = document.getElementById('btn-grid-fault');
    if (gridHealthy) {
      btn.className = "btn-fault healthy";
      btn.innerText = "GRID: HEALTHY";
    } else {
      btn.className = "btn-fault";
      btn.innerText = "🚨 PHASE FAULT";
    }
  }

  function updateSim() {
    let pvRaw = parseFloat(document.getElementById('slider-pv').value);
    let soc = parseInt(document.getElementById('slider-soc').value);
    let gloadRaw = parseFloat(document.getElementById('slider-gload').value);
    let bload = parseFloat(document.getElementById('slider-bload').value);

    document.getElementById('lbl-pv').innerText = pvRaw.toFixed(1) + " kW";
    document.getElementById('lbl-soc').innerText = soc + "%";
    document.getElementById('lbl-gload').innerText = gloadRaw.toFixed(1) + " kW";
    document.getElementById('lbl-bload').innerText = bload.toFixed(1) + " kW";
    document.getElementById('bat-node-soc').innerText = soc + "%";

    let gload = gridHealthy ? gloadRaw : 0.0;
    let totalLoad = bload + gload;
    let pvOut = pvRaw;
    let freq = 50.00;
    let batPower = 0.0;
    let gridPower = 0.0;

    if (gridHealthy) {
      document.getElementById('gti-status-msg').innerText = "Grid Synchronized (50.00 Hz)";
      document.getElementById('freq-meter').innerText = "50.00 Hz";

      if (pvOut >= totalLoad) {
        let surplus = pvOut - totalLoad;
        let maxCharge = (soc >= 100) ? 0 : 25;
        let toBat = Math.min(surplus, maxCharge);
        batPower = toBat;
        gridPower = surplus - toBat;
      } else {
        let deficit = totalLoad - pvOut;
        let maxDischarge = (soc <= 10) ? 0 : 25;
        let fromBat = Math.min(deficit, maxDischarge);
        batPower = -fromBat;
        gridPower = -(deficit - fromBat);
      }
    } else {
      if (soc >= 100 && pvRaw > bload) {
        pvOut = bload;
        freq = 51.50;
        document.getElementById('gti-status-msg').innerText = "FSPC Throttled (100% SoC)";
      } else {
        document.getElementById('gti-status-msg').innerText = "Island Reference (50.00 Hz)";
      }
      document.getElementById('freq-meter').innerText = freq.toFixed(2) + " Hz";

      if (pvOut >= bload) {
        let surplus = pvOut - bload;
        batPower = (soc >= 100) ? 0 : Math.min(surplus, 25);
      } else {
        let deficit = bload - pvOut;
        let maxDischarge = (soc <= 10) ? 0 : 25;
        batPower = -Math.min(deficit, maxDischarge);
      }
      gridPower = 0.0;
    }

    document.getElementById('pv-node-kw').innerText = pvRaw.toFixed(1) + " kW";
    document.getElementById('gti-node-kw').innerText = pvOut.toFixed(1) + " kW";
    document.getElementById('gload-node-kw').innerText = gload.toFixed(1) + " kW";
    document.getElementById('bload-node-kw').innerText = bload.toFixed(1) + " kW";
    document.getElementById('grid-node-kw').innerText = Math.abs(gridPower).toFixed(1) + " kW";

    const batBadge = document.getElementById('bat-badge');
    const flowBatHub = document.getElementById('flow-bat-hub');
    const batFlowInfo = document.getElementById('bat-flow-info');
    const batFlowVal = document.getElementById('bat-flow-val');

    if (batPower > 0.05) {
      batBadge.innerText = "STATUS: CHARGING ↑";
      batBadge.style.background = "#dcfce7";
      batBadge.style.color = "#15803d";
      batFlowInfo.style.color = "#15803d";
      batFlowVal.innerText = `+${batPower.toFixed(1)} kW (Entering)`;
      flowBatHub.style.display = "block";
      flowBatHub.className.baseVal = "pipe-flow reverse-flow";
      flowBatHub.style.stroke = "#10b981";
      flowBatHub.setAttribute("marker-start", "url(#arrow-green)");
      flowBatHub.removeAttribute("marker-end");
    } else if (batPower < -0.05) {
      batBadge.innerText = "STATUS: DISCHARGING ↓";
      batBadge.style.background = "#cffafe";
      batBadge.style.color = "#0e7490";
      batFlowInfo.style.color = "#0891b2";
      batFlowVal.innerText = `-${Math.abs(batPower).toFixed(1)} kW (Leaving)`;
      flowBatHub.style.display = "block";
      flowBatHub.className.baseVal = "pipe-flow";
      flowBatHub.style.stroke = "#06b6d4";
      flowBatHub.setAttribute("marker-end", "url(#arrow-cyan)");
      flowBatHub.removeAttribute("marker-start");
    } else {
      batBadge.innerText = "STATUS: IDLE";
      batBadge.style.background = "#f1f5f9";
      batBadge.style.color = "#64748b";
      batFlowInfo.style.color = "#64748b";
      batFlowVal.innerText = "0.0 kW (Idle)";
      flowBatHub.style.display = "none";
    }

    const gridBadge = document.getElementById('grid-badge');
    const flowGridHub = document.getElementById('flow-grid-hub');
    if (!gridHealthy) {
      gridBadge.innerText = "PHASE FAULT / ISOLATED";
      gridBadge.style.background = "#fee2e2";
      gridBadge.style.color = "#b91c1c";
      flowGridHub.style.display = "none";
    } else if (gridPower > 0.05) {
      gridBadge.innerText = "EXPORT ➔";
      gridBadge.style.background = "#dbeafe";
      gridBadge.style.color = "#1d4ed8";
      flowGridHub.style.display = "block";
      flowGridHub.className.baseVal = "pipe-flow reverse-flow";
      flowGridHub.style.stroke = "#2563eb";
      flowGridHub.setAttribute("marker-start", "url(#arrow-blue)");
      flowGridHub.removeAttribute("marker-end");
    } else if (gridPower < -0.05) {
      gridBadge.innerText = "IMPORT ➔";
      gridBadge.style.background = "#cffafe";
      gridBadge.style.color = "#0284c7";
      flowGridHub.style.display = "block";
      flowGridHub.className.baseVal = "pipe-flow";
      flowGridHub.style.stroke = "#0284c7";
      flowGridHub.setAttribute("marker-end", "url(#arrow-cyan)");
      flowGridHub.removeAttribute("marker-start");
    } else {
      gridBadge.innerText = "BALANCED";
      gridBadge.style.background = "#f1f5f9";
      gridBadge.style.color = "#64748b";
      flowGridHub.style.display = "none";
    }

    document.getElementById('flow-pv-gti').style.display = pvRaw > 0 ? "block" : "none";
    document.getElementById('flow-gti-hub').style.display = pvOut > 0 ? "block" : "none";
    document.getElementById('flow-hub-gload').style.display = gload > 0 ? "block" : "none";
    document.getElementById('flow-hub-bload').style.display = bload > 0 ? "block" : "none";
  }

  updateSim();
</script>
</body>
</html>
"""

components.html(html_simulation, height=760, scrolling=False)
