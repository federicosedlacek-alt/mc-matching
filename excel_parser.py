import openpyxl

def parse_excel(file):
    """
    Ritorna: dict[impegnativa] = {"tariffa": float, "ticket": float}
    Colonna A = impegnativa
    Colonna C = tariffa
    Colonna H = importo ticket
    """
    wb = openpyxl.load_workbook(file, data_only=True)
    ws = wb.active

    results = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue

        imp = str(row[0]).strip()
        if imp == "":
            continue

        tariffa = float(row[2]) if row[2] is not None else 0.0
        ticket = float(row[7]) if len(row) > 7 and row[7] is not None else 0.0

        if imp not in results:
            results[imp] = {"tariffa": 0.0, "ticket": 0.0}

        # Se la stessa impegnativa è su più righe, sommiamo
        results[imp]["tariffa"] += tariffa
        results[imp]["ticket"] += ticket

    return results
