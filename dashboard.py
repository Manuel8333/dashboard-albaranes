import io
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Facturación", layout="wide")

@st.cache_data
def cargar_datos():
    file_id = "1ojkVcMlXHcO_A_oCvm-TcufKmapsoEto"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    return pd.read_excel(io.BytesIO(response.content), sheet_name="DATOS")

try:
    df = cargar_datos()
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()

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

def encontrar_columna(opciones):
    for op in opciones:
        for c in df.columns:
            if op.lower() in c.lower():
                return c
    return None

col_importe = encontrar_columna(['importe', 'base'])
col_iva = encontrar_columna(['iva'])
col_total = encontrar_columna(['total factura', 'total_factura', 'total'])
col_prov = encontrar_columna(['proveedor', 'proveedores'])
col_semana = encontrar_columna(['semana'])
col_mes = encontrar_columna(['mes'])

# Limpiar solo las columnas monetarias reales
for c in [col_importe, col_iva, col_total]:
    if c and c in df.columns:
        df[c] = df[c].apply(limpiar_moneda)

st.title("📊 Dashboard de Control y Facturación")
st.markdown("---")

total_registros = len(df)
val_importe = df[col_importe].sum() if col_importe else 0
val_iva = df[col_iva].sum() if col_iva else 0
val_total = df[col_total].sum() if col_total else 0

st.markdown(f"### Resumen Económico ({total_registros} registros)")

c1, c2, c3 = st.columns(3)
if col_importe:
    c1.metric("Importe (Base)", f"{val_importe:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
if col_iva:
    c2.metric("IVA", f"{val_iva:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
if col_total:
    c3.metric("Total Factura", f"{val_total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

g1, g2 = st.columns(2)

with g1:
    st.markdown("#### 🏢 Principales Proveedores")
    if col_prov and col_total:
        df_p = df.groupby(col_prov, as_index=False)[col_total].sum().sort_values(by=col_total, ascending=True).tail(10)
        fig_prov = px.bar(df_p, x=col_total, y=col_prov, orientation='h', labels={col_total: "Total Facturado", col_prov: "Proveedor"})
        st.plotly_chart(fig_prov, use_container_width=True)
    else:
        st.info("Columna de proveedor no detectada.")

with g2:
    st.markdown("#### 📈 Gasto por Periodo (Semana / Mes)")
    tiempo_col = col_semana or col_mes
    if tiempo_col and col_total:
        df_t = df.groupby(tiempo_col, as_index=False)[col_total].sum()
        fig_t = px.bar(df_t, x=tiempo_col, y=col_total, labels={col_total: "Total Facturado", tiempo_col: "Periodo"})
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("Columna temporal no disponible.")
