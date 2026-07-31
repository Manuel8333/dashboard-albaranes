import io
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial del layout en modo ancho
st.set_page_config(page_title="Dashboard Interactivo de Albaranes", layout="wide")

# Carga y caché de datos optimizada desde Google Drive
@st.cache_data
def cargar_datos():
    file_id = "1ojkVcMlXHcO_A_oCvm-TcufKmapsoEto"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_excel(io.BytesIO(response.content), sheet_name="DATOS")

try:
    df = cargar_datos()
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"Error al cargar los datos desde Google Drive: {e}")
    st.stop()

# Función robusta de limpieza de moneda
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

# Detección inteligente de columnas clave
def encontrar_columna(opciones):
    for op in opciones:
        for c in df.columns:
            if op.lower() in c.lower():
                return c
    return None

col_total = encontrar_columna(['total factura', 'total_factura', 'total', 'importe'])
col_cocina = encontrar_columna(['cocina'])
col_sala = encontrar_columna(['sala'])
col_otros = encontrar_columna(['evento', 'otros', 'otro'])
col_prov = encontrar_columna(['proveedor', 'proveedores'])
col_fecha = encontrar_columna(['fecha', 'mes', 'semana', 'periodo', 'dia'])

# Limpieza estricta de las columnas monetarias
for c in [col_total, col_cocina, col_sala, col_otros]:
    if c and c in df.columns:
        df[c] = df[c].apply(limpiar_moneda)

# Conversión segura de fecha si existe
if col_fecha:
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')

# ==========================================
# BARRA LATERAL: FILTROS INTERACTIVOS
# ==========================================
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.markdown("---")
st.sidebar.subheader("Filtros Dinámicos")

df_filtrado = df.copy()

# Filtro interactivo por Proveedor con opción de Seleccionar Todos
if col_prov:
    proveedores_unicos = sorted(df[col_prov].dropna().astype(str).unique())
    
    # Casilla para marcar/desmarcar todos de golpe
    seleccionar_todos = st.sidebar.checkbox("Seleccionar todos los proveedores", value=True)
    
    if seleccionar_todos:
        prov_seleccionados = st.sidebar.multiselect("Filtrar por Proveedor:", proveedores_unicos, default=proveedores_unicos)
    else:
        prov_seleccionados = st.sidebar.multiselect("Filtrar por Proveedor:", proveedores_unicos, default=[])

    if prov_seleccionados:
        df_filtrado = df_filtrado[df_filtrado[col_prov].astype(str).isin(prov_seleccionados)]

# Filtro interactivo por Rango de Fechas
if col_fecha and not df[col_fecha].isna().all():
    min_date = df[col_fecha].min()
    max_date = df[col_fecha].max()
    if pd.notna(min_date) and pd.notna(max_date):
        rango_fechas = st.sidebar.date_input(
            "Seleccionar Rango de Fechas:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        if len(rango_fechas) == 2:
            start_d, end_d = rango_fechas
            df_filtrado = df_filtrado[
                (df_filtrado[col_fecha].dt.date >= start_d) & 
                (df_filtrado[col_fecha].dt.date <= end_d)
            ]

# ==========================================
# CUERPO PRINCIPAL DEL DASHBOARD
# ==========================================
st.title("📊 Dashboard Interactivo de Albaranes")
st.markdown("Panel de control económico con desglose por Cocina, Sala y Otros, actualizado en tiempo real.")
st.markdown("---")

# Métricas calculadas sobre el dataset filtrado
total_registros_total = len(df)
total_registros_filtro = len(df_filtrado)

val_total = df_filtrado[col_total].sum() if col_total else 0
val_cocina = df_filtrado[col_cocina].sum() if col_cocina else 0
val_sala = df_filtrado[col_sala].sum() if col_sala else 0
val_otros = df_filtrado[col_otros].sum() if col_otros else 0

st.markdown(f"### Resumen Económico (Mostrando {total_registros_filtro} de {total_registros_total} registros)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Facturado", f"{val_total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c2.metric("Gasto Cocina", f"{val_cocina:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c3.metric("Gasto Sala", f"{val_sala:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
c4.metric("Eventos y Otros", f"{val_otros:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# Gráficos Interactivos dinámicos
g1, g2 = st.columns(2)

with g1:
    st.markdown("#### 🏢 Principales Proveedores (Filtrado)")
    if col_prov and col_total and not df_filtrado.empty:
        df_p = df_filtrado.groupby(col_prov, as_index=False)[col_total].sum().sort_values(by=col_total, ascending=True).tail(10)
        fig_prov = px.bar(
            df_p, 
            x=col_total, 
            y=col_prov, 
            orientation='h', 
            labels={col_total: "Total Facturado (€)", col_prov: "Proveedor"},
            template="plotly_white"
        )
        st.plotly_chart(fig_prov, use_container_width=True)
    else:
        st.warning("No hay datos de proveedores para los filtros seleccionados.")

with g2:
    st.markdown("#### 📈 Evolución Temporal")
    if col_fecha and col_total and not df_filtrado.empty:
        df_t = df_filtrado.groupby(df_filtrado[col_fecha].dt.date, as_index=False)[col_total].sum()
        fig_t = px.bar(
            df_t, 
            x=col_fecha, 
            y=col_total, 
            labels={col_total: "Total Facturado (€)", col_fecha: "Fecha"},
            template="plotly_white"
        )
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.warning("No hay datos temporales disponibles para graficar con los filtros actuales.")
