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
col_fecha = encontrar_columna(['fecha', 'dia'])
col_mes = encontrar_columna(['mes'])

# Limpieza estricta de las columnas monetarias
for c in [col_total, col_cocina, col_sala, col_otros]:
    if c and c in df.columns:
        df[c] = df[c].apply(limpiar_moneda)

# Procesar mes para el filtro directo
if col_fecha and not col_mes:
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    df['Mes_Filtro'] = df[col_fecha].dt.strftime('%B %Y')
    col_mes = 'Mes_Filtro'
elif col_mes:
    df[col_mes] = df[col_mes].astype(str)

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
    seleccionar_todos = st.sidebar.checkbox("Seleccionar todos los proveedores", value=True)
    
    if seleccionar_todos:
        prov_seleccionados = st.sidebar.multiselect("Filtrar por Proveedor:", proveedores_unicos, default=proveedores_unicos)
    else:
        prov_seleccionados = st.sidebar.multiselect("Filtrar por Proveedor:", proveedores_unicos, default=[])

    if prov_seleccionados:
        df_filtrado = df_filtrado[df_filtrado[col_prov].astype(str).isin(prov_seleccionados)]

# Filtro interactivo por Mes (Selector directo de meses)
if col_mes:
    meses_unicos = sorted(df[col_mes].dropna().astype(str).unique())
    meses_seleccionados = st.sidebar.multiselect("Filtrar por Mes:", meses_unicos, default=meses_unicos)
    if meses_seleccionados:
        df_filtrado = df_filtrado[df_filtrado[col_mes].astype(str).isin(meses_seleccionados)]

# ==========================================
# CUERPO PRINCIPAL DEL DASHBOARD
# ==========================================
st.title("📊 Dashboard Interactivo de Albaranes")
st.markdown("Panel de control económico con desglose por Cocina, Sala y Otros, actualizado en tiempo real.")
st.markdown("---")

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
    st.markdown("#### 📈 Evolución por Mes")
    if col_mes and col_total and not df_filtrado.empty:
        df_m = df_filtrado.groupby(col_mes, as_index=False)[col_total].sum()
        fig_m = px.bar(
            df_m, 
            x=col_mes, 
            y=col_total, 
            labels={col_total: "Total Facturado (€)", col_mes: "Mes"},
            template="plotly_white"
        )
        st.plotly_chart(fig_m, use_container_width=True)
    else:
        st.warning("No hay datos temporales disponibles para graficar con los filtros actuales.")
