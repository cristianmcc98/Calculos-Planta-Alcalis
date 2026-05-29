"""
app_celdas.py
Módulo 1 — Cálculo de producción y energía: Celdas Castner-Kellner
Planta Cloro-Soda Quimpac Paramonga
"""

import streamlit as st
from calculos_celdas import calcular

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Celdas C-K | Quimpac",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Módulo 1 — Celdas Castner-Kellner")
st.caption("Planta Cloro-Soda · Quimpac Paramonga")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PANEL DE ENTRADAS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📥 Variables de entrada")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Operación de celdas**")
    I_kA   = st.number_input("Intensidad de corriente (kA)",
                              min_value=50.0, max_value=160.0,
                              value=145.0, step=1.0, format="%.1f")
    Kf     = st.number_input("Factor Kf ACPD",
                              min_value=0.030, max_value=0.150,
                              value=0.070, step=0.001, format="%.3f")
    N      = st.number_input("Número de celdas",
                              min_value=1, max_value=36,
                              value=35, step=1)
    ec     = st.number_input("Eficiencia de corriente (0–1)",
                              min_value=0.80, max_value=1.00,
                              value=0.95, step=0.01, format="%.2f")

with col2:
    st.markdown("**Parámetros de celda**")
    V0     = st.number_input("Tensión reversible V₀ (V)",
                              min_value=2.50, max_value=4.00,
                              value=3.15, step=0.01, format="%.2f")
    A      = st.number_input("Área activa por celda (m²)",
                              min_value=1.0, max_value=30.0,
                              value=11.451, step=0.001, format="%.3f")
    perdidas = st.number_input("Pérdidas de conexión total (V)",
                                min_value=0.0, max_value=10.0,
                                value=4.0, step=0.1, format="%.1f")
    tiempo_h = st.number_input("Tiempo de operación (horas)",
                                min_value=1.0, max_value=720.0,
                                value=24.0, step=1.0, format="%.1f")

with col3:
    st.markdown("**Sistema eléctrico y tarifa**")
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

# ══════════════════════════════════════════════════════════════════════════════
# CÁLCULO
# ══════════════════════════════════════════════════════════════════════════════
r = calcular(
    I_kA=I_kA, Kf=Kf, A=A, V0=V0,
    N=N, ec=ec, perdidas=perdidas,
    eta_rect_trafo=eta_rect_trafo, eta_trans=eta_trans,
    P_planta_MW=P_planta_MW, tiempo_h=tiempo_h, tarifa=tarifa,
)

# Alerta transformador (límite 148.5 V)
V_TRAFO_LIMITE = 148.5
alerta_trafo = r["V_total_V"] > V_TRAFO_LIMITE
margen_V = V_TRAFO_LIMITE - r["V_total_V"]

# ══════════════════════════════════════════════════════════════════════════════
# PANEL DE RESULTADOS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📊 Resultados")

# ── Alerta transformador ──────────────────────────────────────────────────────
if alerta_trafo:
    st.error(
        f"⚠️ **ALERTA TRANSFORMADOR** — V_total = {r['V_total_V']} V "
        f"supera el límite de {V_TRAFO_LIMITE} V "
        f"({abs(margen_V):.2f} V por encima)"
    )
else:
    st.success(
        f"✅ Tensión dentro del límite del transformador — "
        f"Margen disponible: {margen_V:.2f} V  "
        f"(límite {V_TRAFO_LIMITE} V)"
    )

# ── Bloques de métricas ───────────────────────────────────────────────────────
st.markdown("#### Tensiones")
c1, c2, c3 = st.columns(3)
c1.metric("Tensión de celda", f"{r['V_celda_V']:.4f} V")
c2.metric("Tensión total circuito", f"{r['V_total_V']:.3f} V")
c3.metric("Margen vs transformador", f"{margen_V:.2f} V",
          delta_color="normal" if margen_V >= 0 else "inverse")

st.markdown("#### Potencia")
c1, c2 = st.columns(2)
c1.metric("Potencia celdas (CC)", f"{r['P_celdas_MW']:.3f} MW",
          help="Potencia consumida directamente por las celdas en corriente continua")
