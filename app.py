import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="OorjaFlow - AC Microgrid Simulation",
    page_icon="⚡",
    layout="wide"
)

st.markdown("<h2 style='text-align: center; color: #1E293B; margin-bottom: 2px;'>⚡ OorjaFlow</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 8px; font-size: 14px;'>AC-Coupled Solar & Storage Power Flow Simulator</p>", unsafe_allow_html=True)

# ----------------- SESSION STATE -----------------
defaults = {
    "grid_connected": True,
    "grid_load_present": True,
    "solar_pv": 26.0,
    "battery_soc": 65,
    "backup_load": 12.0,
    "grid_load_demand": 8.0,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ----------------- DISPATCH LOGIC -----------------
BATTERY_MAX_CHARGE_KW = 25.0
BATTERY_MAX_DISCHARGE_KW = 25.0
freq_hz = 50.0
grid_fault = not st.session_state.grid_connected

if st.session_state.grid_connected and st.session_state.grid_load_present:
    effective_grid_load = float(st.session_state.grid_load_demand)
else:
    effective_grid_load = 0.0

ac_solar_pv = float(st.session_state.solar_pv)
backup_load = float(st.session_state.backup_load)
soc = int(st.session_state.battery_soc)

if not grid_fault:
    total_demand = backup_load + effective_grid_load
    if ac_solar_pv >= total_demand:
        surplus = ac_solar_pv - total_demand
        batt_charge = min(surplus, BATTERY_MAX_CHARGE_KW) if soc < 100 else 0.0
        batt_discharge = 0.0
        grid_export = surplus - batt_charge
        grid_import = 0.0
    else:
        grid_export = 0.0
        if ac_solar_pv < backup_load and soc > 10:
            batt_deficit = backup_load - ac_solar_pv
            batt_discharge = min(batt_deficit, BATTERY_MAX_DISCHARGE_KW)
        else:
            batt_discharge = 0.0
        batt_charge = 0.0
        grid_import = total_demand - ac_solar_pv - batt_discharge

    batt_status = "CHARGING" if batt_charge > 0.05 else ("DISCHARGING" if batt_discharge > 0.05 else "IDLE")
    grid_status = "EXPORTING" if grid_export > 0.05 else ("IMPORTING" if grid_import > 0.05 else "BALANCED")
    grid_net_kw = grid_export if grid_export > 0.05 else grid_import

else:
    grid_export = 0.0
    grid_import = 0.0
    grid_net_kw = 0.0
    grid_status = "ISOLATED"
    
    if ac_solar_pv >= backup_load:
        surplus = ac_solar_pv - backup_load
        if soc >= 100:
            batt_charge = 0.0
            freq_hz = 51.5
        else:
            batt_charge = min(surplus, BATTERY_MAX_CHARGE_KW)
            freq_hz = 50.0
        batt_discharge = 0.0
    else:
        deficit = backup_load - ac_solar_pv
        batt_discharge = min(deficit, BATTERY_MAX_DISCHARGE_KW) if soc > 10 else 0.0
        batt_charge = 0.0
        freq_hz = 50.0

    batt_status = "CHARGING" if batt_charge > 0.05 else ("DISCHARGING" if batt_discharge > 0.05 else "IDLE")

batt_kw = batt_charge if batt_status == "CHARGING" else (batt_discharge if batt_status == "DISCHARGING" else 0.0)
batt_badge_color = "#10B981" if batt_status == "CHARGING" else ("#06B6D4" if batt_status == "DISCHARGING" else "#64748B")
grid_badge_color = "#EF4444" if grid_status == "ISOLATED" else ("#3B82F6" if grid_status == "EXPORTING" else "#06B6D4")

pv_to_ac_flow = "flow-down-amber" if ac_solar_pv > 0.05 else "no-flow"
ac_to_hub_flow = "flow-to-hub-orange" if ac_solar_pv > 0.05 else "no-flow"
backup_load_flow = "flow-from-hub-pink" if backup_load > 0.05 else "no-flow"

# ----------------- ANIMATED HTML/SVG DASHBOARD -----------------
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  body {{ margin: 0; padding: 5px; background: #F8FAFC; overflow: hidden; }}
  
  .canvas-container {{
    position: relative;
    max-width: 960px;
    height: 420px;
    margin: 0 auto;
  }}

  .flow-svg {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    pointer-events: none;
  }}

  .base-pipe {{
    stroke: #E2E8F0;
    stroke-width: 6;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }}

  .flow-line {{
    stroke-width: 5;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-dasharray: 8, 12;
  }}

  @keyframes flowRight {{ from {{ stroke-dashoffset: 40; }} to {{ stroke-dashoffset: 0; }} }}
  @keyframes flowLeft {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: 40; }} }}
  @keyframes flowDown {{ from {{ stroke-dashoffset: 40; }} to {{ stroke-dashoffset: 0; }} }}

  .flow-down-amber {{ stroke: #F59E0B; animation: flowDown 0.8s linear infinite; }}
  .flow-to-hub-orange {{ stroke: #F97316; animation: flowRight 0.8s linear infinite; }}
  .flow-to-batt-green {{ stroke: #10B981; animation: flowLeft 0.85s linear infinite; }}
  .flow-from-batt-cyan {{ stroke: #06B6D4; animation: flowRight 0.85s linear infinite; }}
  .flow-from-hub-blue {{ stroke: #3B82F6; animation: flowRight 0.8s linear infinite; }}
  .flow-to-hub-blue {{ stroke: #06B6D4; animation: flowLeft 0.8s linear infinite; }}
  .flow-from-hub-pink {{ stroke: #D946EF; animation: flowRight 0.8s linear infinite; }}
  .no-flow {{ stroke: transparent; }}

  .dashboard {{
    display: grid;
    grid-template-columns: 350px 140px 350px;
    grid-template-rows: 115px 115px 125px;
    gap: 15px;
    position: relative;
    z-index: 2;
    height: 100%;
  }}

  .card {{
    background: #FFFFFF;
    border-radius: 28px;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 3px 10px rgba(0,0,0,0.04);
    border: 1px solid #E2E8F0;
  }}

  .card-left {{ display: flex; flex-direction: column; }}
  .label-line {{ font-size: 14px; font-weight: 700; color: #1E293B; display: flex; align-items: center; gap: 6px; }}
  .sub-text {{ font-size: 11px; color: #64748B; margin-top: 1px; }}
  .status-badge {{ font-size: 11px; font-weight: 800; margin-top: 4px; display: inline-block; padding: 3px 8px; border-radius: 6px; width: fit-content; }}
  
  .icon-circle {{
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    border: 2px solid;
    background: #FFFFFF;
    text-align: center;
  }}

  .solar-card {{ background: #FFFBEB; border-left: 6px solid #F59E0B; }}
  .ac-pv-card {{ background: #FFF7ED; border-left: 6px solid #F97316; }}
  .batt-card  {{ background: #ECFDF5; border-left: 6px solid #10B981; }}
  .grid-combo {{ background: #EFF6FF; border-left: 6px solid #3B82F6; }}
  .bload-card {{ background: #FDF4FF; border-left: 6px solid #D946EF; }}

  .hub {{
    grid-column: 2;
    grid-row: 2;
    background: #FFFFFF;
    border: 4px solid #EAB308;
    border-radius: 50%;
    width: 100px;
    height: 100px;
    margin: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 16px rgba(234, 179, 8, 0.35);
    font-weight: 800;
    color: #1E293B;
    text-align: center;
    z-index: 5;
  }}

  .telemetry-bar {{
    max-width: 960px;
    margin: 8px auto 0 auto;
    display: flex;
    justify-content: space-around;
    background: white;
    padding: 8px 12px;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    font-size: 13px;
    font-weight: 600;
  }}
</style>
</head>
<body>

<div class="canvas-container">
  <svg class="flow-svg" viewBox="0 0 960 420">
    <defs>
      <marker id="arrow-amber" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#F59E0B"/>
      </marker>
      <marker id="arrow-orange" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#F97316"/>
      </marker>
      <marker id="arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#10B981"/>
      </marker>
      <marker id="arrow-cyan" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#06B6D4"/>
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#3B82F6"/>
      </marker>
      <marker id="arrow-pink" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#D946EF"/>
      </marker>
    </defs>

    <!-- Base Alignment Pipes -->
    <path class="base-pipe" d="M 175 115 V 135" />
    <path class="base-pipe" d="M 350 188 H 430" />
    <path class="base-pipe" d="M 350 320 H 430 Q 480 320 480 260 V 236" />
    <path class="base-pipe" d="M 610 95 H 530 Q 480 95 480 130 V 140" />
    <path class="base-pipe" d="M 610 320 H 530 Q 480 320 480 260 V 236" />

    <!-- Active Animated Flow Lines -->
    <path class="flow-line {pv_to_ac_flow}" d="M 175 115 V 135" marker-end="url(#arrow-amber)" />
    <path class="flow-line {ac_to_hub_flow}" d="M 350 188 H 430" marker-end="url(#arrow-orange)" />

    {'<path class="flow-line flow-to-batt-green" d="M 480 236 V 260 Q 480 320 430 320 H 350" marker-end="url(#arrow-green)" />' if batt_status == "CHARGING" else ''}
    {'<path class="flow-line flow-from-batt-cyan" d="M 350 320 H 430 Q 480 320 480 260 V 236" marker-end="url(#arrow-cyan)" />' if batt_status == "DISCHARGING" else ''}

    {'<path class="flow-line flow-from-hub-blue" d="M 480 140 V 130 Q 480 95 530 95 H 610" marker-end="url(#arrow-blue)" />' if grid_status == "EXPORTING" else ''}
    {'<path class="flow-line flow-to-hub-blue" d="M 610 95 H 530 Q 480 95 480 130 V 140" marker-end="url(#arrow-blue)" />' if grid_status == "IMPORTING" else ''}

    <path class="flow-line {backup_load_flow}" d="M 480 236 V 260 Q 480 320 530 320 H 610" marker-end="{'url(#arrow-pink)' if backup_load > 0 else ''}" />
  </svg>

  <div class="dashboard">
    <!-- Top-Left: Solar PV -->
    <div class="card solar-card" style="grid-column: 1; grid-row: 1;">
      <div class="card-left">
        <span class="label-line"><span style="color:#F59E0B">☀️</span> Solar PV Array</span>
        <span class="sub-text">DC Solar Generation</span>
        <span class="status-badge" style="background: #FEF3C7; color: #D97706;">GENERATING ⬇️</span>
      </div>
      <div class="icon-circle" style="border-color: #F59E0B; color: #D97706; background: #FEF3C7;">
        <span>☀️</span>{ac_solar_pv:.1f} kW
      </div>
    </div>

    <!-- Middle-Left: Grid-Tied Inverter -->
    <div class="card ac-pv-card" style="grid-column: 1; grid-row: 2;">
      <div class="card-left">
        <span class="label-line"><span style="color:#F97316">⚡</span> Grid-Tied Inverter</span>
        <span class="sub-text">AC-Coupled (Smart Port)</span>
        <span class="status-badge" style="background: #FFEDD5; color: #EA580C;">AC FEED ➔</span>
      </div>
      <div class="icon-circle" style="border-color: #F97316; color: #EA580C; background: #FFEDD5;">
        <span>🔌</span>{ac_solar_pv:.1f} kW
      </div>
    </div>

    <!-- Bottom-Left: Battery Bank -->
    <div class="card batt-card" style="grid-column: 1; grid-row: 3;">
      <div class="card-left">
        <span class="label-line"><span style="color:#10B981">🔋</span> Battery Bank</span>
        <span class="sub-text">100 kWh LFP Pack</span>
        <span class="status-badge" style="background: {'#D1FAE5' if batt_status=='CHARGING' else ('#CFFAFE' if batt_status=='DISCHARGING' else '#F1F5F9')}; color: {batt_badge_color};">
          {'⚡ CHARGING ➔' if batt_status=='CHARGING' else ('⚡ DISCHARGING ⬅️' if batt_status=='DISCHARGING' else 'IDLE')}
        </span>
      </div>
      <div class="icon-circle" style="border-color: #10B981; color: #059669; background: #D1FAE5;">
        <span>{soc}%</span>{batt_kw:.1f} kW
      </div>
    </div>

    <!-- Center: Hybrid Inverter Hub -->
    <div class="hub">
      <span style="font-size: 18px;">⚡</span>
      <span style="font-size: 11px; font-weight: 800; line-height: 1.2;">HYBRID<br>INVERTER</span>
    </div>

    <!-- Top-Right: COMBINED Utility Grid & Grid Load Block -->
    <div class="card grid-combo" style="grid-column: 3; grid-row: 1 / span 2; height: 245px; flex-direction: column; justify-content: space-around; align-items: stretch; {'opacity: 0.55; border-left: 6px solid #EF4444;' if grid_fault else ''}">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #CBD5E1; padding-bottom: 8px;">
        <div class="card-left">
          <span class="label-line">Utility Grid <span style="color:#3B82F6">|</span> 🗼</span>
          <span class="sub-text">Bi-directional Meter</span>
          <span class="status-badge" style="background: {'#FEE2E2' if grid_status=='ISOLATED' else ('#DBEAFE' if grid_status=='EXPORTING' else '#CFFAFE')}; color: {grid_badge_color};">
            {'GRID ISOLATED ❌' if grid_status=='ISOLATED' else ('EXPORTING ➔' if grid_status=='EXPORTING' else 'IMPORTING ⬅️')}
          </span>
        </div>
        <div class="icon-circle" style="border-color: {grid_badge_color}; color: {grid_badge_color}; background: #DBEAFE;">
          <span>🗼</span>{grid_net_kw:.1f} kW
        </div>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 6px;">
        <div class="card-left">
          <span class="label-line">Grid Load <span style="color:#8B5CF6">|</span> 🏠</span>
          <span class="sub-text">{'OFFLINE (Shed during Fault / Absent)' if effective_grid_load == 0 else 'Non-Critical circuits'}</span>
          <span class="status-badge" style="background: {'#FEE2E2' if effective_grid_load == 0 else '#EDE9FE'}; color: {'#EF4444' if effective_grid_load == 0 else '#8B5CF6'};">
            {'LOAD SHED (OFF)' if effective_grid_load == 0 else 'ACTIVE ➔'}
          </span>
        </div>
        <div class="icon-circle" style="border-color: #8B5CF6; color: #7C3AED; background: #EDE9FE;">
          <span>🏠</span>{effective_grid_load:.1f} kW
        </div>
      </div>
    </div>

    <!-- Bottom-Right: Backup Load -->
    <div class="card bload-card" style="grid-column: 3; grid-row: 3;">
      <div class="icon-circle" style="border-color: #D946EF; color: #A21CAF; background: #FAE8FF;">
        <span>🛡️</span>{backup_load:.1f} kW
      </div>
      <div class="card-left" style="align-items: flex-end;">
        <span class="label-line">Backup Load <span style="color:#D946EF">🛡️</span></span>
        <span class="sub-text">Critical Protected Bus</span>
        <span class="status-badge" style="background: #FAE8FF; color: #D946EF;">ONLINE (UPS) ➔</span>
      </div>
    </div>
  </div>
</div>

<div class="telemetry-bar">
  <div>Mode: <span style="color: {'#EF4444' if grid_fault else '#10B981'}; font-weight:700;">{'GRID-FORMING ISLAND' if grid_fault else 'GRID-FOLLOWING'}</span></div>
  <div>Microgrid Frequency: <span style="color: #2563EB; font-weight:700;">{freq_hz:.2f} Hz</span></div>
  <div>Net Battery Flow: <span style="color: {batt_badge_color}; font-weight:700;">{'+' if batt_status=='CHARGING' else ('-' if batt_status=='DISCHARGING' else '')}{batt_kw:.1f} kW</span></div>
</div>
</body>
</html>
"""

components.html(html_code, height=480)

# ----------------- CONTROLS DECK -----------------
st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

grid_col_left, grid_col_right = st.columns(2)

with grid_col_left:
    grid_btn_label = "🚨 TRIGGER GRID FAULT (ISLAND)" if st.session_state.grid_connected else "✅ RESTORE GRID CONNECTION"
    if st.button(grid_btn_label, use_container_width=True, type="primary" if st.session_state.grid_connected else "secondary"):
        st.session_state.grid_connected = not st.session_state.grid_connected
        st.rerun()

with grid_col_right:
    load_btn_label = "🔌 GRID LOAD: PRESENT (ENABLED)" if st.session_state.grid_load_present else "🔌 GRID LOAD: ABSENT (DISABLED)"
    if st.button(load_btn_label, use_container_width=True):
        st.session_state.grid_load_present = not st.session_state.grid_load_present
        st.rerun()

st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

solar_col, preset_col = st.columns([1.3, 2.7])

with solar_col:
    st.slider("☀️ Solar PV Generation (kW)", 0.0, 50.0, step=0.5, key="solar_pv")

with preset_col:
    st.caption("⚡ Quick Scenarios:")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        if st.button("☀️ Peak Export", use_container_width=True):
            st.session_state.grid_connected = True
            st.session_state.grid_load_present = True
            st.session_state.solar_pv = 38.0
            st.session_state.backup_load = 10.0
            st.session_state.grid_load_demand = 6.0
            st.session_state.battery_soc = 85
            st.rerun()
    with p2:
        if st.button("⛅ Cloud Deficit", use_container_width=True):
            st.session_state.grid_connected = True
            st.session_state.grid_load_present = True
            st.session_state.solar_pv = 6.0
            st.session_state.backup_load = 18.0
            st.session_state.grid_load_demand = 10.0
            st.session_state.battery_soc = 50
            st.rerun()
    with p3:
        if st.button("🌙 Night Outage", use_container_width=True):
            st.session_state.grid_connected = False
            st.session_state.solar_pv = 0.0
            st.session_state.backup_load = 14.0
            st.session_state.battery_soc = 60
            st.rerun()
    with p4:
        if st.button("🔋 100% Curtail", use_container_width=True):
            st.session_state.grid_connected = False
            st.session_state.solar_pv = 32.0
            st.session_state.backup_load = 8.0
            st.session_state.battery_soc = 100
            st.rerun()

s1, s2, s3 = st.columns(3)

with s1:
    st.slider("🔋 Battery SoC (%)", 10, 100, step=1, key="battery_soc")

with s2:
    st.slider("🛡️ Backup Critical Load (kW)", 0.0, 40.0, step=0.5, key="backup_load")

with s3:
    st.slider("🏠 Grid Load Demand (kW)", 0.0, 30.0, step=0.5, key="grid_load_demand")
