import pdfplumber

def _to_float(val):
    if val is None:
        return 0.0
    s = str(val).replace("€", "").replace(".", "").replace(",", ".").strip()
    if s == "":
        return 0.0
    try:
        return float(s)
    except:
        return 0.0

def parse_pdf(file):
    """
    Ritorna: dict[impegnativa] = {"tariffa": float, "ticket": float}
    """
    results = {}

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                # Trova header per capire gli indici
                header = table[0]
                header_str = " ".join([str(h).lower() for h in header if h])

                if "impegnativa" in header_str and "tariffa" in header_str:
                    # Trova indici colonne
                    idx_imp = None
                    idx_tariffa = None
                    idx_ticket = None

                    for i, h in enumerate(header):
                        hs = str(h).lower()
                        if "impegnativa" in hs:
                            idx_imp = i
                        if "tariffa" in hs:
                            idx_tariffa = i
                        if "ticket" in hs:
                            idx_ticket = i

                    if idx_imp is None or idx_tariffa is None or idx_ticket is None:
                        continue

                    # Scorri righe dati
                    for row in table[1:]:
                        if not row:
                            continue
                        imp = row[idx_imp]
                        if imp is None:
                            continue
                        imp = str(imp).strip()
                        if imp == "" or "impegnativa" in imp.lower():
                            continue

                        tariffa = _to_float(row[idx_tariffa])
                        ticket = _to_float(row[idx_ticket])

                        # Se la stessa impegnativa appare più volte, sommiamo
                        if imp not in results:
                            results[imp] = {"tariffa": 0.0, "ticket": 0.0}
                        results[imp]["tariffa"] += tariffa
                        results[imp]["ticket"] += ticket

    return results
