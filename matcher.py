def compare(pdf_data, excel_data, tol=0.01):
    """
    pdf_data / excel_data:
        dict[imp] = {"tariffa": float, "ticket": float}

    Ritorna lista di dict per tabella finale.
    """
    errors = []

    all_keys = set(pdf_data.keys()) | set(excel_data.keys())

    for imp in sorted(all_keys):
        pdf = pdf_data.get(imp)
        excel = excel_data.get(imp)

        if pdf is None:
            errors.append({
                "Impegnativa": imp,
                "Excel Tariffa": excel["tariffa"] if excel else None,
                "PDF Tariffa": None,
                "Excel Ticket": excel["ticket"] if excel else None,
                "PDF Ticket": None,
                "Errore": "Presente solo in Excel"
            })
            continue

        if excel is None:
            errors.append({
                "Impegnativa": imp,
                "Excel Tariffa": None,
                "PDF Tariffa": pdf["tariffa"] if pdf else None,
                "Excel Ticket": None,
                "PDF Ticket": pdf["ticket"] if pdf else None,
                "Errore": "Presente solo nel PDF"
            })
            continue

        tariffa_ok = abs(pdf["tariffa"] - excel["tariffa"]) <= tol
        ticket_ok = abs(pdf["ticket"] - excel["ticket"]) <= tol

        if tariffa_ok and ticket_ok:
            continue

        err_parts = []
        if not tariffa_ok:
            err_parts.append("Tariffa diversa")
        if not ticket_ok:
            err_parts.append("Ticket diverso")

        errors.append({
            "Impegnativa": imp,
            "Excel Tariffa": excel["tariffa"],
            "PDF Tariffa": pdf["tariffa"],
            "Excel Ticket": excel["ticket"],
            "PDF Ticket": pdf["ticket"],
            "Errore": ", ".join(err_parts)
        })

    return errors
