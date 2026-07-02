import os
import re
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def normalize_name(value):
    if value is None:
        return ""

    value = str(value).strip().upper()
    value = value.split("#")[0].strip()
    value = re.sub(r"\s+", "", value)

    return value


def load_asset_mapping():
    file_path = os.getenv("ASSETS_XLSX")
    sheet_name = os.getenv("ASSETS_SHEET", "Organizados")

    if not file_path:
        raise ValueError("ASSETS_XLSX não configurado no .env")

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]

    df = df.rename(columns={
        "Colaborador(a)": "colaborador",
        "Nome do Dispositivo": "hostname_planilha",
        "ID EXPERWEB": "id_experweb",
        "Departamento / Time": "departamento_time",
        "Cargo": "cargo",
        "Score conferência": "score_conferencia",
    })

    required = ["hostname_planilha", "colaborador", "departamento_time"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente na planilha: {col}")

    df["hostname_key"] = df["hostname_planilha"].apply(normalize_name)

    for col in ["id_experweb", "cargo", "score_conferencia"]:
        if col not in df.columns:
            df[col] = None

    df = df[df["hostname_key"] != ""]

    # Se houver máquina duplicada na planilha, mantém a última ocorrência.
    # Assim você pode atualizar colaborador/departamento adicionando nova linha.
    df = df.drop_duplicates(subset=["hostname_key"], keep="last")

    return df[
        [
            "hostname_key",
            "colaborador",
            "hostname_planilha",
            "id_experweb",
            "departamento_time",
            "cargo",
            "score_conferencia",
        ]
    ]