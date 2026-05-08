import openpyxl

def _safe_float(val):
    if val is None:
        return 0.0
    s = str(val).strip()
    if s == "":
        return 0.0
    s = s.replace("€", "").replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

def parse_excel(file):
    wb = openpyxl.load_workbook(file, data_only=True)
    ws = wb.active

    results = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        imp = row[0]
        if imp is None:
            continue

        imp = str(imp).strip()
        if imp == "":
            continue

        tariffa = _safe_float(row[2])  # COLONNA C
        ticket = _safe_float(row[7]) if len(row) > 7 else 0.0  # COLONNA H

        if imp not in results:
            results[imp] = {"tariffa": 0.0, "ticket": 0.0}

        results[imp]["tariffa"] += tariffa
        results[imp]["ticket"] += ticket

    return results
