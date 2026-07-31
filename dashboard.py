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

# Búsqueda inteligente de columna temporal o de desglose secundario
col_tiempo = encontrar_columna(['semana', 'mes', 'fecha', 'periodo', 'dia', 'área', 'area', 'concepto'])
if not col_tiempo:
    # Respaldo automático: coge la primera columna de texto que no sea proveedor
    text_cols = [c for c in df.columns if c not in [col_prov] and df[c].dtype == 'object']
    col_tiempo = text_cols[0] if text_cols else (df.columns[0] if len(df.columns) > 0 else None)

# Limpiar columnas monetarias
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
    titulo_grafico = f"Desglose por {col_tiempo}" if col_tiempo else "Desglose de Datos"
    st.markdown(f"#### 📈 {titulo_grafico}")
    if col_tiempo and col_total:
        df_t = df.groupby(col_tiempo, as_index=False)[col_total].sum()
        fig_t = px.bar(df_t, x=col_tiempo, y=col_total, labels={col_total: "Total Facturado", col_tiempo: col_tiempo})
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("No hay datos suficientes para el gráfico secundario.")
