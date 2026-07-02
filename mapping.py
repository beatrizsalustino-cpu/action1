import os
import re
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def normalize_name(value):
    if value is None:
        return ""

    value = str(value).strip().upper()
    value = value.split("#")[0].strip()  # EXPERMED58 #292 -> EXPERMED58
    value = re.sub(r"\s+", "", value)

    return value


def load_asset_mapping():
    file_path = os.getenv("ASSETS_XLSX")
    sheet_name = os.getenv("ASSETS_SHEET", "Organizados")

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]

    df = df.rename(columns={
        "Colaborador(a)": "colaborador",
        "Nome do Dispositivo": "hostname",
        "ID EXPERWEB": "id_experweb",
        "Departamento / Time": "departamento_time",
        "Cargo": "cargo",
    })

    df["hostname_key"] = df["hostname"].apply(normalize_name)

    return df[[
        "hostname_key",
        "colaborador",
        "hostname",
        "id_experweb",
        "departamento_time",
        "cargo",
    ]]