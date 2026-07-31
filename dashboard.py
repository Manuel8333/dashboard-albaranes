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

# Detección automática y robusta de columnas numéricas y de texto
columnas_texto = [c for c in df.columns if df[c].dtype == 'object' or str(df[c].dtype).startswith('cat')]
columnas_num = []

for c in df.columns:
    muestra = df[c].apply(limpiar_moneda)
    if muestra.sum() > 0:
        columnas_num.append(c)
        df[c] = muestra

# Seleccionar principales columnas de forma inteligente
col_total = next((c for c in columnas_num if any(k in c.lower() for k in ['total', 'facturado', 'importe', 'suma'])), columnas_num[0] if columnas_num else None)
col_prov = next((c for c in columnas_texto if any(k in c.lower() for k in ['proveedor', 'nombre', 'cliente'])), columnas_texto[0] if columnas_texto else None)
col_tiempo = next((c for c in columnas_texto if any(k in c.lower() for k in ['mes', 'semana', 'fecha', 'periodo', 'dia'])), None)

st.title("📊 Dashboard de Control y Facturación")
st.markdown("---")

total_registros = len(df)
val_total = df[col_total].sum() if col_total else 0

st.markdown(f"### Resumen General ({total_registros} registros)")

# Mostrar métricas automáticas con todas las columnas numéricas detectadas
if columnas_num:
    cols_metrica = st.columns(min(len(columnas_num), 4))
    for i, col_name in enumerate(columnas_num[:4]):
        val_m = df[col_name].sum()
        with cols_metrica[i]:
            st.metric(col_name, f"{val_m:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# Estructura limpia de dashboard con gráficos profesionales
g1, g2 = st.columns(2)

with g1:
    st.markdown("#### 🏢 Top Elementos / Proveedores")
    if col_prov and col_total:
        df_p = df.groupby(col_prov, as_index=False)[col_total].sum().sort_values(by=col_total, ascending=True).tail(10)
        fig_prov = px.bar(df_p, x=col_total, y=col_prov, orientation='h')
        st.plotly_chart(fig_prov, use_container_width=True)
    else:
        st.info("No se encontró columna para agrupar.")

with g2:
    st.markdown("#### 📈 Distribución Temporal / Criterio")
    if col_tiempo and col_total:
        df_t = df.groupby(col_tiempo, as_index=False)[col_total].sum()
        fig_t = px.bar(df_t, x=col_tiempo, y=col_total)
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        alt_col = next((c for c in columnas_texto if c != col_prov), None)
        if alt_col and col_total:
            df_alt = df.groupby(alt_col, as_index=False)[col_total].sum().head(10)
            fig_alt = px.bar(df_alt, x=alt_col, y=col_total)
            st.plotly_chart(fig_alt, use_container_width=True)
        else:
            st.info("Gráfico secundario no disponible.")
