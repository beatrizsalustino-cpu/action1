import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "capacity.db")

st.set_page_config(page_title="Ranking Crítico", page_icon="🏆", layout="wide")
st.title("🏆 Ranking das Máquinas Mais Críticas")


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

ranking = df.sort_values("health_score").head(30)

st.dataframe(
    ranking[
        [
            "hostname",
            "colaborador",
            "departamento_time",
            "status",
            "ram",
            "free_physical_memory_gb",
            "reboot_required",
            "health_score",
            "health_status",
            "health_reasons",
        ]
    ],
    use_container_width=True,
)