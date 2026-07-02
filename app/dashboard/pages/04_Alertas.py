import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "capacity.db")

st.set_page_config(page_title="Alertas", page_icon="🚨", layout="wide")
st.title("🚨 Alertas")


@st.cache_data(ttl=300)
def load_latest_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT *
        FROM endpoint_snapshots
        WHERE collected_at = (
            SELECT MAX(collected_at)
            FROM endpoint_snapshots
        )
    """, conn)
    conn.close()
    return df


df = load_latest_data()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

alerts = []

for _, row in df.iterrows():
    hostname = row.get("hostname")
    colaborador = row.get("colaborador")
    departamento = row.get("departamento_time")
    score = row.get("health_score")

    if row.get("status") != "Connected":
        alerts.append({
            "severidade": "Crítico",
            "tipo": "Endpoint offline",
            "hostname": hostname,
            "colaborador": colaborador,
            "departamento_time": departamento,
            "detalhe": f"Status atual: {row.get('status')}",
            "health_score": score,
        })

    if row.get("reboot_required") == "Yes":
        alerts.append({
            "severidade": "Atenção",
            "tipo": "Reboot pendente",
            "hostname": hostname,
            "colaborador": colaborador,
            "departamento_time": departamento,
            "detalhe": "A máquina precisa ser reiniciada.",
            "health_score": score,
        })

    free_mem = row.get("free_physical_memory_gb")

    if pd.notna(free_mem) and free_mem < 1:
        alerts.append({
            "severidade": "Crítico",
            "tipo": "Memória livre crítica",
            "hostname": hostname,
            "colaborador": colaborador,
            "departamento_time": departamento,
            "detalhe": f"Memória livre: {free_mem} GB",
            "health_score": score,
        })
    elif pd.notna(free_mem) and free_mem < 2:
        alerts.append({
            "severidade": "Atenção",
            "tipo": "Memória livre baixa",
            "hostname": hostname,
            "colaborador": colaborador,
            "departamento_time": departamento,
            "detalhe": f"Memória livre: {free_mem} GB",
            "health_score": score,
        })

    if row.get("health_status") == "Crítico":
        alerts.append({
            "severidade": "Crítico",
            "tipo": "Health Score crítico",
            "hostname": hostname,
            "colaborador": colaborador,
            "departamento_time": departamento,
            "detalhe": f"Health Score: {score}",
            "health_score": score,
        })

alerts_df = pd.DataFrame(alerts)

if alerts_df.empty:
    st.success("Nenhum alerta crítico encontrado no último snapshot.")
    st.stop()

col1, col2, col3 = st.columns(3)

col1.metric("Total de alertas", len(alerts_df))
col2.metric("Críticos", len(alerts_df[alerts_df["severidade"] == "Crítico"]))
col3.metric("Atenção", len(alerts_df[alerts_df["severidade"] == "Atenção"]))

st.dataframe(
    alerts_df.sort_values(["severidade", "health_score"], ascending=[True, True]),
    use_container_width=True,
)