import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Merge Unique Files", layout="wide")

st.title("Combinar archivos únicos")

uploaded = st.file_uploader(
    "Sube uno o más archivos CSV / XLSX",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded:
    dfs = []
    for file in uploaded:
        # Leer según extensión
        name = file.name
        ext = os.path.splitext(name)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(file, dtype=str)
        else:
            df = pd.read_excel(file, dtype=str)

        # Quitar columna con el basename del archivo o Source.Name
        basename = os.path.splitext(name)[0]
        drop = [c for c in (basename, "Source.Name") if c in df.columns]
        if drop:
            df = df.drop(columns=drop)

        dfs.append(df)

    # Combinar y eliminar duplicados
    combined = pd.concat(dfs, ignore_index=True, sort=False)
    combined["__key__"] = combined.astype(str).agg("||".join, axis=1)
    combined = combined.drop_duplicates(subset="__key__").drop(columns="__key__")
    combined.reset_index(drop=True, inplace=True)

    st.subheader(f"Registros únicos: {len(combined)}")
    st.dataframe(combined)

    # Botón de descarga
    csv = combined.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 Descargar merge_unique.csv",
        data=csv,
        file_name="merge_unique.csv",
        mime="text/csv"
    )
