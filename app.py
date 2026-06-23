import streamlit as st
import pandas as pd
import numpy as np

# 1. Ajustes de UI/UX Corporativo de Alto Nivel
st.set_page_config(
    page_title="Strategic Quinquennial Planning 2026",
    page_icon="🏢",
    layout="wide"
)

# Estilos CSS Limpios e Industriales
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: 800; color: #1e3a8a; letter-spacing: -1px; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #4b5563; margin-bottom: 30px; }
    .card { background-color: #ffffff; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); border: 1px solid #e2e8f0; margin-bottom: 25px; }
    h2, h3 { color: #1f2937; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏢 Corporate Intelligence: Auditoría de Presupuestos Quinquenales</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Análisis de Descalces Interanuales (Roll-Over), Costos de Dotación (Labour) y Metas de Ahorro Estratégico</div>', unsafe_allow_html=True)

# 2. Pipeline Automatizado de Carga y Consolidación de Hojas del Excel
@st.cache_data
def load_quinquennial_data():
    import os
    archivos = [f for f in os.listdir('.') if 'Mejora' in f and f.endswith('.xlsx')]
    if not archivos:
        st.error("🚨 Error crítico: No se encontró la base de datos 'Datos Proyecto Mejora 2026.xlsx' en el repositorio.")
        st.stop()
    
    file_path = archivos[0]
    
    # Cargar las tres estructuras de ciclos quinquenales
    try:
        b24 = pd.read_excel(file_path, sheet_name='BUDGET 2024 - 2028')
        b25 = pd.read_excel(file_path, sheet_name='BUDGET 2025 - 2029')
        b26 = pd.read_excel(file_path, sheet_name='BUDGET 2026 - 2030')
    except Exception as e:
        st.error(f"Error al leer las pestañas del presupuesto: {e}")
        st.stop()
        
    for df in [b24, b25, b26]:
        df.columns = df.columns.str.strip()
        if 'Gerencia' in df.columns:
            df['Gerencia_Clean'] = df['Gerencia'].str.strip()
            
    return b24, b25, b26

b24, b25, b26 = load_quinquennial_data()

# 3. Sidebar de Navegación y Parametrización del Largo Plazo
st.sidebar.header("🏢 Filtro Organizacional")
lista_gerencias = sorted(b25['Gerencia_Clean'].dropna().unique())
gerencia_sel = st.sidebar.selectbox("Seleccione Gerencia Corporativa", lista_gerencias)

st.sidebar.markdown("---")
st.sidebar.header("🕹️ Parámetros de Simulación Quinquenal")

# Controles para simular variables macroeconómicas e internas que exige la pauta
inflacion_op = st.sidebar.slider("Escalamiento de Costos Fijos (% Anual)", 0.0, 10.0, 3.5, 0.5) / 100
cumplimiento_savings = st.sidebar.slider("Nivel de Cumplimiento de Metas de Ahorro", 0, 100, 100, 5) / 100
ajuste_labour = st.sidebar.slider("Variación Estructural de Dotación (Labour)", 0.80, 1.30, 1.00, 0.05)

# 4. Procesamiento Analítico y Simulación del Ciclo 2025-2029 (Baseline Central)
df_b25_filtered = b25[b25['Gerencia_Clean'] == gerencia_sel].copy()
años_horizonte = [2025, 2026, 2027, 2028, 2029]

for col in años_horizonte:
    df_b25_filtered[col] = pd.to_numeric(df_b25_filtered[col], errors='coerce').fillna(0)

# Aplicar el motor de simulación de largo plazo
df_simulado = df_b25_filtered.copy()
for i, yr in enumerate(años_horizonte):
    # El escalamiento se acumula año con año (interés compuesto)
    factor_escalamiento = (1 + inflacion_op) ** i
    
    # Discriminar el tipo de cuenta para aplicar la regla de negocio correspondiente
    mask_labour = df_simulado['Clasificación'].str.contains('Mano de Obra|Labour|Personal|Dotación', case=False, na=False)
    mask_savings = df_simulado['Clasificación'].str.contains('Ahorro|Saving', case=False, na=False)
    
    # 1. Modificar costos de personal por dotación estructural
    df_simulado.loc[mask_labour, yr] = df_simulado[yr] * ajuste_labour * factor_escalamiento
    # 2. Amortiguar el efecto del ahorro si el cumplimiento cae
    df_simulado.loc[mask_savings, yr] = df_simulado[yr] * cumplimiento_savings
    # 3. Aplicar escalamiento general al resto de cuentas operacionales
    df_simulado.loc[~mask_labour & ~mask_savings, yr] = df_simulado[yr] * factor_escalamiento

# Totales Consolidados del Ciclo
total_original_quinquenal = df_b25_filtered[años_horizonte].sum().sum()
total_simulado_quinquenal = df_simulado[años_horizonte].sum().sum()
desviacion_global = total_simulado_quinquenal - total_original_quinquenal

# 5. Despliegue de Indicadores Clave de Desempeño Financiero (KPIs)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Budget 25-29 Original", f"${total_original_quinquenal:,.0f}")
with kpi2:
    st.metric("Budget 25-29 Simulado", f"${total_simulado_quinquenal:,.0f}")
with kpi3:
    st.metric("Variación Financiera Neta", f"${desviacion_global:,.0f}", delta=f"{desviacion_global:,.0f}", delta_color="inverse")
with kpi4:
    porc_var = (desviacion_global / (total_original_quinquenal if total_original_quinquenal != 0 else 1)) * 100
    st.metric("Impacto Estructural", f"{porc_var:.2f}%")

# 6. Gráfico de Tendencia del Horizonte Quinquenal (Adiós desorden)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"📈 Proyección Temporal del Gasto Anualizado: {gerencia_sel}")

chart_base = df_b25_filtered[años_horizonte].sum()
chart_sim = df_simulado[años_horizonte].sum()

df_chart = pd.DataFrame({
    'Budget Base Original': chart_base,
    'Budget Simulado Ajustado': chart_sim
})
st.line_chart(df_chart, use_container_width=True)
st.caption("Evolución financiera a 5 años comparando la estructura de planificación original versus el impacto simulado de inflación, Labour y Savings.")
st.markdown('</div>', unsafe_allow_html=True)

# 7. Tabla Analítica con Desglose de Cuentas Operacionales
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📋 Matriz de Planificación y Control de Cuentas")

# Limpieza visual de la tabla final
columnas_tabla = ['Clasificación'] + años_horizonte
df_tabla_final = df_simulado[columnas_tabla].groupby('Clasificación').sum()

st.dataframe(df_tabla_final.style.format('${:,.0f}'), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 8. Alertas de Gobernanza Corporativa
st.subheader("🚨 Alertas de Gobernanza Estratégica")
col_a1, col_a2 = st.columns(2)
with col_a1:
    if porc_var > 5.0:
        st.error(f"⚠️ **Alerta de Riesgo Presupuestario:** Los cambios acumulados superan el umbral tolerable del 5%. Esta gerencia requerirá un Suplemento de Capital o un rediseño de su plan de Savings.")
    elif porc_var < -2.0:
        st.success(f"✅ **Eficiencia Quinquenal Detectada:** La simulación proyecta una liberación significativa de recursos financieros que pueden apalancar otros proyectos de la compañía.")
    else:
        st.info("ℹ️ **Estabilidad Financiera:** Las variaciones simuladas se mantienen dentro del rango de desviación aceptable corporativo.")
with col_a2:
    csv_bytes = df_tabla_final.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Exportar Reporte de Auditoría Quinquenal (CSV)",
        data=csv_bytes,
        file_name=f"Auditoria_Quinquenal_{gerencia_sel.replace(' ', '_')}.csv",
        mime='text/csv',
        use_container_width=True
    )
