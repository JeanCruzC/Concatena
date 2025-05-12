import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Merge Unique Files", layout="wide")
st.title("Combinar archivos únicos con origen")

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
        # 1) Leer como texto
        if ext == ".csv":
            df = pd.read_csv(file, dtype=str)
        else:
            df = pd.read_excel(file, dtype=str)
        # 2) Añadir columna con el nombre base del archivo
        basename = os.path.splitext(name)[0]
        df["source_file"] = basename
        # 3) Quitar la columna Source.Name si existiera
        if "Source.Name" in df.columns:
            df = df.drop(columns="Source.Name")
        dfs.append(df)

    # 4) Concatenar todos los DataFrames (outer join de columnas)
    combined = pd.concat(dfs, ignore_index=True, sort=False)

    # 5) Generar llave única solo con las columnas de datos (sin source_file)
    data_cols = [c for c in combined.columns if c != "source_file"]
    combined["__key__"] = combined[data_cols].astype(str).agg("||".join, axis=1)

    # 6) Eliminar duplicados basados en los datos y conservar la primera ocurrencia
    combined = combined.drop_duplicates(subset="__key__").drop(columns="__key__")

    combined.reset_index(drop=True, inplace=True)

    st.subheader(f"Registros únicos: {len(combined)}")
    st.dataframe(combined)

    # 7) Botón de descarga
    csv = combined.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 Descargar merged_with_source.csv",
        data=csv,
        file_name="merged_with_source.csv",
        mime="text/csv"
    )
