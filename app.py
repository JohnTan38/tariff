# app_tariff.py
import os
import io
from datetime import datetime
from typing import Optional
from flask import Flask, render_template_string, request, send_file, redirect, url_for, flash
import pandas as pd
from werkzeug.utils import secure_filename

# ------------------------- Flask + Constants -------------------------
app = Flask(__name__)
app.secret_key = "replace-me"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {'xlsx'}

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>DMS Tariff Data Formatter</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { --bg:#0b1020; --panel:#131a33; --text:#e6e8f0; --muted:#9aa3b2; --accent:#6ea8fe;
            --border:#2a335c; --thead:#0f1530; --flash-bg:#1b233f; --flash-border:#37406b; --flash-text:#ffd8d8; }
    body.light { --bg:#f7f8fc; --panel:#ffffff; --text:#0c1120; --muted:#606a82; --accent:#245ae5;
                 --border:#e5e8f0; --thead:#f2f4f9; --flash-bg:#fff8e1; --flash-border:#ffe082; --flash-text:#8a6d00; }
    body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto; background:var(--bg); color:var(--text); }
    .wrap { max-width: 1100px; margin: 40px auto; padding: 0 16px; }
    .card { background: var(--panel); border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,.10); }
    .pad { padding: 20px; }
    h1 { margin: 0 0 10px; font-size: 26px; letter-spacing: .2px; display:flex; align-items:center; justify-content:space-between; }
    p { color: var(--muted); }
    .theme-btn { background:transparent; border:1px solid var(--border); border-radius:12px; padding:8px 10px; cursor:pointer; display:inline-flex; align-items:center; gap:8px; color:var(--text); }
    .drop { display: block; width: 95%; min-height: 180px; border: 2px dashed var(--border); border-radius: 16px; padding: 28px; text-align: center; transition: .2s; background:var(--thead); }
    .drop.dragover { border-color: var(--accent); }
    .btn { display:inline-flex; align-items:center; gap:10px; background: var(--accent); color:#fff; padding: 10px 14px; border-radius: 12px; text-decoration:none; border:0; cursor:pointer; font-weight: 600; }
    .btn:focus { outline: 2px solid var(--text); outline-offset: 2px; }
    .muted { color: var(--muted); font-size: 14px; }
    .row { display:flex; gap: 16px; flex-wrap: wrap; }
    .col { flex: 1 1 460px; }
    table { width:100%; border-collapse: collapse; font-size: 14px; }
    th, td { border-bottom: 1px solid var(--border); padding: 8px 10px; text-align:left; }
    th { position: sticky; top: 0; background: var(--thead); z-index: 1; }
    .scroll { max-height: 420px; overflow:auto; border-radius: 12px; border:1px solid var(--border); }
    .icon { width: 18px; height: 18px; }
    .flash { background:var(--flash-bg); border:1px solid var(--flash-border); padding:10px 12px; border-radius:10px; color:var(--flash-text); margin-bottom:12px;}
    .tiny { font-size:12px; color:var(--muted); }
    input[type=file] { display: none; }
    .or { color:var(--muted); font-size: 12px; margin: 6px 0; }
    .badge { display:inline-block; font-size:12px; padding:4px 8px; border:1px solid var(--border); border-radius:999px; color:var(--muted); }
    code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }

    /* Gradient title styles */
    .gradient-text {
      background: linear-gradient(45deg, #3b82f6, #8b5cf6, #ec4899, #f59e0b);
      background-size: 300% 300%;
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      color: transparent;
      font-weight: 700;
      animation: gradientShift 4s ease-in-out infinite;
    }
    @keyframes gradientShift {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }

    /* Respect theme: make gradient visible on light and dark backgrounds */
    body.light .gradient-text { filter: none; }

  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="pad">
        <h1>
          <span class="gradient-text">DMS Tariff Data Formatter</span>
          <button id="themeBtn" class="theme-btn" type="button" title="Toggle theme">
            <svg id="sun" class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M12 18a6 6 0 1 0 0-12a6 6 0 0 0 0 12Zm0 4a1 1 0 0 1-1-1v-1a1 1 0 1 1 2 0v1a1 1 0 0 1-1 1ZM4 13H3a1 1 0 1 1 0-2h1a1 1 0 1 1 0 2Zm17 0h-1a1 1 0 1 1 0-2h1a1 1 0 1 1 0 2ZM5.64 19.36a1 1 0 0 1 0-1.41l.71-.71a1 1 0 0 1 1.41 1.41l-.71.71a1 1 0 0 1-1.41 0ZM16.24 8.76a1 1 0 0 1 0-1.41l.71-.71a1 1 0 1 1 1.41 1.41l-.71.71a1 1 0 0 1-1.41 0ZM4.93 6.34a1 1 0 0 1 1.41 0l.71.71A1 1 0 1 1 5.64 8.46l-.71-.71a1 1 0 0 1 0-1.41Zm12.02 12.02a1 1 0 0 1 1.41 0l.71.71a1 1 0 0 1-1.41 1.41l-.71-.71a1 1 0 0 1 0-1.41Z"/></svg>
            <svg id="moon" class="icon" style="display:none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 1 0 9.79 9.79Z"/></svg>
            <span id="themeLabel" class="tiny">Light/Dark</span>
          </button>
        </h1>
        <p class="muted">Upload 1 Excel file (<b>.xlsx</b>). If the workbook has a sheet named <b>cosco</b>, we’ll run the COSCO parser. If it has <b>hapaq</b> (or <b>hapag</b>), we’ll run the HAPAG formatter. You’ll get a download and a preview.</p>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for m in messages %}
              <div class="flash">{{ m }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <form id="upload-form" action="{{ url_for('process') }}" method="post" enctype="multipart/form-data">
          <label for="file" class="drop" id="drop">
            <div style="display:flex; flex-direction:column; gap:8px; align-items:center;">
              <div class="flex">
                <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a4 4 0 010 8h-1m-3-8v10m0 0l-3-3m3 3l3-3"/></svg>
                <b>Drag & drop</b> your .xlsx here
              </div>
              <div class="or">or</div>
              <button class="btn" type="button" onclick="document.getElementById('file').click()">Choose file</button>
              <div class="tiny">Only .xlsx is accepted</div>
            </div>
            <input id="file" type="file" name="file" accept=".xlsx" />
          </label>
          <div style="margin-top: 12px;">
            <button class="btn" type="submit">Process</button>
            <span class="badge">Steps: Upload → Extract → Download & Preview</span>
          </div>
        </form>

        {% if download_ready %}
          <hr style="border-color:var(--border); margin: 20px 0;">
          <div class="row">
            <div class="col">
              <div class="flex">
                <a class="btn" href="{{ url_for('download', token=download_token) }}" title="Download Excel">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M5 20h14a1 1 0 0 0 0-2H5a1 1 0 1 0 0 2Zm7-3a1 1 0 0 0 1-1V7a1 1 0 1 0-2 0v9a1 1 0 0 0 1 1Zm-3.707-4.293a1 1 0 0 0 1.414 1.414L12 10.828l2.293 2.293a1 1 0 1 0 1.414-1.414l-3-3a1 1 0 0 0-1.414 0l-3 3Z"/>
                  </svg>
                  Download <b>{{ download_name }}</b>
                </a>
                <div class="muted">Processed at {{ processed_at }}</div>
              </div>
              <div style="margin-top: 10px;" class="tiny">
                File token: <code>{{ download_token }}</code> • Detected mode: <code>{{ mode }}</code> • Sheet: <code>{{ sheet_used }}</code>
              </div>
            </div>
          </div>

          <div style="margin-top: 18px;">
            <h3 style="margin:0 0 8px;">Top 10 Rows Preview</h3>
            <div class="scroll">
              <table>
                <thead>
                  <tr>
                    {% for c in columns %}<th>{{ c }}</th>{% endfor %}
                  </tr>
                </thead>
                <tbody>
                  {% for row in head_rows %}
                    <tr>
                      {% for c in columns %}
                        <td>{{ row[c] if row[c] is not none else "" }}</td>
                      {% endfor %}
                    </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
            <div class="tiny" style="margin-top:8px;">Showing first 10 rows only.</div>
          </div>
        {% endif %}
      </div>
    </div>
  </div>

<script>
  // Drag & Drop
  const drop = document.getElementById('drop');
  const fileInput = document.getElementById('file');
  ['dragenter','dragover'].forEach(evt => drop.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); drop.classList.add('dragover'); }));
  ['dragleave','drop'].forEach(evt => drop.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); drop.classList.remove('dragover'); }));
  drop.addEventListener('drop', e => { fileInput.files = e.dataTransfer.files; const ev = new Event('change'); fileInput.dispatchEvent(ev); });

  // On-file selected UX
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      const fileName = fileInput.files[0].name;
      const dropContent = document.querySelector('#drop > div');
      dropContent.innerHTML = `
        <div class="flex">
          <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5l1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          <b>${fileName}</b>
        </div>
        <div class="muted">xlsx upload ready — click <b>Process</b>.</div>
      `;
    }
  });

  // Theme toggle (persist to localStorage)
  const themeBtn = document.getElementById('themeBtn');
  const sun = document.getElementById('sun');
  const moon = document.getElementById('moon');
  const label = document.getElementById('themeLabel');

  function applyTheme(t){
    document.body.classList.toggle('light', t === 'light');
    sun.style.display = t === 'light' ? 'none' : '';
    moon.style.display = t === 'light' ? '' : 'none';
    label.textContent = t === 'light' ? 'Light' : 'Dark';
    localStorage.setItem('theme', t);
  }
  const saved = localStorage.getItem('theme') || 'dark';
  applyTheme(saved);
  themeBtn.addEventListener('click', () => applyTheme(document.body.classList.contains('light') ? 'dark' : 'light'));
