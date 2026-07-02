from datetime import datetime
import pandas as pd

from app.api.action1 import get_all_report_data
from app.services.mapper import load_asset_mapping, normalize_name
from app.database.database import get_conn, init_db
from app.services.alert_rules import build_alerts
from app.services.alerts import process_alerts
from app.services.health import calculate_health

REPORTS = {
    "managed": "managed_endpoints_1635942317188",
    "hardware": "hardware_summary_1635380496058",
    "memory": "process_memory_stats_1635435983998",
}


def rows_to_df(rows):
    data = []

    for row in rows:
        fields = row.get("fields", {})
        fields["last_refresh"] = row.get("last_refresh")
        fields["response_type"] = row.get("response_type")
        data.append(fields)

    return pd.DataFrame(data)


def parse_float(value):
    if value is None:
        return None

    value = str(value).replace(",", ".").strip()

    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value):
    try:
        return int(value)
    except Exception:
        return None


def collect():
    init_db()

    collected_at = datetime.now().isoformat(timespec="seconds")

    print("Coletando Managed Endpoints...")
    managed_df = rows_to_df(get_all_report_data(REPORTS["managed"]))

    print("Coletando Hardware Summary...")
    hardware_df = rows_to_df(get_all_report_data(REPORTS["hardware"]))

    print("Coletando Process/Memory Stats...")
    memory_df = rows_to_df(get_all_report_data(REPORTS["memory"]))

    print("Carregando planilha de mapeamento...")
    mapping_df = load_asset_mapping()

    if managed_df.empty:
        print("Nenhum dado retornado em Managed Endpoints.")
        return

    managed_df["hostname_key"] = managed_df["Endpoint Name"].apply(normalize_name)
    managed_df = managed_df.sort_values("_Last Seen_sortby", ascending=False, na_position="last")
    managed_df = managed_df.drop_duplicates(subset=["hostname_key"], keep="first")

    if not hardware_df.empty:
        hardware_df["hostname_key"] = hardware_df["Endpoint Name"].apply(normalize_name)
        hardware_df = hardware_df.drop_duplicates(subset=["hostname_key"], keep="first")
    else:
        hardware_df = pd.DataFrame(columns=["hostname_key"])

    if not memory_df.empty:
        memory_df["hostname_key"] = memory_df["Endpoint Name"].apply(normalize_name)
        memory_df = memory_df.drop_duplicates(subset=["hostname_key"], keep="first")
    else:
        memory_df = pd.DataFrame(columns=["hostname_key"])

    df = managed_df.merge(
        hardware_df,
        on="hostname_key",
        how="left",
        suffixes=("", "_hardware"),
    )

    memory_columns = [
        "hostname_key",
        "Free Physical Memory (Gb)",
        "Number Of Processes",
    ]

    for col in memory_columns:
        if col not in memory_df.columns:
            memory_df[col] = None

    df = df.merge(
        memory_df[memory_columns],
        on="hostname_key",
        how="left",
    )

    df = df.merge(
        mapping_df,
        on="hostname_key",
        how="left",
    )

    records = []

    for _, row in df.iterrows():
        free_mem = parse_float(row.get("Free Physical Memory (Gb)"))

        score, health_status, health_reasons = calculate_health({
            **row.to_dict(),
            "free_physical_memory_gb": free_mem,
        })

        records.append({
            "collected_at": collected_at,
            "hostname": row.get("Endpoint Name"),
            "hostname_key": row.get("hostname_key"),
            "colaborador": row.get("colaborador"),
            "health_reasons": health_reasons,
            "departamento_time": row.get("departamento_time"),
            "cargo": row.get("cargo"),
            "id_experweb": row.get("id_experweb"),
            "status": row.get("Status"),
            "last_seen": row.get("Last Seen"),
            "operating_system": row.get("Operating System"),
            "cpu_name": row.get("CPU Name"),
            "cpu_size": row.get("CPU Size"),
            "ram": row.get("RAM"),
            "disk": row.get("Disk"),
            "system_model": row.get("System Model"),
            "system_manufacturer": row.get("System Manufacturer"),
            "action1_user": row.get("User"),
            "reboot_required": row.get("Reboot Required"),
            "free_physical_memory_gb": free_mem,
            "number_of_processes": parse_int(row.get("Number Of Processes")),
            "health_score": score,
            "health_status": health_status,
        })

    final_df = pd.DataFrame(records)

    conn = get_conn()
    final_df.to_sql(
        "endpoint_snapshots",
        conn,
        if_exists="append",
        index=False,
    )
    conn.close()

    print(f"Coleta concluída: {len(final_df)} máquinas salvas em {collected_at}")

    alerts = build_alerts(final_df)
    process_alerts(alerts)


if __name__ == "__main__":
    collect()