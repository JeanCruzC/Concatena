import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Merge Unique Files", layout="wide")
st.title("Combinar archivos únicos")

# Checkbox para incluir o no la columna de origen
include_source = st.checkbox("Incluir columna 'source_file' (origen de cada registro)", value=True)

uploaded = st.file_uploader(
    "Sube uno o más archivos CSV / XLSX",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded:
    dfs = []
    for file in uploaded:
        name = file.name
        ext  = os.path.splitext(name)[1].lower()

        # 1) Lectura
        if ext == ".csv":
            df = pd.read_csv(file, dtype=str)
        else:
            df = pd.read_excel(file, dtype=str)

        # 2) Si se pidió, añadimos source_file
        if include_source:
            basename = os.path.splitext(name)[0]
            df["source_file"] = basename

        # 3) Limpiar columna Source.Name si existe
        if "Source.Name" in df.columns:
            df = df.drop(columns="Source.Name")

        dfs.append(df)

    # 4) Concatenar todos los DataFrames
    combined = pd.concat(dfs, ignore_index=True, sort=False)

    # 5) Detección de duplicados solo sobre columnas de datos
    cols_to_key = [c for c in combined.columns if c != "source_file"]
    combined["__key__"] = combined[cols_to_key].astype(str).agg("||".join, axis=1)
    combined = combined.drop_duplicates(subset="__key__").drop(columns="__key__")
    combined.reset_index(drop=True, inplace=True)

    st.subheader(f"Registros únicos: {len(combined)}")
    st.dataframe(combined)

    # 6) Botón de descarga
    csv = combined.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 Descargar CSV combinado",
        data=csv,
        file_name="merged_unique.csv",
        mime="text/csv"
    )
