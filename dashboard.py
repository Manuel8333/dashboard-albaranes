
import io
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Panel Interactivo de Albaranes", layout="wide")

@st.cache_data
def cargar_datos():
    file_id = "1ojkVcMlXHcO_A_oCvm-TcufKmapsoEto"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    return pd.read_excel(io.BytesIO(response.content), sheet_name="DATOS")

df = cargar_datos()
df.columns = df.columns.str.strip()

def limpiar_moneda(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace('.', '').replace(',', '.').replace('€', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

# Obtener todas las columnas que parezcan numéricas
columnas_numericas = []
for c in df.columns:
    if c.lower() not in ['mes', 'semana', 'id', 'año', 'codigo', 'código']:
        # Probar si la columna se puede convertir parcialmente a número
        muestra = df[c].dropna().head(5)
        convertibles = 0
        for val in muestra:
            if limpiar_moneda(val) > 0:
                convertibles += 1
        if convertibles > 0:
            columnas_numericas.append(c)

# Asignar automáticamente según orden o nombres
col_total = next((c for c in df.columns if 'total' in c.lower() or 'facturado' in c.lower()), columnas_numericas[0] if columnas_numericas else None)
col_cocina = next((c for c in df.columns if 'cocina' in c.lower()), columnas_numericas[1] if len(columnas_numericas) > 1 else None)
col_sala = next((c for c in df.columns if 'sala' in c.lower()), columnas_numericas[2] if len(columnas_numericas) > 2 else None)
col_eventos = next((c for c in df.columns if 'evento' in c.lower() or 'otros' in c.lower()), columnas_numericas[3] if len(columnas_numericas) > 3 else None)

for col in [col_total, col_cocina, col_sala, col_eventos]:
    if col:
        df[col] = df[col].apply(limpiar_moneda)

st.title("📊 Panel Interactivo de Albaranes")
st.markdown("Análisis avanzado de facturación.")
st.markdown("---")

total_registros = len(df)
val_total = df[col_total].sum() if col_total else 0
val_cocina = df[col_cocina].sum() if col_cocina else 0
val_sala = df[col_sala].sum() if col_sala else 0
val_eventos = df[col_eventos].sum() if col_eventos else 0

st.markdown(f"### Resumen Económico ({total_registros} registros)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Facturado", f"{val_total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c2.metric("Gasto Cocina", f"{val_cocina:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c3.metric("Gasto Sala", f"{val_sala:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c4.metric("Eventos y Otros", f"{val_eventos:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### Distribución por Área o Semanas")
    col_semana = next((c for c in df.columns if 'semana' in c.lower()), None)
    col_area = next((c for c in df.columns if 'area' in c.lower() or 'área' in c.lower()), None)
    if col_semana and col_total and col_area:
        df_g = df.groupby([col_semana, col_area], as_index=False)[col_total].sum()
        fig1 = px.bar(df_g, x=col_semana, y=col_total, color=col_area, barmode='group')
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Mostrando resumen general de datos.")

with col_g2:
    st.markdown("#### Principales Proveedores")
    col_prov = next((c for c in df.columns if 'proveedor' in c.lower()), None)
    if col_prov and col_total:
        df_p = df.groupby(col_prov, as_index=False)[col_total].sum().sort_values(by=col_total, ascending=True).tail(10)
        fig2 = px.bar(df_p, x=col_total, y=col_prov, orientation='h')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Columna de proveedores no detectada en la hoja.")
