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

# Búsqueda inteligente de columnas
def buscar_col(keywords):
    for c in df.columns:
        if any(kw in c.lower() for kw in keywords):
            return c
    return None

col_total = buscar_col(['total', 'facturado', 'importe']) or (df.columns[0] if len(df.columns) > 0 else None)
col_cocina = buscar_col(['cocina'])
col_sala = buscar_col(['sala'])
col_eventos = buscar_col(['evento', 'otros', 'otro'])
col_mes = buscar_col(['mes'])
col_semana = buscar_col(['semana'])
col_prov = buscar_col(['proveedor', 'proveedores'])

# Limpiar columnas numéricas
for c in [col_total, col_cocina, col_sala, col_eventos]:
    if c and c in df.columns:
        df[c] = df[c].apply(limpiar_moneda)

st.title("📊 Panel Interactivo de Albaranes")
st.markdown("Análisis completo de facturación y control de gastos.")
st.markdown("---")

# Métricas principales
total_registros = len(df)
val_total = df[col_total].sum() if col_total and col_total in df.columns else 0
val_cocina = df[col_cocina].sum() if col_cocina and col_cocina in df.columns else 0
val_sala = df[col_sala].sum() if col_sala and col_sala in df.columns else 0
val_eventos = df[col_eventos].sum() if col_eventos and col_eventos in df.columns else 0

st.markdown(f"### Resumen Económico ({total_registros} registros)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Facturado", f"{val_total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c2.metric("Gasto Cocina", f"{val_cocina:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c3.metric("Gasto Sala", f"{val_sala:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c4.metric("Eventos y Otros", f"{val_eventos:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# Fila 1 de gráficos: Rosquilla y Proveedores
g1, g2 = st.columns(2)

with g1:
    st.markdown("#### 🍩 Distribución de Gastos (Rosquilla)")
    datos_rosquilla = {
        'Categoría': ['Cocina', 'Sala', 'Eventos y Otros'],
        'Importe': [val_cocina, val_sala, val_eventos]
    }
    df_rosq = pd.DataFrame(datos_rosquilla)
    if df_rosq['Importe'].sum() > 0:
        fig_donut = px.pie(df_rosq, names='Categoría', values='Importe', hole=0.4)
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No hay importes suficientes para mostrar la rosquilla.")

with g2:
    st.markdown("#### 🏢 Principales Proveedores")
    if col_prov and col_total and col_prov in df.columns and col_total in df.columns:
        df_p = df.groupby(col_prov, as_index=False)[col_total].sum().sort_values(by=col_total, ascending=True).tail(10)
        fig_prov = px.bar(df_p, x=col_total, y=col_prov, orientation='h')
        st.plotly_chart(fig_prov, use_container_width=True)
    else:
        st.info("Columna de proveedores no disponible.")

st.markdown("---")

# Fila 2 de gráficos: Gasto por Mes y Gasto por Semana
g3, g4 = st.columns(2)

with g3:
    st.markdown("#### 📅 Gasto por Mes")
    if col_mes and col_total and col_mes in df.columns and col_total in df.columns:
        df_mes = df.groupby(col_mes, as_index=False)[col_total].sum()
        fig_mes = px.bar(df_mes, x=col_mes, y=col_total)
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("Columna de mes no disponible en el Excel.")

with g4:
    st.markdown("#### 📈 Gasto por Semana")
    if col_semana and col_total and col_semana in df.columns and col_total in df.columns:
        df_sem = df.groupby(col_semana, as_index=False)[col_total].sum()
        fig_sem = px.bar(df_sem, x=col_semana, y=col_total)
        st.plotly_chart(fig_sem, use_container_width=True)
    else:
        st.info("Columna de semana no disponible en el Excel.")
