def calculate_health(row):
    score = 100
    reasons = []

    status = str(row.get("Status", "")).lower()
    reboot = str(row.get("Reboot Required", "")).lower()
    ram = str(row.get("RAM", "")).lower()
    free_mem = row.get("free_physical_memory_gb")

    if status != "connected":
        score -= 30
        reasons.append("Endpoint desconectado")

    if reboot == "yes":
        score -= 10
        reasons.append("Reboot pendente")

    if "4gb" in ram:
        score -= 25
        reasons.append("RAM instalada muito baixa")
    elif "8gb" in ram:
        score -= 10
        reasons.append("RAM instalada no limite")

    if free_mem is not None:
        if free_mem < 1:
            score -= 25
            reasons.append("Memória livre crítica")
        elif free_mem < 2:
            score -= 15
            reasons.append("Memória livre baixa")

    score = max(score, 0)

    if score >= 85:
        health_status = "Saudável"
    elif score >= 70:
        health_status = "Atenção"
    else:
        health_status = "Crítico"

    return score, health_status, ", ".join(reasons)