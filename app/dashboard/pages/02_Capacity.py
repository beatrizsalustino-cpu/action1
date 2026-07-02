import os
import re
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "capacity.db")

st.set_page_config(page_title="Capacity", page_icon="📊", layout="wide")
st.title("📊 Capacity")


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

col1, col2, col3, col4 = st.columns(4)

col1.metric("RAM média", f"{df['ram_gb'].mean():.1f} GB")
col2.metric("Disco médio", f"{df['disk_gb'].mean():.1f} GB")
col3.metric("Máquinas com 8GB ou menos", len(df[df["ram_gb"] <= 8]))
col4.metric("Máquinas críticas", len(df[df["health_status"] == "Crítico"]))

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Distribuição de RAM")
    ram_chart = df["ram"].fillna("Desconhecido").value_counts().reset_index()
    ram_chart.columns = ["RAM", "Quantidade"]

    fig = px.bar(
        ram_chart,
        x="RAM",
        y="Quantidade",
        title="Máquinas por memória RAM",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Distribuição de Disco")
    disk_chart = df["disk"].fillna("Desconhecido").value_counts().reset_index()
    disk_chart.columns = ["Disco", "Quantidade"]

    fig = px.bar(
        disk_chart,
        x="Disco",
        y="Quantidade",
        title="Máquinas por capacidade de disco",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Máquinas com menor memória livre")

memory_df = df.sort_values("free_physical_memory_gb", na_position="last").head(20)

st.dataframe(
    memory_df[
        [
            "hostname",
            "colaborador",
            "departamento_time",
            "ram",
            "free_physical_memory_gb",
            "number_of_processes",
            "health_score",
            "health_status",
        ]
    ],
    use_container_width=True,
)

st.subheader("Modelos de máquinas")

model_chart = df["system_model"].fillna("Desconhecido").value_counts().reset_index()
model_chart.columns = ["Modelo", "Quantidade"]

fig = px.bar(
    model_chart.head(15),
    x="Modelo",
    y="Quantidade",
    title="Top modelos de hardware",
)

st.plotly_chart(fig, use_container_width=True)