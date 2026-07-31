import io
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Panel Interactivo de Albaranes", layout="wide")

# ==========================================
# CARGA DE DATOS DESDE GOOGLE DRIVE
# ==========================================
@st.cache_data
def cargar_datos():
    file_id = "1ojkVcMlXHcO_A_oCvm-TcufKmapsoEto"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    return pd.read_excel(io.BytesIO(response.content), sheet_name="DATOS")

df = cargar_datos()

# ==========================================
# PROCESAMIENTO Y LIMPIEZA DE DATOS
# ==========================================
# Asegurarnos de que las columnas de fecha y numéricas tengan el formato correcto
if 'Fecha' in df.columns:
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

# Convertir columnas monetarias si vienen como texto
for col in ['Total Facturado', 'Gasto Cocina', 'Gasto Sala', 'Eventos y Otros']:
    if col in df.columns and df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ==========================================
# BARRA LATERAL - FILTROS DE ANÁLISIS
# ==========================================
st.sidebar.markdown("## 🛠️ Filtros de Análisis")

# Filtro de Mes
if 'Mes' in df.columns:
    meses_disponibles = sorted(df['Mes'].dropna().unique())
    mes_seleccionado = st.sidebar.multiselect("Selecciona el Mes:", options=meses_disponibles, default=meses_disponibles)
    if mes_seleccionado:
        df = df[df['Mes'].isin(mes_seleccionado)]

# Filtro de Semana
if 'Semana' in df.columns:
    semanas_disponibles = sorted(df['Semana'].dropna().unique())
    semana_seleccionada = st.sidebar.multiselect("Selecciona la Semana:", options=semanas_disponibles, default=semanas_disponibles)
    if semana_seleccionada:
        df = df[df['Semana'].isin(semana_seleccionada)]

# Filtro de Área (Sala/Cocina)
if 'Área' in df.columns:
    areas_disponibles = sorted(df['Área'].dropna().unique())
    area_seleccionada = st.sidebar.multiselect("Área (Sala/Cocina):", options=areas_disponibles, default=areas_disponibles)
    if area_seleccionada:
        df = df[df['Área'].isin(area_seleccionada)]

# Filtro de Tipo de Operativa
if 'Tipo de Operativa' in df.columns:
    operativa_disponibles = sorted(df['Tipo de Operativa'].dropna().unique())
    operativa_seleccionada = st.sidebar.multiselect("Tipo de Operativa:", options=operativa_disponibles, default=operativa_disponibles)
    if operativa_seleccionada:
        df = df[df['Tipo de Operativa'].isin(operativa_seleccionada)]

# ==========================================
# CUERPO PRINCIPAL DEL PANEL
# ==========================================
st.title("📊 Panel Interactivo de Albaranes")
st.markdown("Análisis avanzado de facturación. Utiliza el menú lateral para cruzar datos.")
st.markdown("---")

# Resumen Económico
total_registros = len(df)
total_facturado = df['Total Facturado'].sum() if 'Total Facturado' in df.columns else 0
gasto_cocina = df['Gasto Cocina'].sum() if 'Gasto Cocina' in df.columns else 0
gasto_sala = df['Gasto Sala'].sum() if 'Gasto Sala' in df.columns else 0
eventos_otros = df['Eventos y Otros'].sum() if 'Eventos y Otros' in df.columns else 0

st.markdown(f"### Resumen Económico ({total_registros} registros)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Facturado", f"{total_facturado:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("Gasto Cocina", f"{gasto_cocina:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Gasto Sala", f"{gasto_sala:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
col4.metric("Eventos y Otros", f"{eventos_otros:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# Gráficas inferiores
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### Gasto por Semana y Área")
    if 'Semana' in df.columns and 'Total Facturado' in df.columns and 'Área' in df.columns:
        df_gasto_semana = df.groupby(['Semana', 'Área'], as_index=False)['Total Facturado'].sum()
        fig_semana = px.bar(df_gasto_semana, x='Semana', y='Total Facturado', color='Área', barmode='group')
        st.plotly_chart(fig_semana, use_container_width=True)
    else:
        st.info("No hay suficientes datos para mostrar la gráfica por semana.")

with col_g2:
    st.markdown("#### Principales Proveedores del Periodo")
    if 'Proveedor' in df.columns and 'Total Facturado' in df.columns:
        df_proveedores = df.groupby('Proveedor', as_index=False)['Total Facturado'].sum()
        df_proveedores = df_proveedores.sort_values(by='Total Facturado', ascending=True).tail(10)
        fig_prov = px.bar(df_proveedores, x='Total Facturado', y='Proveedor', orientation='h')
        st.plotly_chart(fig_prov, use_container_width=True)
    else:
        st.info("No hay suficientes datos para mostrar la gráfica de proveedores.")