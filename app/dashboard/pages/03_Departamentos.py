import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "capacity.db")

st.set_page_config(page_title="Departamentos", page_icon="🏢", layout="wide")
st.title("🏢 Departamentos / Times")


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

df["departamento_time"] = df["departamento_time"].fillna("Sem mapeamento")

summary = df.groupby("departamento_time").agg(
    total=("hostname", "count"),
    criticas=("health_status", lambda x: (x == "Crítico").sum()),
    atencao=("health_status", lambda x: (x == "Atenção").sum()),
    saudaveis=("health_status", lambda x: (x == "Saudável").sum()),
    score_medio=("health_score", "mean"),
).reset_index()

summary["score_medio"] = summary["score_medio"].round(1)

st.subheader("Resumo por departamento")

st.dataframe(
    summary.sort_values(["criticas", "atencao"], ascending=False),
    use_container_width=True,
)

col_a, col_b = st.columns(2)

with col_a:
    fig = px.bar(
        summary.sort_values("total", ascending=False),
        x="departamento_time",
        y="total",
        title="Máquinas por departamento",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    fig = px.bar(
        summary.sort_values("score_medio"),
        x="departamento_time",
        y="score_medio",
        title="Health Score médio por departamento",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Máquinas críticas por departamento")

criticas = df[df["health_status"] == "Crítico"]

st.dataframe(
    criticas[
        [
            "departamento_time",
            "hostname",
            "colaborador",
            "ram",
            "free_physical_memory_gb",
            "status",
            "reboot_required",
            "health_score",
        ]
    ].sort_values(["departamento_time", "health_score"]),
    use_container_width=True,
)