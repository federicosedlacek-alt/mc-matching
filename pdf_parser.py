import pdfplumber

def _to_float(val):
    if val is None:
        return 0.0
    s = str(val).replace("€", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except:
        return 0.0

def parse_pdf(file):
    results = {}

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                header = [str(h).strip().lower() for h in table[0]]

                # Trova indici dinamicamente
                try:
                    idx_imp = header.index("nº impegnativa")
                except:
                    try:
                        idx_imp = header.index("n° impegnativa")
                    except:
                        continue

                try:
                    idx_tariffa = header.index("tariffa")
                except:
                    continue

                try:
                    idx_ticket = header.index("imp. ticket")
                except:
                    idx_ticket = None

                # Leggi righe
                for row in table[1:]:
                    if not row or row[idx_imp] is None:
                        continue

                    imp = str(row[idx_imp]).strip()
                    if imp == "":
                        continue

                    tariffa = _to_float(row[idx_tariffa])
                    ticket = _to_float(row[idx_ticket]) if idx_ticket is not None else 0.0

                    if imp not in results:
                        results[imp] = {"tariffa": 0.0, "ticket": 0.0}

                    results[imp]["tariffa"] += tariffa
                    results[imp]["ticket"] += ticket

    return results
