import json
import pandas as pd
import streamlit as st

# Configuración de la página para aprovechar todo el ancho en Streamlit Cloud
st.set_page_config(
    page_title="Control de Albaranes", page_icon="📋", layout="wide"
)


# Cargar los datos desde tu archivo Excel o CSV original
@st.cache_data
def load_data():
    # Cambia 'albaranes.xlsx' por el nombre de tu archivo de datos real
    try:
        df = pd.read_excel("albaranes.xlsx")
    except Exception:
        # Si no lo encuentra en local, intenta leer un CSV por defecto
        df = pd.read_csv("albaranes.csv")

    # Asegurar formato de fecha ISO para JavaScript
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d")
    return df


try:
    df_data = load_data()
    raw_data_json = df_data.to_dict(orient="records")
except Exception as e:
    raw_data_json = []

# Plantilla HTML/JS exacta con todas las funciones y diseño solicitados[cite: 1]
html_code = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comanda — Control de Albaranes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
  :root{{
    --ink:#211C17;
    --ink-2:#2B241D;
    --paper:#F7F1E3;
    --paper-2:#EFE6D0;
    --copper:#BE5A2E;
    --olive:#6F7A46;
    --mustard:#D6A13A;
    --rust:#8C3F35;
    --muted:#C9BFAE;
    --muted-2:#8C8271;
    --line:#3A322888;
    --good:#6F7A46;
    --bad:#8C3F35;
  }}
  *{{box-sizing:border-box;}}
  html,body{{margin:0;padding:0;}}
  body{{
    background:var(--ink);
    color:var(--paper);
    font-family:'Inter',sans-serif;
    -webkit-font-smoothing:antialiased;
    min-height:100vh;
  }}
  .wrap{{
    max-width:1240px;
    margin:0 auto;
    padding:28px 20px 80px;
  }}

  /* ===== HEADER ===== */
  .masthead{{
    display:flex;
    justify-content:space-between;
    align-items:flex-end;
    flex-wrap:wrap;
    gap:14px;
    padding-bottom:22px;
    margin-bottom:26px;
    border-bottom:2px dashed var(--line);
    position:relative;
  }}
  .masthead::before{{
    content:"";
    position:absolute;
    left:0; top:-8px;
    width:10px; height:10px;
    border-radius:50%;
    background:var(--ink);
    box-shadow: 0 0 0 2px var(--line);
  }}
  .eyebrow{{
    font-family:'IBM Plex Mono',monospace;
    font-size:11px;
    letter-spacing:.16em;
    text-transform:uppercase;
    color:var(--mustard);
    margin:0 0 6px;
  }}
  h1{{
    font-family:'Zilla Slab',serif;
    font-weight:700;
    font-size:clamp(28px,4.5vw,42px);
    margin:0;
    letter-spacing:-.01em;
    color:var(--paper);
  }}
  .subtitle{{
    font-size:13px;
    color:var(--muted);
    margin-top:6px;
    max-width:520px;
  }}
  .meta-badge{{
    font-family:'IBM Plex Mono',monospace;
    font-size:12px;
    color:var(--ink);
    background:var(--paper);
    padding:9px 14px;
    border-radius:3px;
    text-align:right;
    line-height:1.5;
  }}
  .meta-badge b{{display:block;font-size:13px;color:var(--copper);}}

  /* ===== TICKET RAIL (KPI) ===== */
  .rail{{
    position:relative;
    margin-bottom:34px;
  }}
  .rail-line{{
    position:absolute;
    top:14px; left:0; right:0;
    height:2px;
    background:repeating-linear-gradient(90deg, var(--muted-2) 0 10px, transparent 10px 18px);
    opacity:.5;
  }}
  .tickets{{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:18px;
    position:relative;
  }}
  .ticket{{
    background:var(--paper);
    color:var(--ink);
    border-radius:2px;
    padding:22px 18px 18px;
    position:relative;
    box-shadow:0 10px 24px -12px rgba(0,0,0,.55);
    transform:rotate(var(--tilt,0deg));
    transition:transform .25s ease;
  }}
  .ticket:hover{{ transform:rotate(0deg) translateY(-3px); }}
  .ticket:nth-child(1){{--tilt:-0.6deg;}}
  .ticket:nth-child(2){{--tilt:0.4deg;}}
  .ticket:nth-child(3){{--tilt:-0.3deg;}}
  .ticket:nth-child(4){{--tilt:0.6deg;}}
  .clip{{
    position:absolute;
    top:-15px; left:50%;
    transform:translateX(-50%);
    width:16px; height:16px;
    border-radius:50%;
    background:var(--ink);
    box-shadow:0 0 0 3px var(--ink), inset 0 0 0 2px var(--paper-2);
  }}
  .ticket::after{{
    content:"";
    position:absolute;
    bottom:-1px; left:12px; right:12px;
    height:8px;
    background-image: radial-gradient(circle at 6px 0, transparent 4px, var(--ink) 4px);
    background-size:12px 8px;
    background-repeat:repeat-x;
  }}
  .ticket-label{{
    font-family:'IBM Plex Mono',monospace;
    font-size:10.5px;
    letter-spacing:.1em;
    text-transform:uppercase;
    color:var(--muted-2);
    display:flex;
    align-items:center;
    gap:6px;
  }}
  .dot{{width:7px;height:7px;border-radius:50%;display:inline-block;}}
  .ticket-value{{
    font-family:'Zilla Slab',serif;
    font-weight:700;
    font-size:clamp(20px,2.6vw,27px);
    margin:8px 0 2px;
    color:var(--ink);
    letter-spacing:-.01em;
  }}
  .ticket-sub{{
    font-family:'IBM Plex Mono',monospace;
    font-size:11px;
    color:var(--muted-2);
  }}
  .ticket-sub.up{{color:var(--good);}}
  .ticket-sub.down{{color:var(--bad);}}

  /* ===== FILTER BAR ===== */
  .filters{{
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    align-items:center;
    margin-bottom:24px;
    padding:14px 16px;
    background:var(--ink-2);
    border:1px solid var(--line);
    border-radius:8px;
  }}
  .chip{{
    font-family:'IBM Plex Mono',monospace;
    font-size:12px;
    padding:7px 13px;
    border-radius:20px;
    border:1px solid var(--line);
    background:transparent;
    color:var(--muted);
    cursor:pointer;
    display:flex;
    align-items:center;
    gap:7px;
    transition:.15s;
    user-select:none;
  }}
  .chip:hover{{border-color:var(--muted-2);color:var(--paper);}}
  .chip.active{{
    background:var(--paper);
    color:var(--ink);
    border-color:var(--paper);
    font-weight:600;
  }}
  .chip .dot{{width:8px;height:8px;}}
  .search-wrap{{
    margin-left:auto;
    position:relative;
    flex:1 1 220px;
    max-width:280px;
  }}
  #search{{
    width:100%;
    background:var(--ink);
    border:1px solid var(--line);
    color:var(--paper);
    padding:8px 12px 8px 30px;
    border-radius:20px;
    font-family:'Inter',sans-serif;
    font-size:13px;
    outline:none;
  }}
  #search:focus{{border-color:var(--mustard);}}
  .search-wrap svg{{position:absolute;left:10px;top:50%;transform:translateY(-50%);opacity:.5;}}
  select#monthSel{{
    background:var(--ink);
    border:1px solid var(--line);
    color:var(--paper);
    padding:8px 12px;
    border-radius:20px;
    font-family:'IBM Plex Mono',monospace;
    font-size:12px;
    outline:none;
    cursor:pointer;
  }}
  .results-count{{
    font-family:'IBM Plex Mono',monospace;
    font-size:11px;
    color:var(--muted-2);
    white-space:nowrap;
  }}

  /* ===== CHART GRID ===== */
  .grid2{{
    display:grid;
    grid-template-columns:1.15fr 1fr;
    gap:18px;
    margin-bottom:18px;
  }}
  .panel{{
    background:var(--ink-2);
    border:1px solid var(--line);
    border-radius:8px;
    padding:20px;
  }}
  .panel-title{{
    font-family:'Zilla Slab',serif;
    font-weight:600;
    font-size:16px;
    margin:0 0 4px;
    color:var(--paper);
  }}
  .panel-sub{{
    font-size:11.5px;
    color:var(--muted-2);
    margin-bottom:14px;
    font-family:'IBM Plex Mono',monospace;
  }}
  .chart-box{{position:relative;height:260px;}}
  .chart-box.tall{{height:320px;}}

  .legend-list{{display:flex;flex-direction:column;gap:8px;margin-top:14px;}}
  .legend-row{{display:flex;align-items:center;gap:9px;font-size:12.5px;}}
  .legend-row .dot{{width:9px;height:9px;flex:none;}}
  .legend-row .lname{{color:var(--paper);flex:1;}}
  .legend-row .lval{{font-family:'IBM Plex Mono',monospace;color:var(--muted);}}

  /* ===== TOP PROVEEDORES ===== */
  .provrow{{
    display:grid;
    grid-template-columns:26px 1fr 90px;
    align-items:center;
    gap:10px;
    padding:8px 0;
    border-bottom:1px solid var(--line);
    font-size:12.5px;
  }}
  .provrow:last-child{{border-bottom:none;}}
  .provrank{{font-family:'IBM Plex Mono',monospace;color:var(--muted-2);font-size:11px;}}
  .provname{{color:var(--paper);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .provbar-track{{background:var(--ink);border-radius:3px;height:6px;margin-top:5px;overflow:hidden;}}
  .provbar-fill{{height:100%;background:var(--copper);border-radius:3px;}}
  .provval{{font-family:'IBM Plex Mono',monospace;color:var(--muted);text-align:right;}}

  /* ===== TABLE ===== */
  .table-panel{{margin-top:18px;}}
  .table-scroll{{
    max-height:480px;
    overflow-y:auto;
    border-radius:6px;
    border:1px solid var(--line);
  }}
  table{{width:100%;border-collapse:collapse;font-size:12.5px;}}
  thead th{{
    position:sticky; top:0;
    background:var(--ink);
    text-align:left;
    padding:10px 12px;
    font-family:'IBM Plex Mono',monospace;
    font-size:10.5px;
    letter-spacing:.08em;
    text-transform:uppercase;
    color:var(--muted-2);
    border-bottom:1px solid var(--line);
    cursor:pointer;
    white-space:nowrap;
  }}
  thead th:hover{{color:var(--mustard);}}
  thead th.num{{text-align:right;}}
  tbody td{{
    padding:9px 12px;
    border-bottom:1px solid var(--line);
    color:var(--muted);
    white-space:nowrap;
  }}
  tbody td.num{{text-align:right;font-family:'IBM Plex Mono',monospace;color:var(--paper);}}
  tbody td.neg{{color:var(--rust);}}
  tbody tr:hover td{{background:var(--ink-2);}}
  tbody td.provname{{color:var(--paper);max-width:220px;overflow:hidden;text-overflow:ellipsis;}}
  .tipo-tag{{
    font-family:'IBM Plex Mono',monospace;
    font-size:10px;
    padding:3px 8px;
    border-radius:10px;
    display:inline-flex;
    align-items:center;
    gap:5px;
  }}

  .empty-state{{
    text-align:center;
    padding:50px 20px;
    color:var(--muted-2);
    font-family:'IBM Plex Mono',monospace;
    font-size:13px;
  }}

  footer{{
    text-align:center;
    margin-top:34px;
    font-family:'IBM Plex Mono',monospace;
    font-size:10.5px;
    color:var(--muted-2);
    letter-spacing:.05em;
  }}

  @media (max-width:820px){{
    .tickets{{grid-template-columns:repeat(2,1fr);}}
    .grid2{{grid-template-columns:1fr;}}
    .search-wrap{{max-width:none;flex-basis:100%;order:5;}}
    thead th:nth-child(4), tbody td:nth-child(4){{display:none;}}
  }}
  @media (max-width:480px){{
    .tickets{{grid-template-columns:1fr;}}
  }}

  tbody tr{{cursor:pointer;}}

  /* ===== DETAIL MODAL ===== */
  .modal-overlay{{
    position:fixed; inset:0;
    background:rgba(15,12,9,.72);
    backdrop-filter:blur(2px);
    display:flex; align-items:center; justify-content:center;
    z-index:100;
    padding:24px;
    opacity:0; pointer-events:none;
    transition:opacity .18s ease;
  }}
  .modal-overlay.open{{opacity:1; pointer-events:all;}}
  .receipt{{
    background:var(--paper);
    color:var(--ink);
    width:100%;
    max-width:360px;
    border-radius:2px;
    padding:26px 24px 22px;
    position:relative;
    box-shadow:0 30px 60px -20px rgba(0,0,0,.7);
    transform:translateY(14px) scale(.98);
    transition:transform .2s ease;
    font-family:'IBM Plex Mono',monospace;
    max-height:88vh;
    overflow-y:auto;
  }}
  .modal-overlay.open .receipt{{transform:translateY(0) scale(1);}}
  .receipt::before{{
    content:"";
    position:absolute; top:-1px; left:12px; right:12px; height:8px;
    background-image: radial-gradient(circle at 6px 8px, transparent 4px, var(--ink) 4px);
    background-size:12px 8px; background-repeat:repeat-x;
  }}
  .receipt::after{{
    content:"";
    position:absolute; bottom:-1px; left:12px; right:12px; height:8px;
    background-image: radial-gradient(circle at 6px 0, transparent 4px, var(--ink) 4px);
    background-size:12px 8px; background-repeat:repeat-x;
  }}
  .receipt-close{{
    position:absolute; top:14px; right:14px;
    width:26px; height:26px;
    border:none; background:transparent;
    color:var(--muted-2); cursor:pointer;
    font-size:16px; line-height:1;
    display:flex; align-items:center; justify-content:center;
  }}
  .receipt-close:hover{{color:var(--ink);}}
  .receipt-eyebrow{{
    font-size:10px; letter-spacing:.14em; text-transform:uppercase;
    color:var(--muted-2); text-align:center; margin:6px 0 2px;
  }}
  .receipt-title{{
    font-family:'Zilla Slab',serif; font-weight:700;
    font-size:19px; text-align:center; color:var(--ink);
    margin:0 0 2px; line-height:1.25;
  }}
  .receipt-tag{{
    display:flex; justify-content:center; margin:8px 0 16px;
  }}
  .receipt-tag span{{
    font-size:10.5px; padding:4px 12px; border-radius:12px;
    display:inline-flex; align-items:center; gap:6px;
    text-transform:uppercase; letter-spacing:.06em;
  }}
  .receipt-divider{{
    border:none; border-top:1px dashed #B8AD90; margin:14px 0;
  }}
  .receipt-row{{
    display:flex; justify-content:space-between; align-items:baseline;
    font-size:12.5px; padding:5px 0; color:#5A5140;
  }}
  .receipt-row span:last-child{{color:var(--ink); font-weight:600; text-align:right;}}
  .receipt-total-row{{
    display:flex; justify-content:space-between; align-items:baseline;
    padding:12px 0 4px; margin-top:4px;
  }}
  .receipt-total-row .rt-label{{font-size:12px; color:var(--muted-2); text-transform:uppercase; letter-spacing:.08em;}}
  .receipt-total-row .rt-value{{font-family:'Zilla Slab',serif; font-weight:700; font-size:24px; color:var(--ink);}}
  .receipt-total-row .rt-value.neg{{color:var(--rust);}}
  .receipt-comment{{
    margin-top:14px; padding:12px; background:var(--paper-2);
    border-radius:4px; font-family:'Inter',sans-serif;
    font-size:12px; color:#5A5140; line-height:1.5;
  }}
  .receipt-comment b{{
    display:block; font-family:'IBM Plex Mono',monospace;
    font-size:9.5px; text-transform:uppercase; letter-spacing:.1em;
    color:var(--muted-2); margin-bottom:4px; font-weight:600;
  }}
  .receipt-barcode{{
    margin-top:18px; height:36px;
    background: repeating-linear-gradient(90deg, var(--ink) 0 2px, transparent 2px 5px, var(--ink) 5px 6px, transparent 6px 10px);
    opacity:.85;
  }}
  .receipt-foot{{
    text-align:center; font-size:9.5px; color:var(--muted-2);
    margin-top:8px; letter-spacing:.08em;
  }}
</style>
</head>
<body>
<div class="wrap">

  <div class="masthead">
    <div>
      <p class="eyebrow">Restaurante Caná · La Moraleja</p>
      <h1>Control de Albaranes</h1>
      <p class="subtitle">Panel de control económico interactivo actualizado en tiempo real.</p>
    </div>
    <div class="meta-badge">
      <b id="rangeLabel">—</b>
      periodo analizado
    </div>
  </div>

  <div class="rail">
    <div class="rail-line"></div>
    <div class="tickets" id="ticketRail"></div>
  </div>

  <div class="filters">
    <button class="chip active" data-tipo="Todos"><span class="dot" style="background:var(--paper)"></span>Todos</button>
    <button class="chip" data-tipo="Cocina"><span class="dot" style="background:var(--copper)"></span>Cocina</button>
    <button class="chip" data-tipo="Sala"><span class="dot" style="background:var(--olive)"></span>Sala</button>
    <button class="chip" data-tipo="Otros"><span class="dot" style="background:var(--mustard)"></span>Otros</button>
    <button class="chip" data-tipo="Extras"><span class="dot" style="background:var(--rust)"></span>Extras</button>
    <select id="monthSel">
      <option value="Todos">Todos los meses</option>
    </select>
    <div class="search-wrap">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9BFAE" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input type="text" id="search" placeholder="Buscar proveedor o nº albarán…">
    </div>
    <span class="results-count" id="resultsCount"></span>
  </div>

  <div class="grid2">
    <div class="panel">
      <p class="panel-title">Evolución mensual</p>
      <p class="panel-sub">Gasto total por mes, desglosado por área</p>
      <div class="chart-box tall"><canvas id="trendChart"></canvas></div>
    </div>
    <div class="panel">
      <p class="panel-title">Distribución por área</p>
      <p class="panel-sub">% del gasto filtrado</p>
      <div class="chart-box"><canvas id="donutChart"></canvas></div>
      <div class="legend-list" id="donutLegend"></div>
    </div>
  </div>

  <div class="grid2" style="grid-template-columns:1fr 1fr;">
    <div class="panel">
      <p class="panel-title">Principales proveedores</p>
      <p class="panel-sub">Top 8 por importe total (según filtro activo)</p>
      <div id="provList"></div>
    </div>
    <div class="panel">
      <p class="panel-title">Tickets por semana</p>
      <p class="panel-sub">Volumen de albaranes registrados</p>
      <div class="chart-box"><canvas id="weekChart"></canvas></div>
    </div>
  </div>

  <div class="panel table-panel">
    <p class="panel-title">Detalle de albaranes</p>
    <p class="panel-sub">Haz clic en una columna para ordenar</p>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th data-sort="fecha">Fecha</th>
            <th data-sort="tipo">Área</th>
            <th data-sort="proveedor">Proveedor</th>
            <th data-sort="albaran">Nº Albarán</th>
            <th data-sort="importe" class="num">Base</th>
            <th data-sort="iva" class="num">IVA</th>
            <th data-sort="total" class="num">Total</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </div>

  <footer>Control de Albaranes · Panel interactivo Streamlit</footer>
</div>

<div class="modal-overlay" id="modalOverlay">
  <div class="receipt" id="receiptCard" role="dialog" aria-modal="true">
    <button class="receipt-close" id="receiptClose" aria-label="Cerrar">✕</button>
    <div id="receiptContent"></div>
  </div>
</div>

<script id="raw-data" type="application/json">
{json.dumps(raw_data_json)}
</script>

<script>
(function(){
  const RAW = JSON.parse(document.getElementById('raw-data').textContent);

  const COLORS = {{
    Cocina:'#BE5A2E',
    Sala:'#6F7A46',
    Otros:'#D6A13A',
    Extras:'#8C3F35'
  }};

  const fmtEUR = (n) => n.toLocaleString('es-ES',{{style:'currency',currency:'EUR',maximumFractionDigits:0}});
  const fmtEUR2 = (n) => n.toLocaleString('es-ES',{{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2}});
  const fmtDate = (iso) => {{ if(!iso) return '—'; const [y,m,d]=iso.split('-'); return `${{d}}/${{m}}/${{y.slice(2)}}`; }};
  const monthKey = (iso) => iso ? iso.slice(0,7) : '';
  const MONTH_NAMES = {{'01':'Ene','02':'Feb','03':'Mar','04':'Abr','05':'May','06':'Jun','07':'Jul','08':'Ago','09':'Sep','10':'Oct','11':'Nov','12':'Dic'}};

  let state = {{ tipo:'Todos', month:'Todos', search:'', sortKey:'fecha', sortDir:-1 }};

  const months = [...new Set(RAW.map(r=>monthKey(r.fecha)).filter(Boolean))].sort();
  const monthSel = document.getElementById('monthSel');
  months.forEach(m=>{{
    const [y,mm]=m.split('-');
    const opt = document.createElement('option');
    opt.value = m;
    opt.textContent = `${{MONTH_NAMES[mm] || mm}} ${{y}}`;
    monthSel.appendChild(opt);
  }});

  if(RAW.length > 0){{
    const dates = RAW.map(r=>r.fecha).filter(Boolean).sort();
    if(dates.length) document.getElementById('rangeLabel').textContent = `${{fmtDate(dates[0])}} → ${{fmtDate(dates[dates.length-1])}}`;
  }}

  function getFiltered(){{
    return RAW.filter(r=>{{
      if(state.tipo !== 'Todos' && r.tipo !== state.tipo) return false;
      if(state.month !== 'Todos' && monthKey(r.fecha) !== state.month) return false;
      if(state.search){{
        const s = state.search.toLowerCase();
        const prov = (r.proveedor || '').toLowerCase();
        const alb = String(r.albaran || '').toLowerCase();
        if(!prov.includes(s) && !alb.includes(s)) return false;
      }}
      return true;
    }});
  }}

  let trendChart, donutChart, weekChart;

  function render(){{
    const data = getFiltered();
    renderTickets(data);
    renderDonut(data);
    renderTrend(data);
    renderWeek(data);
    renderProviders(data);
    renderTable(data);
    document.getElementById('resultsCount').textContent = `Mostrando ${{data.length}} de ${{RAW.length}} registros`;
  }}

  function renderTickets(data){{
    const total = data.reduce((a,r)=>a+(r.total||0),0);
    const byTipo = {{Cocina:0,Sala:0,Otros:0,Extras:0}};
    data.forEach(r=> {{ if(byTipo[r.tipo] !== undefined) byTipo[r.tipo] += (r.total||0); }});
    const otrosExtras = byTipo.Otros + byTipo.Extras;

    const cards = [
      {{label:'Total facturado', value: total, sub: `${{data.length}} albaranes`, color:'#211C17'}},
      {{label:'Gasto Cocina', value: byTipo.Cocina, sub: total? `${{(byTipo.Cocina/total*100).toFixed(0)}}% del total`:'—', color:COLORS.Cocina}},
      {{label:'Gasto Sala', value: byTipo.Sala, sub: total? `${{(byTipo.Sala/total*100).toFixed(0)}}% del total`:'—', color:COLORS.Sala}},
      {{label:'Eventos y Otros', value: otrosExtras, sub: total? `${{(otrosExtras/total*100).toFixed(0)}}% del total`:'—', color:COLORS.Otros}},
    ];

    const rail = document.getElementById('ticketRail');
    rail.innerHTML = cards.map(c=>`
      <div class="ticket">
        <div class="clip"></div>
        <div class="ticket-label"><span class="dot" style="background:${{c.color}}"></span>${{c.label}}</div>
        <div class="ticket-value">${{fmtEUR(c.value)}}</div>
        <div class="ticket-sub">${{c.sub}}</div>
      </div>
    `).join('');
  }}

  function renderDonut(data){{
    const byTipo = {{Cocina:0,Sala:0,Otros:0,Extras:0}};
    data.forEach(r=> {{ if(byTipo[r.tipo] !== undefined) byTipo[r.tipo] += (r.total||0); }});
    const total = Object.values(byTipo).reduce((a,b)=>a+b,0) || 1;
    const labels = Object.keys(byTipo);
    const values = labels.map(l=>byTipo[l]);
    const colors = labels.map(l=>COLORS[l]);

    const ctx = document.getElementById('donutChart').getContext('2d');
    if(donutChart) donutChart.destroy();
    donutChart = new Chart(ctx, {{
      type:'doughnut',
      data:{{ labels, datasets:[{{ data: values, backgroundColor: colors, borderColor:'#2B241D', borderWidth:3, hoverOffset:6 }}] }},
      options:{{
        responsive:true, maintainAspectRatio:false,
        cutout:'68%',
        plugins:{{ legend:{{display:false}}, tooltip:{{ callbacks:{{ label:(c)=> ` ${{c.label}}: ${{fmtEUR2(c.raw)}}` }} }} }}
      }}
    });

    const legend = document.getElementById('donutLegend');
    legend.innerHTML = labels.map((l,i)=>`
      <div class="legend-row">
        <span class="dot" style="background:${{colors[i]}}"></span>
        <span class="lname">${{l}}</span>
        <span class="lval">${{total? (values[i]/total*100).toFixed(1):'0.0'}}% · ${{fmtEUR2(values[i])}}</span>
      </div>
    `).join('');
  }}

  function renderTrend(data){{
    const grouped = {{}};
    data.forEach(r=>{{
      if(!r.fecha) return;
      const mk = monthKey(r.fecha);
      grouped[mk] = grouped[mk] || {{Cocina:0,Sala:0,Otros:0,Extras:0}};
      if(grouped[mk][r.tipo] !== undefined) grouped[mk][r.tipo] += (r.total||0);
    }});
    const keys = Object.keys(grouped).sort();
    const labels = keys.map(k=>{{ const [y,m]=k.split('-'); return `${{MONTH_NAMES[m] || m}}`; }});

    const ctx = document.getElementById('trendChart').getContext('2d');
    if(trendChart) trendChart.destroy();
    trendChart = new Chart(ctx, {{
      type:'bar',
      data:{{
        labels,
        datasets:['Cocina','Sala','Otros','Extras'].map(tipo=>({{
          label: tipo,
          data: keys.map(k=>grouped[k][tipo]),
          backgroundColor: COLORS[tipo],
          borderRadius: 3,
          maxBarThickness: 34
        }}))
      }},
      options:{{
        responsive:true, maintainAspectRatio:false,
        scales:{{
          x:{{ stacked:true, grid:{{display:false}}, ticks:{{ color:'#C9BFAE', font:{{family:'IBM Plex Mono',size:11}} }} }},
          y:{{ stacked:true, grid:{{ color:'#3A322855' }}, ticks:{{ color:'#C9BFAE', font:{{family:'IBM Plex Mono',size:10}}, callback:(v)=>fmtEUR(v) }} }}
        }},
        plugins:{{
          legend:{{ position:'top', align:'end', labels:{{ color:'#C9BFAE', boxWidth:9, boxHeight:9, font:{{family:'Inter',size:11.5}} }} }},
          tooltip:{{ callbacks:{{ label:(c)=> ` ${{c.dataset.label}}: ${{fmtEUR2(c.raw)}}` }} }}
        }}
      }}
    });
  }}

  function renderWeek(data){{
    function isoWeek(dStr){{
      const dt = new Date(dStr);
      if(isNaN(dt)) return '2026-W01';
      const target = new Date(dt.valueOf());
      const dayNr = (dt.getUTCDay()+6)%7;
      target.setUTCDate(target.getUTCDate()-dayNr+3);
      const firstThursday = new Date(Date.UTC(target.getUTCFullYear(),0,4));
      const diff = (target - firstThursday)/86400000;
      const week = 1 + Math.round(diff/7);
      return `${{target.getUTCFullYear()}}-W${{String(week).padStart(2,'0')}}`;
    }}
    const grouped = {{}};
    data.forEach(r=>{{
      if(!r.fecha) return;
      const wk = isoWeek(r.fecha);
      grouped[wk] = (grouped[wk]||0)+1;
    }});
    const keys = Object.keys(grouped).sort();
    const labels = keys.map(k=>k.split('-W')[1] || k);

    const ctx = document.getElementById('weekChart').getContext('2d');
    if(weekChart) weekChart.destroy();
    weekChart = new Chart(ctx, {{
      type:'line',
      data:{{
        labels,
        datasets:[{{
          data: keys.map(k=>grouped[k]),
          borderColor:'#D6A13A',
          backgroundColor:'rgba(214,161,58,0.15)',
          fill:true,
          tension:0.35,
          pointRadius:0,
          pointHoverRadius:4,
          borderWidth:2
        }}]
      }},
      options:{{
        responsive:true, maintainAspectRatio:false,
        scales:{{
          x:{{ grid:{{display:false}}, ticks:{{ color:'#8C8271', font:{{family:'IBM Plex Mono',size:9}}, maxTicksLimit:12 }} }},
          y:{{ grid:{{ color:'#3A322855' }}, ticks:{{ color:'#8C8271', font:{{family:'IBM Plex Mono',size:10}}, precision:0 }} }}
        }},
        plugins:{{ legend:{{display:false}}, tooltip:{{ callbacks:{{ title:(c)=>`Semana ${{c[0].label}}`, label:(c)=>` ${{c.raw}} albaranes` }} }} }}
      }}
    });
  }}

  function renderProviders(data){{
    const byProv = {{}};
    data.forEach(r=>{{ const p = r.proveedor || 'Desconocido'; byProv[p] = (byProv[p]||0) + (r.total||0); }});
    const sorted = Object.entries(byProv).sort((a,b)=>b[1]-a[1]).slice(0,8);
    const max = sorted.length? sorted[0][1] : 1;

    const list = document.getElementById('provList');
    if(!sorted.length){{
      list.innerHTML = `<div class="empty-state">Sin resultados para este filtro</div>`;
      return;
    }}
    list.innerHTML = sorted.map(([name,val],i)=>`
      <div class="provrow">
        <div class="provrank">${{String(i+1).padStart(2,'0')}}</div>
        <div>
          <div class="provname">${{name}}</div>
          <div class="provbar-track"><div class="provbar-fill" style="width:${{(val/max*100).toFixed(1)}}%"></div></div>
        </div>
        <div class="provval">${{fmtEUR2(val)}}</div>
      </div>
    `).join('');
  }}

  function renderTable(data){{
    const sorted = [...data].sort((a,b)=>{{
      const k = state.sortKey;
      let av=a[k], bv=b[k];
      if(av === undefined || av === null) av = '';
      if(bv === undefined || bv === null) bv = '';
      if(typeof av === 'string'){{ av=av.toLowerCase(); bv=bv.toLowerCase(); }}
      if(av<bv) return -1*state.sortDir;
      if(av>bv) return 1*state.sortDir;
      return 0;
    }});
    const body = document.getElementById('tableBody');
    if(!sorted.length){{
      body.innerHTML = `<tr><td colspan="7"><div class="empty-state">No hay albaranes que coincidan con la búsqueda</div></td></tr>`;
      return;
    }}
    body.innerHTML = sorted.map((r,i)=>`
      <tr data-idx="${{i}}">
        <td>${{fmtDate(r.fecha)}}</td>
        <td><span class="tipo-tag" style="background:${{COLORS[r.tipo]||'#8C8271'}}22;color:${{COLORS[r.tipo]||'#8C8271'}}"><span class="dot" style="width:6px;height:6px;background:${{COLORS[r.tipo]||'#8C8271'}}"></span>${{r.tipo || '—'}}</span></td>
        <td class="provname">${{r.proveedor || '—'}}</td>
        <td>${{r.albaran || '—'}}</td>
        <td class="num ${{(r.importe||0)<0?'neg':''}}">${{fmtEUR2(r.importe||0)}}</td>
        <td class="num ${{(r.iva||0)<0?'neg':''}}">${{fmtEUR2(r.iva||0)}}</td>
        <td class="num ${{(r.total||0)<0?'neg':''}}">${{fmtEUR2(r.total||0)}}</td>
      </tr>
    `).join('');

    body.querySelectorAll('tr[data-idx]').forEach(tr=>{{
      tr.addEventListener('click', ()=> openReceipt(sorted[+tr.dataset.idx]));
    }});
  }}

  const overlay = document.getElementById('modalOverlay');
  const receiptContent = document.getElementById('receiptContent');

  function fmtDateLong(iso){{
    if(!iso) return '—';
    const [y,m,d] = iso.split('-');
    const MONTH_FULL = {{'01':'enero','02':'febrero','03':'marzo','04':'abril','05':'mayo','06':'junio','07':'julio','08':'agosto','09':'septiembre','10':'octubre','11':'noviembre','12':'diciembre'}};
    return `${{d}} de ${{MONTH_FULL[m] || m}} de ${{y}}`;
  }}

  function openReceipt(r){{
    const imp = r.importe || 0;
    const iva = r.iva || 0;
    const tot = r.total || 0;
    const ivaPct = imp !== 0 ? (iva / imp * 100) : 0;
    const color = COLORS[r.tipo] || '#8C8271';
    receiptContent.innerHTML = `
      <p class="receipt-eyebrow">Restaurante Caná · La Moraleja</p>
      <p class="receipt-title">${{r.proveedor || 'Proveedor'}}</p>
      <div class="receipt-tag"><span style="background:${{color}}22;color:${{color}}">${{r.tipo || '—'}}</span></div>
      <hr class="receipt-divider">
      <div class="receipt-row"><span>Nº albarán</span><span>${{r.albaran || '—'}}</span></div>
      <div class="receipt-row"><span>Fecha</span><span>${{fmtDateLong(r.fecha)}}</span></div>
      <div class="receipt-row"><span>Periodo</span><span>${{r.periodo || '—'}}</span></div>
      <hr class="receipt-divider">
      <div class="receipt-row"><span>Base imponible</span><span>${{fmtEUR2(imp)}}</span></div>
      <div class="receipt-row"><span>IVA (${{ivaPct.toFixed(1)}}%)</span><span>${{fmtEUR2(iva)}}</span></div>
      <div class="receipt-total-row">
        <span class="rt-label">Total</span>
        <span class="rt-value ${{tot<0?'neg':''}}">${{fmtEUR2(tot)}}</span>
      </div>
      ${{r.comentario ? `<div class="receipt-comment"><b>Comentario</b>${{r.comentario}}</div>` : ''}}
      <div class="receipt-barcode"></div>
      <p class="receipt-foot">*** GRACIAS ***</p>
    `;
    overlay.classList.add('open');
  }}

  function closeReceipt(){{ overlay.classList.remove('open'); }}

  document.getElementById('receiptClose').addEventListener('click', closeReceipt);
  overlay.addEventListener('click', (e)=>{ if(e.target === overlay) closeReceipt(); });
  document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') closeReceipt(); });

  document.querySelectorAll('.chip').forEach(chip=>{{
    chip.addEventListener('click', ()=>{{
      document.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));
      chip.classList.add('active');
      state.tipo = chip.dataset.tipo;
      render();
    }});
  }});

  monthSel.addEventListener('change', (e)=>{{ state.month = e.target.value; render(); }});

  let searchTimeout;
  document.getElementById('search').addEventListener('input', (e)=>{{
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(()=>{{ state.search = e.target.value.trim(); render(); }}, 150);
  }});

  document.querySelectorAll('thead th[data-sort]').forEach(th=>{{
    th.addEventListener('click', ()=>{{
      const key = th.dataset.sort;
      if(state.sortKey === key){{ state.sortDir *= -1; }}
      else {{ state.sortKey = key; state.sortDir = key==='fecha' ? -1 : 1; }}
      renderTable(getFiltered());
    }});
  }});

  render();
}})();
</script>
</body>
</html>
"""

st.components.v1.html(html_code, height=1400, scrolling=True)
