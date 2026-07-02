import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "capacity.db")

st.set_page_config(page_title="Tendências", page_icon="📈", layout="wide")
st.title("📈 Tendências de Capacidade")


@st.cache_data(ttl=300)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT collected_at, hostname, colaborador, departamento_time,
               free_physical_memory_gb, health_score, health_status
        FROM endpoint_snapshots
    """, conn)
    conn.close()

    df["collected_at"] = pd.to_datetime(df["collected_at"])
    return df


df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

machine = st.selectbox(
    "Selecione uma máquina",
    sorted(df["hostname"].dropna().unique())
)

machine_df = df[df["hostname"] == machine].sort_values("collected_at")

st.subheader(machine)

fig = px.line(
    machine_df,
    x="collected_at",
    y="free_physical_memory_gb",
    title="Memória física livre ao longo do tempo",
    markers=True,
)
st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    machine_df,
    x="collected_at",
    y="health_score",
    title="Health Score ao longo do tempo",
    markers=True,
)
st.plotly_chart(fig, use_container_width=True)