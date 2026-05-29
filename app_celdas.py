"""
app_celdas.py
Módulo 1 — Cálculo de producción y energía: Celdas Castner-Kellner
Planta Cloro-Soda Quimpac Paramonga — versión mobile
"""
 
import streamlit as st
from calculos_celdas import calcular
 
st.set_page_config(
    page_title="Celdas C-K | Quimpac",
    page_icon="⚡",
    layout="centered",
)
 
st.title("⚡ Celdas Castner-Kellner")
st.caption("Planta Cloro-Soda · Quimpac Paramonga")
st.divider()
 
# ══════════════════════════════════════════════════════
# ENTRADAS — una columna, agrupadas en expanders
# ══════════════════════════════════════════════════════
st.subheader("📥 Variables de entrada")
 
with st.expander("⚙️ Operación de celdas", expanded=True):
    I_kA = st.number_input("Intensidad de corriente (kA)",
                            min_value=50.0, max_value=160.0,
                            value=145.0, step=1.0, format="%.1f")
    Kf   = st.number_input("Factor Kf ACPD",
                            min_value=0.030, max_value=0.150,
                            value=0.070, step=0.001, format="%.3f")
    N    = st.number_input("Número de celdas",
                            min_value=1, max_value=36,
                            value=35, step=1)
    ec   = st.number_input("Eficiencia de corriente (0–1)",
                            min_value=0.80, max_value=1.00,
                            value=0.95, step=0.01, format="%.2f")
    tiempo_h = st.number_input("Tiempo de operación (horas)",
                                min_value=1.0, max_value=720.0,
                                value=24.0, step=1.0, format="%.1f")
 
with st.expander("🔩 Parámetros de celda", expanded=False):
    V0       = st.number_input("Tensión reversible V₀ (V)",
                                min_value=2.50, max_value=4.00,
                                value=3.15, step=0.01, format="%.2f")
    A        = st.number_input("Área activa por celda (m²)",
                                min_value=1.0, max_value=30.0,
                                value=11.451, step=0.001, format="%.3f")
    perdidas = st.number_input("Pérdidas de conexión total (V)",
                                min_value=0.0, max_value=10.0,
                                value=4.0, step=0.1, format="%.1f")
 
with st.expander("⚡ Sistema eléctrico y tarifa", expanded=False):
    eta_rect_trafo = st.number_input("Eficiencia rectificación y transformación (0–1)",
                                      min_value=0.80, max_value=1.00,
                                      value=0.98, step=0.01, format="%.2f")
    eta_trans      = st.number_input("Eficiencia de transmisión (0–1)",
                                      min_value=0.80, max_value=1.00,
                                      value=0.95, step=0.01, format="%.2f")
    P_planta_MW    = st.number_input("Potencia auxiliar de planta (MW)",
                                      min_value=0.0, max_value=5.0,
                                      value=1.0, step=0.1, format="%.1f")
    tarifa         = st.number_input("Tarifa eléctrica ($/MWh)",
                                      min_value=10.0, max_value=200.0,
                                      value=72.0, step=1.0, format="%.1f")
 
st.divider()
 
# ══════════════════════════════════════════════════════
# CÁLCULO
# ══════════════════════════════════════════════════════
r = calcular(
    I_kA=I_kA, Kf=Kf, A=A, V0=V0,
    N=N, ec=ec, perdidas=perdidas,
    eta_rect_trafo=eta_rect_trafo, eta_trans=eta_trans,
    P_planta_MW=P_planta_MW, tiempo_h=tiempo_h, tarifa=tarifa,
)
 
V_TRAFO_LIMITE = 148.5
margen_V       = V_TRAFO_LIMITE - r["V_total_V"]
 
# ══════════════════════════════════════════════════════
# RESULTADOS
# ══════════════════════════════════════════════════════
st.subheader("📊 Resultados")
 
# Alerta transformador
if margen_V < 0:
    st.error(f"⚠️ ALERTA: V_total = {r['V_total_V']} V supera límite {V_TRAFO_LIMITE} V "
             f"({abs(margen_V):.2f} V por encima)")
else:
    st.success(f"✅ Tensión OK — margen {margen_V:.2f} V hasta límite {V_TRAFO_LIMITE} V")
 
