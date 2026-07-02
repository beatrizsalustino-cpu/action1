import pandas as pd


ALERT_RULES = {
    "offline": {
        "enabled": True,
        "severity": "Crítico",
    },
    "reboot_required": {
        "enabled": True,
        "severity": "Atenção",
    },
    "free_memory_critical": {
        "enabled": True,
        "severity": "Crítico",
        "threshold_gb": 1,
    },
    "free_memory_warning": {
        "enabled": True,
        "severity": "Atenção",
        "threshold_gb": 2,
    },
    "health_score_critical": {
        "enabled": True,
        "severity": "Crítico",
        "threshold": 70,
    },
}


def build_alerts(df: pd.DataFrame) -> list[dict]:
    alerts = []

    for _, row in df.iterrows():
        hostname = row.get("hostname")
        hostname_key = row.get("hostname_key")
        colaborador = row.get("colaborador")
        departamento = row.get("departamento_time")
        score = row.get("health_score")

        if ALERT_RULES["offline"]["enabled"] and row.get("status") != "Connected":
            alerts.append({
                "hostname": hostname,
                "hostname_key": hostname_key,
                "colaborador": colaborador,
                "departamento_time": departamento,
                "alert_type": "Endpoint offline",
                "severity": ALERT_RULES["offline"]["severity"],
                "message": f"A máquina {hostname} está offline ou desconectada. Status atual: {row.get('status')}.",
                "health_score": score,
            })

        if ALERT_RULES["reboot_required"]["enabled"] and row.get("reboot_required") == "Yes":
            alerts.append({
                "hostname": hostname,
                "hostname_key": hostname_key,
                "colaborador": colaborador,
                "departamento_time": departamento,
                "alert_type": "Reboot pendente",
                "severity": ALERT_RULES["reboot_required"]["severity"],
                "message": f"A máquina {hostname} precisa ser reiniciada.",
                "health_score": score,
            })

        free_mem = row.get("free_physical_memory_gb")

        if pd.notna(free_mem):
            if ALERT_RULES["free_memory_critical"]["enabled"] and free_mem < ALERT_RULES["free_memory_critical"]["threshold_gb"]:
                alerts.append({
                    "hostname": hostname,
                    "hostname_key": hostname_key,
                    "colaborador": colaborador,
                    "departamento_time": departamento,
                    "alert_type": "Memória livre crítica",
                    "severity": ALERT_RULES["free_memory_critical"]["severity"],
                    "message": f"A máquina {hostname} está com apenas {free_mem:.2f} GB de memória física livre.",
                    "health_score": score,
                })

            elif ALERT_RULES["free_memory_warning"]["enabled"] and free_mem < ALERT_RULES["free_memory_warning"]["threshold_gb"]:
                alerts.append({
                    "hostname": hostname,
                    "hostname_key": hostname_key,
                    "colaborador": colaborador,
                    "departamento_time": departamento,
                    "alert_type": "Memória livre baixa",
                    "severity": ALERT_RULES["free_memory_warning"]["severity"],
                    "message": f"A máquina {hostname} está com {free_mem:.2f} GB de memória física livre.",
                    "health_score": score,
                })

        if ALERT_RULES["health_score_critical"]["enabled"] and score is not None and score < ALERT_RULES["health_score_critical"]["threshold"]:
            alerts.append({
                "hostname": hostname,
                "hostname_key": hostname_key,
                "colaborador": colaborador,
                "departamento_time": departamento,
                "alert_type": "Health Score crítico",
                "severity": ALERT_RULES["health_score_critical"]["severity"],
                "message": f"A máquina {hostname} está com Health Score {score}.",
                "health_score": score,
            })

    return alerts