import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "capacity.db")

st.set_page_config(page_title="Máquinas", page_icon="💻", layout="wide")
st.title("💻 Máquinas")


@st.cache_data(ttl=300)
def load_data():
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


df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

with st.sidebar:
    st.header("Filtros")

    status = st.multiselect(
        "Status",
        sorted(df["status"].dropna().unique()),
        default=sorted(df["status"].dropna().unique()),
    )

    health = st.multiselect(
        "Health Status",
        sorted(df["health_status"].dropna().unique()),
        default=sorted(df["health_status"].dropna().unique()),
    )

    departamento = st.multiselect(
        "Departamento / Time",
        sorted(df["departamento_time"].dropna().unique()),
    )

    busca = st.text_input("Buscar por máquina ou colaborador")

filtered = df.copy()

filtered = filtered[filtered["status"].isin(status)]
filtered = filtered[filtered["health_status"].isin(health)]

if departamento:
    filtered = filtered[filtered["departamento_time"].isin(departamento)]

if busca:
    busca = busca.lower()
    filtered = filtered[
        filtered["hostname"].fillna("").str.lower().str.contains(busca)
        | filtered["colaborador"].fillna("").str.lower().str.contains(busca)
    ]

st.metric("Máquinas encontradas", len(filtered))

st.dataframe(
    filtered[
        [
            "hostname",
            "colaborador",
            "departamento_time",
            "cargo",
            "status",
            "operating_system",
            "ram",
            "disk",
            "free_physical_memory_gb",
            "reboot_required",
            "health_score",
            "health_status",
        ]
    ].sort_values("health_score"),
    use_container_width=True,
)