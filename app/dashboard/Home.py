import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import sqlite3
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

from app.collector import collect

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "capacity.db")


@st.cache_data(ttl=300)
def load_latest_data():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT *
    FROM endpoint_snapshots
    WHERE collected_at = (
        SELECT MAX(collected_at)
        FROM endpoint_snapshots
    )
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def main():
    st.set_page_config(
        page_title="Expermed Endpoint Health",
        page_icon="💻",
        layout="wide",
    )

    st.title("💻 Expermed Endpoint Health")
    st.caption("Visão geral de capacidade, saúde e inventário dos endpoints.")

    st.sidebar.subheader("Atualização")

    if st.sidebar.button("🔄 Atualizar dados agora"):
        with st.spinner("Coletando dados do Action1 e atualizando planilha..."):
            collect()
            st.cache_data.clear()
        st.success("Dados atualizados com sucesso!")
        st.rerun()

    df = load_latest_data()

    if df.empty:
        st.warning("Ainda não há dados coletados.")
        st.stop()

    total = len(df)
    online = len(df[df["status"].str.lower() == "connected"])
    offline = total - online
    criticos = len(df[df["health_status"] == "Crítico"])
    atencao = len(df[df["health_status"] == "Atenção"])

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total de máquinas", total)
    col2.metric("Online", online)
    col3.metric("Offline", offline)
    col4.metric("Críticas", criticos)
    col5.metric("Em atenção", atencao)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Saúde dos endpoints")
        health_chart = df["health_status"].value_counts().reset_index()
        health_chart.columns = ["Status", "Quantidade"]

        fig = px.pie(
            health_chart,
            names="Status",
            values="Quantidade",
            title="Distribuição por Health Score",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Status de conexão")
        status_chart = df["status"].fillna("Desconhecido").value_counts().reset_index()
        status_chart.columns = ["Status", "Quantidade"]

        fig = px.bar(
            status_chart,
            x="Status",
            y="Quantidade",
            title="Online / Offline",
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Máquinas mais críticas")

    critical_df = df.sort_values("health_score").head(15)

    st.dataframe(
        critical_df[
            [
                "hostname",
                "colaborador",
                "departamento_time",
                "status",
                "ram",
                "free_physical_memory_gb",
                "disk",
                "reboot_required",
                "health_score",
                "health_status",
            ]
        ],
        use_container_width=True,
    )


if __name__ == "__main__":
    main()