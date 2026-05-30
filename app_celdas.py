"""
app_celdas.py
Módulo 1 — Celdas de Mercurio
Planta Cloro-Soda Quimpac Paramonga — versión mobile
"""

import streamlit as st
from calculos_celdas import calcular

st.set_page_config(
    page_title="Celdas de Mercurio | Quimpac",
    page_icon="⚡",
    layout="centered",
)

st.title("⚡ Celdas de Mercurio")
st.markdown("### Planta Cloro-Soda · Quimpac Paramonga")
st.caption("Calculadora de producción de Cloro-Soda y consumo de energía eléctrica en Planta Álcalis.")
st.divider()

# ══════════════════════════════════════════════════════
# ENTRADAS
# ══════════════════════════════════════════════════════
st.subheader("📥 Variables de entrada")

with st.expander("⚙️ Operación sin modulación", expanded=True):
    I_kA   = st.number_input("Intensidad de corriente (kA)",
                              min_value=50.0, max_value=160.0,
                              value=145.0, step=1.0, format="%.1f")
    Kf     = st.number_input("Factor Kf ACPD",
                              min_value=0.030, max_value=0.150,
                              value=0.070, step=0.001, format="%.3f")
    t_sin  = st.number_input("Tiempo de operación sin modulación (horas)",
                              min_value=1.0, max_value=720.0,
                              value=24.0, step=1.0, format="%.1f")

with st.expander("🔁 Modulación de carga — hora punta", expanded=True):
    st.info(
        "Durante la hora punta del sistema eléctrico nacional se reduce la carga "
        "para evitar multas por sobreconsumo. Ingrese 0 en ambos campos si no aplica modulación."
    )
    I_mod  = st.number_input("Intensidad durante modulación (kA)",
                              min_value=0.0, max_value=160.0,
                              value=50.0, step=1.0, format="%.1f")
    Kf_mod = st.number_input("Factor Kf durante modulación",
                              min_value=0.030, max_value=0.150,
                              value=0.098, step=0.001, format="%.3f")
    t_mod  = st.number_input("Tiempo de modulación (horas)",
                              min_value=0.0, max_value=24.0,
                              value=3.0, step=0.5, format="%.1f")

with st.expander("🔩 Parámetros de celda", expanded=False):
    V0       = st.number_input("Voltaje de descomposición V₀ (V)",
                                min_value=2.50, max_value=4.00,
                                value=3.15, step=0.01, format="%.2f")
    A        = st.number_input("Área activa por celda (m²)",
                                min_value=1.0, max_value=30.0,
                                value=11.451, step=0.001, format="%.3f")
    N        = st.number_input("Número de celdas",
                                min_value=1, max_value=36,
                                value=35, step=1)
    ec       = st.number_input("Eficiencia de corriente (0–1)",
                                min_value=0.80, max_value=1.00,
                                value=0.95, step=0.01, format="%.2f")
    perdidas = st.number_input("Pérdidas de conexión total (V)",
                                min_value=0.0, max_value=10.0,
                                value=4.0, step=0.1, format="%.1f")

with st.expander("⚡ Sistema eléctrico y tarifa", expanded=False):
    eta_rect = st.number_input("Eficiencia rectificación y transformación (0–1)",
                                min_value=0.80, max_value=1.00,
                                value=0.98, step=0.01, format="%.2f")
    eta_trans= st.number_input("Eficiencia de transmisión (0–1)",
                                min_value=0.80, max_value=1.00,
                                value=0.95, step=0.01, format="%.2f")
    P_planta = st.number_input("Potencia auxiliar de planta (MW)",
                                min_value=0.0, max_value=5.0,
                                value=1.0, step=0.1, format="%.1f")
    tarifa   = st.number_input("Tarifa eléctrica ($/MWh)",
                                min_value=10.0, max_value=200.0,
                                value=72.0, step=1.0, format="%.1f")

st.divider()

# ══════════════════════════════════════════════════════
# CÁLCULO
# ══════════════════════════════════════════════════════
r = calcular(
    I_kA=I_kA, Kf=Kf, t_sin=t_sin,
    I_mod_kA=I_mod, Kf_mod=Kf_mod, t_mod=t_mod,
    A=A, V0=V0, N=N, ec=ec, perdidas=perdidas,
    eta_rect_trafo=eta_rect, eta_trans=eta_trans,
    P_planta_MW=P_planta, tarifa=tarifa,
)

con_mod = t_mod > 0

# ══════════════════════════════════════════════════════
# RESULTADOS
# ══════════════════════════════════════════════════════
st.subheader("📊 Resultados")

# ── Alerta transformador ──────────────────────────────
V_TRAFO = 148.5
if r["alerta_trafo"]:
    st.error(
        f"⚠️ **ALERTA RECTIFICADORES** — V_total = {r['V_total_sin']} V "
        f"supera el límite de {V_TRAFO} V "
        f"({abs(r['margen_V']):.2f} V por encima) — "
        f"Utilización: {r['uso_trafo_pct']}%"
    )
else:
    st.success(
        f"✅ Tensión dentro del límite de los rectificadores — "
        f"Margen: {r['margen_V']:.2f} V hasta {V_TRAFO} V — "
        f"Utilización: {r['uso_trafo_pct']}%"
    )

# ── Resultados de Voltaje ─────────────────────────────
st.markdown("#### 🔌 Resultados de Voltaje")
col1, col2 = st.columns(2)
col1.metric("Voltaje de celda — sin modulación", f"{r['V_celda_sin']:.4f} V")
col2.metric("Voltaje total circuito — sin modulación", f"{r['V_total_sin']:.3f} V")

