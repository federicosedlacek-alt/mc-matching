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
                if not table or len(table) < 2:
                    continue

                header = [_clean(h) for h in table[0]]

                # Trova indice impegnativa
                idx_imp = None
                for i, h in enumerate(header):
                    if "impegnativa" in h:
                        idx_imp = i
                        break
                if idx_imp is None:
                    continue

                # Trova indice tariffa
                idx_tariffa = None
                for i, h in enumerate(header):
                    if "tariffa" in h:
                        idx_tariffa = i
                        break
                if idx_tariffa is None:
                    continue

                # Trova indice ticket
                idx_ticket = None
                for i, h in enumerate(header):
                    if "ticket" in h:
                        idx_ticket = i
                        break

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