c2.metric("Potencia total planta (CA)", f"{r['P_total_MW']:.3f} MW",
          help="Potencia total retirada del SEIN — base para declaración COES/Osinergmin")

st.markdown("#### Producción")
c1, c2, c3 = st.columns(3)
c1.metric("NaOH por celda", f"{r['tn_naoh_celda']:.3f} tn",
          help=f"En {tiempo_h:.0f} h de operación")
c2.metric("NaOH total", f"{r['tn_naoh_total']:.2f} tn",
          help=f"{N} celdas × {tiempo_h:.0f} h")
c3.metric("Cl₂ total", f"{r['tn_cl2_total']:.2f} tn",
          help="NaOH total × 0.886 (relación molar Cl₂/NaOH)")

st.markdown("#### Energía")
c1, c2 = st.columns(2)
c1.metric("Energía celdas (DC)", f"{r['E_celdas_MWh']:.2f} MWh",
          help="Base para ratios operativos — equivale a lo reportado por ACPD")
c2.metric("Energía total planta (CA)", f"{r['E_total_MWh']:.2f} MWh",
          help="Base para costo de energía y declaración ante COES / Osinergmin")

st.divider()

# ── Indicadores operativos y costo ───────────────────────────────────────────
st.subheader("📈 Indicadores")

c1, c2, c3 = st.columns(3)

c1.metric(
    "kWh / tn NaOH",
    f"{r['ratio_kwh_naoh']:,.1f}",
    help="Ratio operativo — calculado con energía DC de celdas"
)
c2.metric(
    "kWh / tn Cl₂",
    f"{r['ratio_kwh_cl2']:,.1f}",
    help="Ratio operativo — calculado con energía DC de celdas"
)
c3.metric(
    "Costo de energía",
    f"$ {r['costo_usd']:,.2f}",
    help=f"Energía total CA ({r['E_total_MWh']:.2f} MWh) × tarifa (${tarifa}/MWh)"
)

# Costo unitario derivado
costo_tn_naoh = r["costo_usd"] / r["tn_naoh_total"] if r["tn_naoh_total"] > 0 else 0
costo_tn_cl2  = r["costo_usd"] / r["tn_cl2_total"]  if r["tn_cl2_total"]  > 0 else 0

c1, c2 = st.columns(2)
c1.metric("Costo energía / tn NaOH", f"$ {costo_tn_naoh:.2f}",
          help="Costo total CA / producción NaOH")
c2.metric("Costo energía / tn Cl₂",  f"$ {costo_tn_cl2:.2f}",
          help="Costo total CA / producción Cl₂")

st.divider()

# ── Resumen de fórmulas aplicadas ─────────────────────────────────────────────
with st.expander("🔢 Fórmulas aplicadas"):
    st.markdown(f"""
| Cálculo | Fórmula | Resultado |
|---|---|---|
| Tensión de celda | V₀ + Kf × I(kA) / A | {r['V_celda_V']:.4f} V |
| Tensión total | V_celda × N + pérdidas | {r['V_total_V']:.3f} V |
| Potencia celdas (CC) | I(kA) × V_total / 1000 | {r['P_celdas_MW']:.3f} MW |
| Potencia total (CA) | P_celdas / (η_rect × η_trans) + P_planta | {r['P_total_MW']:.3f} MW |
| NaOH / celda | I(kA) × t(h) × ec / 670 | {r['tn_naoh_celda']:.3f} tn |
| NaOH total | NaOH_celda × N | {r['tn_naoh_total']:.2f} tn |
| Cl₂ total | NaOH_total × 0.886 | {r['tn_cl2_total']:.2f} tn |
| Energía celdas (DC) | P_celdas × t | {r['E_celdas_MWh']:.2f} MWh |
| Energía total (CA) | P_total × t | {r['E_total_MWh']:.2f} MWh |
| kWh / tn NaOH | E_celdas(kWh) / NaOH_total | {r['ratio_kwh_naoh']:,.1f} |
| kWh / tn Cl₂ | E_celdas(kWh) / Cl₂_total | {r['ratio_kwh_cl2']:,.1f} |
| Costo energía | E_total(MWh) × tarifa | $ {r['costo_usd']:,.2f} |
    """)

st.caption("Módulo 1 v1.0 · Quimpac Paramonga · Planta Cloro-Soda")
