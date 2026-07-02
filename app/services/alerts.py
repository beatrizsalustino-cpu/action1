from datetime import datetime
from app.database.database import get_conn
from app.services.google_chat import send_google_chat_message


def alert_already_sent(hostname_key: str, alert_type: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM alert_history
        WHERE hostname_key = ?
          AND alert_type = ?
          AND created_at >= datetime('now', '-6 hours')
    """, (hostname_key, alert_type))

    count = cur.fetchone()[0]
    conn.close()

    return count > 0


def save_alert(alert: dict, notification_sent: bool):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO alert_history (
            created_at,
            hostname,
            hostname_key,
            colaborador,
            departamento_time,
            alert_type,
            severity,
            message,
            health_score,
            notification_sent
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        alert.get("hostname"),
        alert.get("hostname_key"),
        alert.get("colaborador"),
        alert.get("departamento_time"),
        alert.get("alert_type"),
        alert.get("severity"),
        alert.get("message"),
        alert.get("health_score"),
        1 if notification_sent else 0,
    ))

    conn.commit()
    conn.close()


def format_google_chat_alert(alert: dict) -> str:
    icon = "🚨" if alert.get("severity") == "Crítico" else "⚠️"

    return f"""
{icon} *Alerta de Endpoint - {alert.get("severity")}*

*Máquina:* {alert.get("hostname")}
*Colaborador:* {alert.get("colaborador") or "Sem mapeamento"}
*Departamento / Time:* {alert.get("departamento_time") or "Sem mapeamento"}

*Tipo:* {alert.get("alert_type")}
*Detalhe:* {alert.get("message")}
*Health Score:* {alert.get("health_score")}
""".strip()


def process_alerts(alerts: list[dict]):
    sent = 0
    saved = 0
    skipped = 0

    for alert in alerts:
        if alert_already_sent(alert.get("hostname_key"), alert.get("alert_type")):
            skipped += 1
            continue

        message = format_google_chat_alert(alert)
        notification_sent = send_google_chat_message(message)

        save_alert(alert, notification_sent)

        saved += 1
        if notification_sent:
            sent += 1

    print(f"Alertas processados: salvos={saved}, enviados={sent}, ignorados_por_deduplicacao={skipped}")