import os
import re
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "capacity.db")

st.set_page_config(page_title="Planejamento", page_icon="🧠", layout="wide")
st.title("🧠 Planejamento de Capacidade")


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


def extract_gb(value):
    if pd.isna(value):
        return None

    value = str(value).lower().replace(",", ".")
    match = re.search(r"(\d+(\.\d+)?)\s*gb", value)

    if match:
        return float(match.group(1))

    return None


df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

df["ram_gb"] = df["ram"].apply(extract_gb)
df["disk_gb"] = df["disk"].apply(extract_gb)

below_16 = df[df["ram_gb"] < 16]
low_free_memory = df[df["free_physical_memory_gb"] < 2]
critical = df[df["health_status"] == "Crítico"]

col1, col2, col3 = st.columns(3)

col1.metric("Máquinas abaixo de 16 GB RAM", len(below_16))
col2.metric("Memória livre < 2 GB", len(low_free_memory))
col3.metric("Máquinas críticas", len(critical))

st.divider()

st.subheader("Recomendação de upgrade de RAM")

upgrade_df = df[
    (df["ram_gb"] < 16) | (df["free_physical_memory_gb"] < 2)
].sort_values(["ram_gb", "free_physical_memory_gb"], na_position="last")

st.dataframe(
    upgrade_df[
        [
            "hostname",
            "colaborador",
            "departamento_time",
            "ram",
            "free_physical_memory_gb",
            "system_model",
            "system_manufacturer",
            "health_score",
            "health_status",
        ]
    ],
    use_container_width=True,
)

st.subheader("Distribuição de RAM")

ram_chart = df["ram"].fillna("Desconhecido").value_counts().reset_index()
ram_chart.columns = ["RAM", "Quantidade"]

fig = px.bar(
    ram_chart,
    x="RAM",
    y="Quantidade",
    title="Máquinas por quantidade de RAM",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Distribuição por fabricante")

manufacturer_chart = df["system_manufacturer"].fillna("Desconhecido").value_counts().reset_index()
manufacturer_chart.columns = ["Fabricante", "Quantidade"]

fig = px.bar(
    manufacturer_chart,
    x="Fabricante",
    y="Quantidade",
    title="Máquinas por fabricante",
)
st.plotly_chart(fig, use_container_width=True)