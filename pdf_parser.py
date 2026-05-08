import pdfplumber
import re

def _clean(s):
    if s is None:
        return ""
    return str(s).strip().lower().replace(" ", "").replace("º", "°")

import re

def _to_float(val):
    if val is None:
        return 0.0

    # Caso 0: pdfplumber estrae liste di pezzi → ricomponi
    if isinstance(val, list):
        # unisci tutto con spazio
        val = " ".join([str(v) for v in val if v])

    s = str(val).strip()

    # Rimuovi euro e spazi invisibili
    s = s.replace("€", "").replace("\u00A0", "").strip()

    # Caso 1: numeri spezzati tipo "60 15"
    if re.match(r"^\d+\s+\d+$", s):
        parts = s.split()
        s = parts[0] + "," + parts[1]

    # Caso 2: numeri spezzati con simboli strani
    if re.match(r"^\d+[^\d]\d+$", s):
        s = re.sub(r"[^\d]", ",", s)

    # Caso 3: numeri senza virgola ma troppo lunghi (es. 21605)
    if re.match(r"^\d{3,}$", s) and "," not in s and "." not in s:
        s = s[:-2] + "," + s[-2:]

    # Normalizza
    s = s.replace(".", "").replace(",", ".")

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
                if not table or len(table) < 3:
                    continue

                header = table[0]
                rows = table[1:]

                # 1) Trova colonna impegnativa
                idx_imp = None
                for col in range(len(header)):
                    sample = str(rows[0][col]).replace(" ", "")
                    if re.match(r"^\d{10,}$", sample):
                        idx_imp = col
                        break
                if idx_imp is None:
                    continue

                # 2) Trova colonna tariffa (prima colonna numerica dopo impegnativa)
                idx_tariffa = None
                for col in range(idx_imp + 1, len(header)):
                    sample = str(rows[0][col])
                    if re.search(r"\d", sample):
                        idx_tariffa = col
                        break
                if idx_tariffa is None:
                    continue

                # 3) Trova colonna ticket (ultima colonna numerica)
                idx_ticket = None
                for col in reversed(range(len(header))):
                    sample = str(rows[0][col])
                    if any(x in sample for x in ["38", "0", "-4", "4,40"]):
                        idx_ticket = col
                        break

                # 4) Leggi righe
                for row in rows:
                    imp = row[idx_imp]
                    if not imp:
                        continue
                    imp = str(imp).strip()

                    tariffa = _to_float(row[idx_tariffa])
                    ticket = _to_float(row[idx_ticket]) if idx_ticket is not None else 0.0

                    if imp not in results:
                        results[imp] = {"tariffa": 0.0, "ticket": 0.0}

                    results[imp]["tariffa"] += tariffa
                    results[imp]["ticket"] += ticket

    return results
