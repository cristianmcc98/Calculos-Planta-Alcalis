"""
calculos_celdas.py
Motor de cálculos — Módulo 1: Celdas Castner-Kellner
Quimpac Paramonga
"""

def calcular(I_kA, Kf, A, V0, N, ec, perdidas, eta_rect_trafo, eta_trans, P_planta_MW, tiempo_h, tarifa):
    """
    Parámetros
    ----------
    I_kA            : Intensidad de corriente (kA)
    Kf              : Factor Kf ACPD (adimensional / S/cm según planta)
    A               : Área activa por celda (m²)
    V0              : Tensión reversible (V)
    N               : Número de celdas
    ec              : Eficiencia de corriente (0–1)
    perdidas        : Pérdidas de conexión circuito total (V)
    eta_rect_trafo  : Eficiencia rectificación y transformación (0–1)
    eta_trans       : Eficiencia de transmisión (0–1)
    P_planta_MW     : Potencia auxiliar de planta (MW)
    tiempo_h        : Tiempo de operación (horas)
    tarifa          : Precio de energía ($/MWh)
    """

    # ── 1. Tensiones ─────────────────────────────────────────────
    V_celda = V0 + Kf * I_kA / A                         # V
    V_total = V_celda * N + perdidas                      # V

    # ── 2. Potencia celdas (CC) ───────────────────────────────────
    P_celdas_MW = I_kA * V_total / 1000                  # MW

    # ── 3. Potencia total planta (CA) ────────────────────────────
    P_total_MW = P_celdas_MW / (eta_rect_trafo * eta_trans) + P_planta_MW  # MW

    # ── 4. Energía ───────────────────────────────────────────────
    E_celdas_MWh = P_celdas_MW * tiempo_h                # MWh  → ratios operativos
    E_total_MWh  = P_total_MW  * tiempo_h                # MWh  → costo / declaración

    E_celdas_kWh = E_celdas_MWh * 1000
    E_total_kWh  = E_total_MWh  * 1000

    # ── 5. Producción NaOH ───────────────────────────────────────
    # Tn NaOH por celda = I(kA) × t(h) × ec / 670
    tn_naoh_celda = I_kA * tiempo_h * ec / 670           # tn NaOH / celda
    tn_naoh_total = tn_naoh_celda * N                    # tn NaOH total

    # ── 6. Producción Cl₂ ────────────────────────────────────────
    tn_cl2_total = tn_naoh_total * 0.886                 # tn Cl₂

    # ── 7. Ratios energéticos (solo E_celdas DC) ─────────────────
    ratio_kwh_naoh = E_celdas_kWh / tn_naoh_total if tn_naoh_total > 0 else 0
    ratio_kwh_cl2  = E_celdas_kWh / tn_cl2_total  if tn_cl2_total  > 0 else 0

    # ── 8. Costo de energía (E_total CA) ─────────────────────────
    costo_total_usd = E_total_MWh * tarifa               # USD

    return {
        # Tensiones
        "V_celda_V":        round(V_celda, 4),
        "V_total_V":        round(V_total, 3),
        # Potencias
        "P_celdas_MW":      round(P_celdas_MW, 3),
        "P_total_MW":       round(P_total_MW, 3),
        # Energías
        "E_celdas_MWh":     round(E_celdas_MWh, 2),
        "E_total_MWh":      round(E_total_MWh, 2),
        # Producción
        "tn_naoh_celda":    round(tn_naoh_celda, 3),
        "tn_naoh_total":    round(tn_naoh_total, 2),
        "tn_cl2_total":     round(tn_cl2_total, 2),
        # Ratios operativos (DC)
        "ratio_kwh_naoh":   round(ratio_kwh_naoh, 1),
        "ratio_kwh_cl2":    round(ratio_kwh_cl2, 1),
        # Costo (CA)
        "costo_usd":        round(costo_total_usd, 2),
    }