</script>
</body>
</html>
"""

# ------------------------- COSCO Parser -------------------------
EXPECTED_COLUMNS = [
    'component','description','repair_code','repair_description',
    'material','length','width','measurement',
    'hours_calc','material_calc',
    'hour_rate_qty_from','hour_rate_qty_to','hour',
    'material_price_qty_from','material_price_qty_to','price'
]
HEADER_KEYS = ('component', 'repair code', 'material', 'measurement')

def _find_header_row(sheet_df: pd.DataFrame) -> int:
    for i in range(len(sheet_df)):
        row = sheet_df.iloc[i].astype(str).str.lower().tolist()
        if all(key in row for key in HEADER_KEYS):
            return i
    raise ValueError("Could not locate the tariff header row (Component/Repair Code/Material/Measurement).")

def _column_map(sheet_df: pd.DataFrame, header_row: int) -> dict:
    row = sheet_df.iloc[header_row].astype(str).str.strip().tolist()
    cmap = {}
    for j, val in enumerate(row):
        v = val.lower()
        if v == 'component' and 'component' not in cmap: cmap['component'] = j
        elif v == 'description' and 'description' not in cmap: cmap['description'] = j
        elif v == 'repair code': cmap['repair_code'] = j
        elif v == 'description' and 'repair_description' not in cmap and 'description' in cmap: cmap['repair_description'] = j
        elif v == 'material': cmap['material'] = j
        elif v == 'length': cmap['length'] = j
        elif v == 'width': cmap['width'] = j
        elif v == 'measurement': cmap['measurement'] = j
        elif v == 'hours calc': cmap['hours_calc'] = j
        elif v == 'material calc': cmap['material_calc'] = j
    return cmap

def _to_float(x):
    try:
        if isinstance(x, str):
            x = x.replace(",", "").strip()
        return float(x)
    except Exception:
        return None

def parse_tariff_excel(xlsx_bytes: bytes, sheet_name_hint: str | None = None) -> pd.DataFrame:
    """
    Robust parser for admmr_tariff* layouts (COSCO).
    Supports split and combined layouts.
    """
    excel = pd.ExcelFile(io.BytesIO(xlsx_bytes))
    # choose sheet by hint or first with our header keys
    if sheet_name_hint and sheet_name_hint in excel.sheet_names:
        df = pd.read_excel(excel, sheet_name=sheet_name_hint, header=None)
    else:
        df = None
        for name in excel.sheet_names:
            tmp = pd.read_excel(excel, sheet_name=name, header=None)
            try:
                _find_header_row(tmp); df = tmp; break
            except Exception:
                continue
        if df is None:
            df = pd.read_excel(excel, sheet_name=excel.sheet_names[0], header=None)

    header_row = _find_header_row(df)
    cmap = _column_map(df, header_row)

    records = []
    n = len(df)
    i = header_row + 1

    def nonempty(v):
        return not (pd.isna(v) or str(v).strip() == "" or str(v).lower() == "nan")

    def is_item_row(row):
        return (nonempty(row[cmap['component']]) and
                nonempty(row[cmap['description']]) and
                nonempty(row[cmap['repair_code']]))

    while i < n:
        row = df.iloc[i]
        if not is_item_row(row):
            i += 1
            continue

        base = {
            'component': str(row[cmap['component']]).strip(),
            'description': str(row[cmap['description']]).strip(),
            'repair_code': str(row[cmap['repair_code']]).strip(),
            'repair_description': str(row.get(cmap.get('repair_description'), "")).strip(),
            'material': str(row.get(cmap.get('material'), "")).strip(),
            'length': str(row.get(cmap.get('length'), "")).strip(),
            'width': str(row.get(cmap.get('width'), "")).strip(),
            'measurement': str(row.get(cmap.get('measurement'), "")).strip(),
            'hours_calc': str(row.get(cmap.get('hours_calc'), "")).strip(),
            'material_calc': str(row.get(cmap.get('material_calc'), "")).strip(),
        }
        i += 1

        hour_rates = []
        material_prices = []

        while i < n:
            row_text = " ".join(str(x) for x in df.iloc[i].tolist()).lower()

            if is_item_row(df.iloc[i]):
                break

            if "hour rate" in row_text:
                j = i + 1
                if j >= n: break
                header = df.iloc[j].astype(str).str.strip().tolist()

                qty_from_idx = [idx for idx, v in enumerate(header) if v.lower() == "qty from"]
                qty_to_idx   = [idx for idx, v in enumerate(header) if v.lower() == "qty to"]
                hour_idx     = [idx for idx, v in enumerate(header) if v.lower() == "hour"]
                price_idx    = [idx for idx, v in enumerate(header) if v.lower() == "price"]

                combined = (len(qty_from_idx) >= 2 and len(qty_to_idx) >= 2 and len(hour_idx) >= 1 and len(price_idx) >= 1)

                i = j + 1
                if combined:
                    hr_from, hr_to, hr_col = qty_from_idx[0], qty_to_idx[0], hour_idx[0]
                    mp_from, mp_to, mp_col = qty_from_idx[1], qty_to_idx[1], price_idx[0]

                    while i < n:
                        nxt = df.iloc[i]
                        if is_item_row(nxt):
                            break
                        qf_hr = _to_float(nxt[hr_from]) if hr_from is not None else None
                        qt_hr = _to_float(nxt[hr_to])   if hr_to   is not None else None
                        hour  = _to_float(nxt[hr_col])  if hr_col  is not None else None
                        qf_mp = _to_float(nxt[mp_from]) if mp_from is not None else None
                        qt_mp = _to_float(nxt[mp_to])   if mp_to   is not None else None
                        price = _to_float(nxt[mp_col])  if mp_col  is not None else None

                        if all(v is None for v in [qf_hr, qt_hr, hour, qf_mp, qt_mp, price]):
                            i += 1; continue

                        rec = dict(base)
                        rec.update({
                            'hour_rate_qty_from': qf_hr, 'hour_rate_qty_to': qt_hr, 'hour': hour,
                            'material_price_qty_from': qf_mp, 'material_price_qty_to': qt_mp, 'price': price
                        })
                        records.append(rec)
                        i += 1
                    continue

                else:
                    while i < n and ("qty from" in " ".join(str(x) for x in df.iloc[i].astype(str)).lower()):
                        i += 1
                    while i < n:
                        nxt = df.iloc[i]
                        if is_item_row(nxt) or "material price" in " ".join(str(x) for x in nxt.astype(str)).lower() or "hour rate" in " ".join(str(x) for x in nxt.astype(str)).lower():
                            break
                        vals = [ _to_float(x) for x in nxt.tolist() ]
                        nums = [v for v in vals if v is not None]
                        if len(nums) >= 3:
                            hour_rates.append({'hour_rate_qty_from': nums[0], 'hour_rate_qty_to': nums[1], 'hour': nums[2]})
                        i += 1
                    continue

            if "material price" in row_text:
                i += 1
                while i < n and ("qty from" in " ".join(str(x) for x in df.iloc[i].astype(str)).lower()):
                    i += 1
                while i < n:
                    nxt = df.iloc[i]
                    if is_item_row(nxt) or "hour rate" in " ".join(str(x) for x in nxt.astype(str)).lower() or "material price" in " ".join(str(x) for x in nxt.astype(str)).lower():
                        break
                    vals = [ _to_float(x) for x in nxt.tolist() ]
                    nums = [v for v in vals if v is not None]
                    if len(nums) >= 3:
                        material_prices.append({'material_price_qty_from': nums[0], 'material_price_qty_to': nums[1], 'price': nums[2]})
                    i += 1
                continue

            i += 1

        if hour_rates or material_prices:
            if len(hour_rates) == len(material_prices) and len(hour_rates) > 0:
                pairs = zip(hour_rates, material_prices)
            elif hour_rates and material_prices:
                from itertools import product
                pairs = product(hour_rates, material_prices)
            else:
                pairs = [(hr or {}, mp or {}) for hr in (hour_rates or [{}]) for mp in (material_prices or [{}])]

            for hr, mp in pairs:
                rec = dict(base)
                rec.update({
                    'hour_rate_qty_from': hr.get('hour_rate_qty_from'),
                    'hour_rate_qty_to': hr.get('hour_rate_qty_to'),
                    'hour': hr.get('hour'),
                    'material_price_qty_from': mp.get('material_price_qty_from'),
                    'material_price_qty_to': mp.get('material_price_qty_to'),
                    'price': mp.get('price')
                })
                records.append(rec)

    out = pd.DataFrame.from_records(records, columns=EXPECTED_COLUMNS)
    for c in EXPECTED_COLUMNS:
        if c not in out.columns:
            out[c] = None
    return out[EXPECTED_COLUMNS]

# ------------------------- HAPAG Formatter -------------------------
def _s(x) -> str:
    return str(x).strip() if pd.notna(x) else ""

def format_tariff_hap(xlsx_bytes: bytes, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Parse the HAPAG sheet -> long form table
    Columns:
      Component, Component Description, Repair Code, Repair Description,
      Material, Length, Width, Measurement, Hours Calc, Material Calc,
      Block, Metric, Qty From, Qty To, Value
    """
    xls = pd.ExcelFile(io.BytesIO(xlsx_bytes))
    target_sheet = sheet_name or xls.sheet_names[0]
    df = pd.read_excel(xls, target_sheet, header=None)

    rows = []
    n = len(df)
    i = 0

    KEYWORDS = {"Component", "Hour Rate", "Material Price", "Length", "HAPAG", "HAPAQ", "HAPAG-LLOYD"}

    while i < n:
        cell0 = _s(df.iat[i, 0]) if 0 in df.columns else ""
        # Heuristic: treat a non-empty, non-keyword value in col0 as a component header
        if cell0 and cell0 not in KEYWORDS:
            comp         = _s(df.iat[i, 0])
            desc         = _s(df.iat[i, 1]) if 1 in df.columns else ""
            rep_code     = _s(df.iat[i, 2]) if 2 in df.columns else ""
            rep_desc     = _s(df.iat[i, 3]) if 3 in df.columns else ""
            material     = _s(df.iat[i, 4]) if 4 in df.columns else ""
            length       = _s(df.iat[i, 5]) if 5 in df.columns else ""
            width        = _s(df.iat[i, 6]) if 6 in df.columns else ""
            measurement  = _s(df.iat[i, 7]) if 7 in df.columns else ""
            hours_calc   = _s(df.iat[i, 8]) if 8 in df.columns else ""
            material_calc= _s(df.iat[i, 9]) if 9 in df.columns else ""

            j = i + 1
            while j < n and _s(df.iat[j, 0]) == "":
                j += 1

            # Hour Rate block
            if j < n and _s(df.iat[j, 0]) == "Hour Rate":
                j += 1
                while j < n:
                    c0 = _s(df.iat[j, 0])
                    if c0 in {"Hour Rate", "Material Price", "Component", "Length", "HAPAG", "HAPAQ", "HAPAG-LLOYD"}:
                        break
                    hr = df.iat[j, 0] if 0 in df.columns else None
                    qf = df.iat[j, 1] if 1 in df.columns else None
                    qt = df.iat[j, 2] if 2 in df.columns else None
                    hv = df.iat[j, 3] if 3 in df.columns else None
                    has_any = any(pd.notna(x) and str(x).strip() != "" for x in (hr, qf, qt, hv))
                    if has_any:
                        rows.append({
                            "Component": comp,
                            "Component Description": desc,
                            "Repair Code": rep_code,
                            "Repair Description": rep_desc,
                            "Material": material,
                            "Length": length,
                            "Width": width,
                            "Measurement": measurement,
                            "Hours Calc": hours_calc,
                            "Material Calc": material_calc,
                            "Block": "Hour Rate",
                            "Metric": "Hour Rate",
                            "Qty From": qf,
                            "Qty To": qt,
                            "Value": hv if pd.notna(hv) and str(hv).strip() != "" else hr
                        })
                        j += 1
                    else:
                        j += 1
                        break
                while j < n and _s(df.iat[j, 0]) == "":
                    j += 1

            # Material Price block
            if j < n and _s(df.iat[j, 0]) == "Material Price":
                j += 1
                while j < n:
                    c0 = _s(df.iat[j, 0])
                    if c0 in {"Hour Rate", "Material Price", "Component", "Length", "HAPAG", "HAPAQ", "HAPAG-LLOYD"}:
                        break
                    mp = df.iat[j, 0] if 0 in df.columns else None
                    qf = df.iat[j, 1] if 1 in df.columns else None
                    qt = df.iat[j, 2] if 2 in df.columns else None
                    pv = df.iat[j, 3] if 3 in df.columns else None
                    has_any = any(pd.notna(x) and str(x).strip() != "" for x in (mp, qf, qt, pv))
                    if has_any:
                        rows.append({
                            "Component": comp,
                            "Component Description": desc,
                            "Repair Code": rep_code,
                            "Repair Description": rep_desc,
                            "Material": material,
                            "Length": length,
                            "Width": width,
                            "Measurement": measurement,
                            "Hours Calc": hours_calc,
                            "Material Calc": material_calc,
                            "Block": "Material Price",
                            "Metric": "Material Price",
                            "Qty From": qf,
                            "Qty To": qt,
                            "Value": pv if pd.notna(pv) and str(pv).strip() != "" else mp
                        })
                        j += 1
                    else:
                        j += 1
                        break
                while j < n and _s(df.iat[j, 0]) == "":
                    j += 1

            i = max(i + 1, j)
            continue
        i += 1

    out_df = pd.DataFrame(rows, columns=[
        "Component", "Component Description", "Repair Code", "Repair Description",
        "Material", "Length", "Width", "Measurement", "Hours Calc", "Material Calc",
        "Block", "Metric", "Qty From", "Qty To", "Value"
    ])
    return out_df