if con_mod:
    col1, col2 = st.columns(2)
    col1.metric("Voltaje de celda — modulación", f"{r['V_celda_mod']:.4f} V")
    col2.metric("Voltaje total circuito — modulación", f"{r['V_total_mod']:.3f} V")

# ── Potencia ──────────────────────────────────────────
st.markdown("#### ⚡ Potencia")
col1, col2 = st.columns(2)
col1.metric("Potencia consumida por celdas corriente continua — sin mod.",
            f"{r['P_celdas_sin']:.3f} MW")
col2.metric("Potencia total de la Planta en Corriente Alterna — sin mod.",
            f"{r['P_total_sin']:.3f} MW")

if con_mod:
    col1, col2 = st.columns(2)
    col1.metric("Potencia consumida por celdas corriente continua — modulación",
                f"{r['P_celdas_mod']:.3f} MW")
    col2.metric("Potencia total de la Planta en Corriente Alterna — modulación",
                f"{r['P_total_mod']:.3f} MW")

# ── Producción ────────────────────────────────────────
st.markdown("#### 🧪 Producción")
if con_mod:
    st.caption(f"Calculada con intensidad promedio: {r['I_prom']:.2f} kA — tiempo total: {r['t_total']:.0f} h")
col1, col2 = st.columns(2)
col1.metric("NaOH por celda", f"{r['tn_naoh_celda']:.3f} tn")
col2.metric("NaOH total", f"{r['tn_naoh_total']:.2f} tn")
col1, col2 = st.columns(2)
col1.metric("Cl₂ total", f"{r['tn_cl2_total']:.2f} tn")
col2.metric("Tiempo total", f"{r['t_total']:.0f} h")

# ── Energía ───────────────────────────────────────────
st.markdown("#### 🔋 Energía")
col1, col2 = st.columns(2)
col1.metric("Energía celdas DC",
            f"{r['E_celdas_MWh']:.2f} MWh",
            help="Indicador operativo — equivale a lo reportado por ACPD")
col2.metric("Energía total Planta CA",
            f"{r['E_total_MWh']:.2f} MWh",
            help="Base para costo de energía y declaración COES / Osinergmin")

st.divider()

# ── Indicadores ───────────────────────────────────────
st.subheader("📈 Indicadores operativos")
st.caption("Calculados con energía DC de celdas — comparables con reporte ACPD")

col1, col2 = st.columns(2)
col1.metric("kWh / tn NaOH", f"{r['ratio_kwh_naoh']:,.0f}")
col2.metric("kWh / tn Cl₂",  f"{r['ratio_kwh_cl2']:,.0f}")

st.subheader("💲 Costos de energía")
st.caption("Calculados con energía total CA — base para declaración COES / Osinergmin")

st.metric("Costo total energía", f"$ {r['costo_usd']:,.2f}")
col1, col2 = st.columns(2)
col1.metric("$ / tn NaOH", f"$ {r['costo_tn_naoh']:.2f}")
col2.metric("$ / tn Cl₂",  f"$ {r['costo_tn_cl2']:.2f}")

st.divider()

# ── Fórmulas ──────────────────────────────────────────
with st.expander("🔢 Fórmulas aplicadas"):
    st.markdown(f"""
| Cálculo | Fórmula | Resultado |
|---|---|---|
| I promedio | (I_sin×t_sin + I_mod×t_mod) / t_total | {r['I_prom']:.3f} kA |
| V celda sin mod. | V₀ + Kf × I(kA) / A | {r['V_celda_sin']:.4f} V |
| V total sin mod. | V_celda × N + pérdidas | {r['V_total_sin']:.3f} V |
| V celda modulación | V₀ + Kf_mod × I_mod(kA) / A | {r['V_celda_mod']:.4f} V |
| V total modulación | V_celda_mod × N + pérdidas | {r['V_total_mod']:.3f} V |
| P celdas DC sin mod. | I(kA) × V_total_sin / 1000 | {r['P_celdas_sin']:.3f} MW |
| P total CA sin mod. | P_celdas / (η_rect × η_trans) + P_planta | {r['P_total_sin']:.3f} MW |
| P celdas DC mod. | I_mod(kA) × V_total_mod / 1000 | {r['P_celdas_mod']:.3f} MW |
| P total CA mod. | P_celdas_mod / (η_rect × η_trans) + P_planta | {r['P_total_mod']:.3f} MW |
| E celdas DC | P_celdas_sin×t_sin + P_celdas_mod×t_mod | {r['E_celdas_MWh']:.2f} MWh |
| E total CA | P_total_sin×t_sin + P_total_mod×t_mod | {r['E_total_MWh']:.2f} MWh |
| NaOH / celda | I_prom × t_total × ec / 670 | {r['tn_naoh_celda']:.3f} tn |
| NaOH total | NaOH_celda × N | {r['tn_naoh_total']:.2f} tn |
| Cl₂ total | NaOH_total × 0.886 | {r['tn_cl2_total']:.2f} tn |
| kWh / tn NaOH | E_celdas_DC(kWh) / NaOH_total | {r['ratio_kwh_naoh']:,.0f} |
| kWh / tn Cl₂ | E_celdas_DC(kWh) / Cl₂_total | {r['ratio_kwh_cl2']:,.0f} |
| Costo total | E_total_CA(MWh) × tarifa | $ {r['costo_usd']:,.2f} |
    """)

st.caption("Módulo 1 v2.0 · Quimpac Paramonga · Planta Cloro-Soda")
