import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de la plataforma con UI/UX de alto nivel
st.set_page_config(
    page_title="Mining Business Intelligence 2026", 
    page_icon="📊", 
    layout="wide"
)

# Inyección de estilos CSS avanzados para limpiar bordes, espaciados y diseño de tarjetas
st.markdown("""
    <style>
    .reportview-container { background: #f8fafc; }
    .main-title { font-size: 42px; font-weight: 800; color: #0f172a; letter-spacing: -1px; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #64748b; margin-bottom: 35px; }
    .card { background-color: #ffffff; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0; margin-bottom: 25px; }
    h2, h3 { color: #1e293b; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Executive Dashboard: Optimización Analítica Forecast 5+7</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Control de Gestión Avanzado e Ingeniería de Datos aplicada a la Gerencia de Operación Concentradora</div>', unsafe_allow_html=True)

# 2. Pipeline de Carga de Datos Automatizado
@st.cache_data
def load_data():
    import os
    archivos = [f for f in os.listdir('.') if 'Datos' in f and f.endswith('.xlsx')]
    if not archivos:
        st.error("🚨 Error crítico: No se encontró la base de datos Excel en el repositorio.")
        st.stop()
    
    file_path = archivos[0]
    df = pd.read_excel(file_path, sheet_name='Forecast 5+7', skiprows=1)
    df.columns = df.columns.str.strip()
    df['Gerencia_Clean'] = df['Gerencia'].str.strip()
    df['Desc_Item_Clean'] = df['Desc Item'].str.strip()
    return df

df = load_data()
df_conc = df[df['Gerencia_Clean'] == 'Gerencia Operación Concentradora'].copy()

# Definición de la estructura temporal 5+7
meses_reales = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26']
meses_forecast = ['Jun-26', 'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26']
todos_los_meses = meses_reales + meses_forecast

for col in todos_los_meses + ['Budget FY']:
    df_conc[col] = pd.to_numeric(df_conc[col], errors='coerce').fillna(0)

# 3. Sidebar Profesional de Simulación Financiera
st.sidebar.header("🕹️ Parámetros de Simulación Operativa")
st.sidebar.markdown("Configure las variables metalúrgicas del modelo no lineal:")

escenario = st.sidebar.selectbox(
    "Escenario de Operación Planta",
    ["Plan Base Corporativo", "Campañas de Alta Dureza (Exponencial)", "Optimización de Reactivos"]
)

if escenario == "Plan Base Corporativo":
    beta_default = 1.05
    ajuste_energia_default = 1.20
elif escenario == "Campañas de Alta Dureza (Exponencial)":
    beta_default = 1.45
    ajuste_energia_default = 1.50
else:
    beta_default = 0.85
    ajuste_energia_default = 1.00

beta_factor = st.sidebar.slider("Factor de Complejidad Mineral (β