def append_hour_material_triplets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Append 6 columns based on Metric per row; keep row count.
    """
    required_cols = {'Metric', 'Qty From', 'Qty To', 'Value'}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"Missing required column(s): {sorted(missing)}")

    out = df.copy()
    new_cols = [
        'hour_rate_qty_from', 'hour_rate_qty_to', 'hour',
        'material_price_qty_from', 'material_price_qty_to', 'material_price'
    ]
    for c in new_cols:
        if c not in out.columns:
            out[c] = pd.NA

    metric_norm = out['Metric'].astype(str).str.strip().str.casefold()
    mask_hr = metric_norm == 'hour rate'
    mask_mp = metric_norm == 'material price'

    if mask_hr.any():
        out.loc[mask_hr, ['hour_rate_qty_from', 'hour_rate_qty_to', 'hour']] = (
            out.loc[mask_hr, ['Qty From', 'Qty To', 'Value']].to_numpy()
        )
    if mask_mp.any():
        out.loc[mask_mp, ['material_price_qty_from', 'material_price_qty_to', 'material_price']] = (
            out.loc[mask_mp, ['Qty From', 'Qty To', 'Value']].to_numpy()
        )

    # Optional numeric coercions (kept loose per your prior preference)
    for col in ['hour_rate_qty_from', 'hour_rate_qty_to', 'material_price_qty_from', 'material_price_qty_to', 'Qty From', 'Qty To']:
        out[col] = pd.to_numeric(out[col], errors='ignore')

    out.drop(columns=['Block', 'Qty From', 'Qty To', 'Value'], inplace=True, errors='ignore')
    return out

# ------------------------- Helpers -------------------------
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------- Routes -------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template_string(PAGE, download_ready=False)

@app.route("/process", methods=["POST"])
def process():
    f = request.files.get("file")
    if not f or f.filename == "":
        flash("Please choose a .xlsx file.")
        return redirect(url_for("index"))
    if not allowed_file(f.filename):
        flash("Invalid file type. Only .xlsx is allowed.")
        return redirect(url_for("index"))

    xlsx_bytes = f.read()

    # Decide mode by sheet name
    try:
        xls = pd.ExcelFile(io.BytesIO(xlsx_bytes))
        sheet_names_lower = [s.lower().strip() for s in xls.sheet_names]
    except Exception as e:
        flash(f"Could not open workbook: {e}")
        return redirect(url_for("index"))

    mode = None
    sheet_used = None
    df_out = None
    download_name = None

    # Priority: exact names if present
    if any(s == "cosco" for s in sheet_names_lower):
        mode = "COSCO"
        sheet_used = xls.sheet_names[sheet_names_lower.index("cosco")]
        df_out = parse_tariff_excel(xlsx_bytes, sheet_name_hint=sheet_used)
        # Drop completely empty numeric blocks
        cols_to_check = ['hour_rate_qty_from','hour_rate_qty_to','hour','material_price_qty_from','material_price_qty_to','price']
        df_out = df_out.copy()
        df_out.dropna(subset=cols_to_check, how='all', inplace=True)
        # Output filename
        download_name = "tariff_cosco_formatted.xlsx"

    elif any(s in ("hapaq", "hapag") for s in sheet_names_lower):
        # Accept both spellings
        idx = next(i for i, s in enumerate(sheet_names_lower) if s in ("hapaq", "hapag"))
        sheet_used = xls.sheet_names[idx]
        mode = "HAPAG"
        long_df = format_tariff_hap(xlsx_bytes, sheet_name=sheet_used)
        df_out = append_hour_material_triplets(long_df)
        download_name = "tariff_hapaq_formatted.xlsx"

    else:
        # Fallback: try COSCO header detection
        try:
            mode = "COSCO (fallback)"
            sheet_used = "auto-detected"
            df_out = parse_tariff_excel(xlsx_bytes, sheet_name_hint=None)
            cols_to_check = ['hour_rate_qty_from','hour_rate_qty_to','hour','material_price_qty_from','material_price_qty_to','price']
            df_out = df_out.copy()
            df_out.dropna(subset=cols_to_check, how='all', inplace=True)
            download_name = "tariff_cosco_formatted.xlsx"
        except Exception:
            # If COSCO parse fails, try HAPAG on first sheet
            try:
                mode = "HAPAG (fallback)"
                sheet_used = xls.sheet_names[0]
                long_df = format_tariff_hap(xlsx_bytes, sheet_name=sheet_used)
                df_out = append_hour_material_triplets(long_df)
                download_name = "tariff_hapag_formatted.xlsx"
            except Exception as e2:
                flash(f"Failed to parse workbook using both modes: {e2}")
                return redirect(url_for("index"))

    # Save Excel
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{('cosco' if 'COSCO' in mode else 'hapag')}_{ts}.xlsx"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    try:
        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            df_out.to_excel(writer, sheet_name="output", index=False)
    except Exception as e:
        flash(f"Failed to write output: {e}")
        return redirect(url_for("index"))

    token = out_name
    head_rows = df_out.head(10).where(pd.notnull(df_out), None).to_dict(orient="records")

    return render_template_string(
        PAGE,
        download_ready=True,
        download_token=token,
        processed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        columns=df_out.columns.tolist(),
        head_rows=head_rows,
        mode=mode,
        sheet_used=sheet_used,
        download_name=download_name
    )

@app.route("/download/<token>", methods=["GET"])
def download(token):
    safe_path = os.path.join(OUTPUT_DIR, token)
    if not os.path.isfile(safe_path):
        flash("Download expired or not found. Please reprocess your file.")
        return redirect(url_for("index"))
    # Choose user-facing download name by token prefix
    if token.startswith("cosco_"):
        download_name = "tariff_cosco_formatted.xlsx"
    else:
        download_name = "tariff_hapag_formatted.xlsx"
    return send_file(
        safe_path,
        as_attachment=True,
        download_name=download_name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Optional: simple upload persister (not used by main flow, kept for parity)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(OUTPUT_DIR, filename))
        flash(f'File "{filename}" uploaded successfully!')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload an Excel file (.xlsx).')
        return redirect(request.url)

# ------------------------- Main -------------------------
if __name__ == "__main__":
    # Run with: python app_tariff.py
    app.run(host="0.0.0.0", port=5000, debug=True)
