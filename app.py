import streamlit as st
import pandas as pd

from pdf_parser import parse_pdf
from excel_parser import parse_excel
from matcher import compare

st.set_page_config(page_title="Matching PDF ↔ Excel", layout="wide")

st.title("🔍 Matching impegnative PDF ↔ Excel")

st.markdown("""
Carica:
- un file **Excel** (colonna A = impegnativa, C = tariffa, H = ticket)
- uno o più **PDF** con l'elenco dettagliato prestazioni

Il sistema confronterà:
- impegnativa
- tariffa
- importo ticket

e ti mostrerà tutte le discrepanze.
""")

excel_file = st.file_uploader("Carica Excel (.xlsx)", type=["xlsx"])
pdf_files = st.file_uploader("Carica uno o più PDF", type=["pdf"], accept_multiple_files=True)

if excel_file and pdf_files:
    if st.button("Esegui matching"):
        with st.spinner("Elaborazione in corso..."):
            excel_data = parse_excel(excel_file)

            pdf_data = {}
            for pdf in pdf_files:
                parsed = parse_pdf(pdf)
                # merge: se stessa impegnativa su più pdf, sommiamo
                for k, v in parsed.items():
                    if k not in pdf_data:
                        pdf_data[k] = {"tariffa": 0.0, "ticket": 0.0}
                    pdf_data[k]["tariffa"] += v["tariffa"]
                    pdf_data[k]["ticket"] += v["ticket"]

            errors = compare(pdf_data, excel_data)

        if not errors:
            st.success("✅ Nessun errore trovato: tutti i match sono coerenti.")
        else:
            st.error(f"❌ Trovati {len(errors)} errori di matching.")
            df = pd.DataFrame(errors)
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Scarica errori in CSV",
                csv,
                "errori_matching.csv",
                "text/csv"
            )
else:
    st.info("Carica sia un Excel che almeno un PDF per procedere.")