# Tensiones
st.markdown("#### 🔌 Tensiones")
col1, col2 = st.columns(2)
col1.metric("V celda", f"{r['V_celda_V']:.4f} V")
col2.metric("V total circuito", f"{r['V_total_V']:.3f} V")
 
# Potencia
st.markdown("#### ⚡ Potencia")
col1, col2 = st.columns(2)
col1.metric("Celdas CC", f"{r['P_celdas_MW']:.3f} MW")
col2.metric("Total planta CA", f"{r['P_total_MW']:.3f} MW")
 
# Producción
st.markdown("#### 🧪 Producción")
col1, col2 = st.columns(2)
col1.metric("NaOH / celda", f"{r['tn_naoh_celda']:.3f} tn")
col2.metric("NaOH total", f"{r['tn_naoh_total']:.2f} tn")
col1, col2 = st.columns(2)
col1.metric("Cl₂ total", f"{r['tn_cl2_total']:.2f} tn")
col2.metric("Tiempo", f"{tiempo_h:.0f} h")
 
# Energía
st.markdown("#### 🔋 Energía")
col1, col2 = st.columns(2)
col1.metric("Celdas DC", f"{r['E_celdas_MWh']:.2f} MWh",
            help="Para ratios operativos")
col2.metric("Total CA", f"{r['E_total_MWh']:.2f} MWh",
            help="Para costo / COES")
 
st.divider()
 
# Indicadores
st.subheader("📈 Indicadores")
 
col1, col2 = st.columns(2)
col1.metric("kWh / tn NaOH", f"{r['ratio_kwh_naoh']:,.0f}",
            help="Energía DC celdas / producción NaOH")
col2.metric("kWh / tn Cl₂",  f"{r['ratio_kwh_cl2']:,.0f}",
            help="Energía DC celdas / producción Cl₂")
 
costo_tn_naoh = r["costo_usd"] / r["tn_naoh_total"] if r["tn_naoh_total"] > 0 else 0
costo_tn_cl2  = r["costo_usd"] / r["tn_cl2_total"]  if r["tn_cl2_total"]  > 0 else 0
 
st.metric("Costo total energía", f"$ {r['costo_usd']:,.2f}",
          help=f"Energía CA {r['E_total_MWh']:.2f} MWh × ${tarifa}/MWh")
 
col1, col2 = st.columns(2)
col1.metric("$/tn NaOH", f"$ {costo_tn_naoh:.2f}")
col2.metric("$/tn Cl₂",  f"$ {costo_tn_cl2:.2f}")
 
st.divider()
 
# Fórmulas
with st.expander("🔢 Fórmulas aplicadas"):
    st.markdown(f"""
| Cálculo | Fórmula | Resultado |
|---|---|---|
| V celda | V₀ + Kf × I(kA) / A | {r['V_celda_V']:.4f} V |
| V total | V_celda × N + pérdidas | {r['V_total_V']:.3f} V |
| P celdas CC | I(kA) × V_total / 1000 | {r['P_celdas_MW']:.3f} MW |
| P total CA | P_celdas / (η_rect × η_trans) + P_planta | {r['P_total_MW']:.3f} MW |
| NaOH / celda | I(kA) × t(h) × ec / 670 | {r['tn_naoh_celda']:.3f} tn |
| NaOH total | NaOH_celda × N | {r['tn_naoh_total']:.2f} tn |
| Cl₂ total | NaOH_total × 0.886 | {r['tn_cl2_total']:.2f} tn |
| E celdas DC | P_celdas × t | {r['E_celdas_MWh']:.2f} MWh |
| E total CA | P_total × t | {r['E_total_MWh']:.2f} MWh |
| kWh/tn NaOH | E_DC(kWh) / NaOH_total | {r['ratio_kwh_naoh']:,.0f} |
| kWh/tn Cl₂ | E_DC(kWh) / Cl₂_total | {r['ratio_kwh_cl2']:,.0f} |
| Costo | E_CA(MWh) × tarifa | $ {r['costo_usd']:,.2f} |
    """)
 
st.caption("Módulo 1 v1.1 · Quimpac Paramonga · Planta Cloro-Soda")
 
