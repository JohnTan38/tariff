# DMS Tariff Data Formatter

A lightweight Flask web app that converts carrier tariff Excel files (.xlsx) into a clean, analysis‑ready table with a downloadable Excel output and an on‑page preview.

> **Who is this for?** Operations and data teams who receive carrier tariff spreadsheets (e.g., COSCO, HAPAG) and need a consistent long‑form table for downstream pricing/analytics.

---

## ✨ What the app does
- Accepts a **single .xlsx** upload via drag‑and‑drop or file picker.
- Detects the **shipping company** from the workbook and chooses a parsing pipeline:
  - **COSCO**: robust parser for admmr_tariff‑style layouts; supports **split** and **combined** hour/material blocks.
  - **HAPAG** (default for all other carriers): general formatter that normalizes “Hour Rate” and “Material Price” blocks into a long table, then appends triplet columns for easy analysis.
- Adds the detected **shipping_company** column to the output.
- Saves a processed Excel to disk and shows a **Top‑10 rows preview** in the UI.
- Provides a **Download** button with a user‑friendly filename (e.g., `tariff_cosco_formatted.xlsx`).

---

## 🧭 Quick start (UI)

### UI Screenshots

**Walkthrough Video (6s):**
[![Watch video](https://img.youtube.com/vi/T-D1KVIuvjA/maxresdefault.jpg)](https://youtu.be/91T_Yp8R-Fk))
<video controls src="sandbox:/mnt/data/dms_tariff_walkthrough.webm" width="600"></video>

**Dark mode:**

**Dark mode:**
![alt text](https://github.com/JohnTan38/tariff/blob/master/dark.png?raw=true)
![](sandbox:/mnt/data/dark.png)

**Light mode:**

![alt text](https://github.com/JohnTan38/tariff/blob/master/light.png?raw=true)
![](sandbox:/mnt/data/light.png)

### Steps
1. Open the app in your browser (default: `http://localhost:5000`).
2. Prepare one Excel file (`.xlsx`).
   - Put the **carrier name in cell B2** (e.g., `COSCO`, `HAPAG`, etc.).
3. Drag‑drop the file into the upload zone or click **Choose file**.
4. Click **Process**. You’ll see:
   - A **download** button for the processed Excel.
   - A **Top 10 Rows Preview** table.
   - The **parser mode** used, **sheet** that was parsed, and a file **token** (for reference).
5. (Optional) Toggle **Light/Dark** theme via the header button.

---

## 📥 Input requirements & detection logic

### File type
- Only **`.xlsx`** is accepted.

### Shipping company detection
The app tries the following, in order:
1. Read **cell B2** on each sheet (first match wins).
2. If B2 is empty/unreliable, look for a cell containing a label like **“Shipping Company”** near the top and take the value to its **right** or **below**.
3. Fall back to **`General Carrier`** if nothing is found.

> The **company name** is slugified and used to choose parsing mode and output filenames.

### Parser selection
- If the slugged company name **contains `cosco`**, the app **tries the COSCO parser first**.
- Otherwise it uses the HAPAG pipeline.

### Sheet selection heuristics
- For HAPAG: prefers sheet names like **“hapaq”/“hapag”**. If absent, it also tries a sheet containing the company name. Otherwise uses the **first** sheet.
- For COSCO (when applicable): prefers **“cosco”** or a sheet containing the company name; otherwise falls back to reasonable defaults.

---

## 🔧 What each parser produces

### COSCO parser (admmr_tariff style)
**Output columns (wide table):**
```
component, description, repair_code, repair_description,
material, length, width, measurement,
hours_calc, material_calc,
hour_rate_qty_from, hour_rate_qty_to, hour,
material_price_qty_from, material_price_qty_to, price
```
- Handles both **combined** layouts (where Hour Rate + Material Price are on the same row) and **split** layouts (separate blocks).
- Drops rows where all value columns are `NaN`/empty for the value triplets.
- Inserts `shipping_company` as the first column in the final Excel.

### HAPAG formatter (generic)
1. Parses each **Component** block and normalizes **Hour Rate** and **Material Price** entries into a **long format**:
   - Columns include: `Component`, `Component Description`, `Repair Code`, `Repair Description`, `Material`, `Length`, `Width`, `Measurement`, `Hours Calc`, `Material Calc`, `Block`, `Metric`, `Qty From`, `Qty To`, `Value`.
2. Converts the long format to an analysis‑friendly table by appending these **triplet columns** (row‑wise, preserving row count):
   - `hour_rate_qty_from`, `hour_rate_qty_to`, `hour`
   - `material_price_qty_from`, `material_price_qty_to`, `material_price`
3. Drops helper columns (`Block`, `Qty From`, `Qty To`, `Value`) in the final output.
4. Inserts `shipping_company` as the first column in the final Excel.

---

## 📤 Output

### Example Input (first 3 rows)

```
" + input_md + "
```

### Example Output (first 3 rows)

```
" + output_md + "
```



### Example Input (first 3 rows)
```text
" + input_sample.to_string(index=False) + "
```

### Example Output (first 3 rows)
```text
" + output_sample.to_string(index=False) + "
```


- A single worksheet named **`output`** in a generated `.xlsx` saved to disk.
- Download filename:
  - If the token includes a slug: `tariff_{slug}_formatted.xlsx` (e.g., `tariff_cosco_formatted.xlsx`).
  - Otherwise: `tariff_hapag_formatted.xlsx`.
- The UI shows a **Top 10 rows** preview of the processed DataFrame.

---

## 🖥️ Running locally

### Prerequisites
- **Python 3.10+** (recommended)
- Install dependencies:
  ```bash
  pip install flask pandas openpyxl werkzeug
  ```

### Start the server
```bash
python app.py
```
- The app listens on `0.0.0.0:5000` in **debug** mode.
- Outputs are written to `OUTPUT_DIR` (default: `/tmp`).

> For containerized/serverless environments (e.g., Cloud Run), writing to `/tmp` is supported.

---

## 🔒 Validation & safety
- Only `.xlsx` files are accepted; other types are rejected with a message.
- Empty uploads or unreadable workbooks surface a friendly **flash** message in the UI.

---

## 🧩 Endpoints
- **GET /** — Renders the upload page.
- **POST /process** — Handles file upload, detects company & sheet, runs parser, saves Excel, and renders the preview panel with a **Download** button.
- **GET /download/<token>** — Streams the processed Excel with a clean filename.
- **POST /upload** — Simple persister (optional, not used by main flow); flashes a success message if used via tools.

---

## 🧰 UI details
- Drag‑and‑drop upload zone with **visual hover** state.
- **Light/Dark** theme toggle (persisted in `localStorage`).
- Gradient animated title; compact **badge** showing the pipeline and sheet used.
- Accessible buttons: keyboard focus outlines and ARIA‑friendly text.

---

## 🐞 Troubleshooting
- **“Please choose a .xlsx file.”** — No file was selected or an empty filename was posted.
- **“Invalid file type. Only .xlsx is allowed.”** — File extension not `.xlsx`.
- **“Could not open workbook: …”** — Corrupt file or incompatible format; try re‑saving as `.xlsx`.
- **“Failed to parse workbook for <carrier>: …”** — Parser couldn’t find expected headers/blocks;
  - Ensure **B2** contains the carrier name (e.g., `COSCO`, `HAPAG`).
  - For COSCO layouts, verify the presence of header keys like `Component / Repair Code / Material / Measurement` and the `Hour Rate` / `Material Price` blocks.
- **Download not found** — Tokens expire when files are cleaned or the server restarts; re‑process your file.

---

## 📚 Field reference (common)
- `Component`, `Component Description`, `Repair Code`, `Repair Description`, `Material`, `Length`, `Width`, `Measurement`, `Hours Calc`, `Material Calc`: metadata captured from the component block.
- **Hour Rate triplet**: `hour_rate_qty_from`, `hour_rate_qty_to`, `hour`.
- **Material Price triplet**: `material_price_qty_from`, `material_price_qty_to`, `material_price` (or `price` in the COSCO output schema).
- `shipping_company`: the cleaned company name detected from the workbook.

---

## 📦 Naming & tokens
- Saved filenames include a timestamp and parser mode, e.g., `{slug}__{mode}__YYYYMMDD_HHMMSS.xlsx`.
- The **download token** is the saved filename; the UI displays the token and a friendly download name.

---

## 📄 License
Internal tool — usage restricted to your organization unless stated otherwise.

---

## 🙋 FAQ
**Q: What if the COSCO parser is selected but fails?**  
A: The app automatically falls back to the HAPAG pipeline when appropriate; otherwise, you’ll see a friendly error with details.

**Q: Can I force a specific sheet?**  
A: Put an obvious sheet name (e.g., `HAPAQ`, `HAPAG`, `COSCO`) or ensure the company name appears in the sheet title.

**Q: Can I process multiple files?**  
A: The UI processes one file at a time. You can submit again for additional files.

**Q: Where does the processed file live?**  
A: It is saved under `OUTPUT_DIR` (default `/tmp`). Use the **Download** button to retrieve it.

