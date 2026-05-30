"""
calculos_celdas.py
Motor de cálculos — Módulo 1: Celdas Castner-Kellner
Quimpac Paramonga
"""
 
def calcular(
    I_kA, Kf, t_sin,
    I_mod_kA, Kf_mod, t_mod,
    A, V0, N, ec, perdidas,
    eta_rect_trafo, eta_trans, P_planta_MW,
    tarifa
):
    # ── Tiempo total ──────────────────────────────────────────
    t_total = t_sin + t_mod
 
    # ── Intensidad promedio (para producción) ─────────────────
    I_prom = (I_kA * t_sin + I_mod_kA * t_mod) / t_total
 
    # ── Voltajes sin modulación ───────────────────────────────
    V_celda_sin = V0 + Kf * I_kA / A
    V_total_sin = V_celda_sin * N + perdidas
 
    # ── Voltajes durante modulación ───────────────────────────
    V_celda_mod = V0 + Kf_mod * I_mod_kA / A
    V_total_mod = V_celda_mod * N + perdidas
 
    # ── Potencia sin modulación ───────────────────────────────
    P_celdas_sin = I_kA * V_total_sin / 1000
    P_total_sin  = P_celdas_sin / (eta_rect_trafo * eta_trans) + P_planta_MW
 
    # ── Potencia durante modulación ───────────────────────────
    P_celdas_mod = I_mod_kA * V_total_mod / 1000
    P_total_mod  = P_celdas_mod / (eta_rect_trafo * eta_trans) + P_planta_MW
 
    # ── Energías (cada potencia por su tiempo) ────────────────
    E_celdas_MWh = P_celdas_sin * t_sin + P_celdas_mod * t_mod
    E_total_MWh  = P_total_sin  * t_sin + P_total_mod  * t_mod
 
    E_celdas_kWh = E_celdas_MWh * 1000
 
    # ── Producción (con I_prom) ───────────────────────────────
    tn_naoh_celda = I_prom * t_total * ec / 670
    tn_naoh_total = tn_naoh_celda * N
    tn_cl2_total  = tn_naoh_total * 0.886
 
    # ── Ratios operativos (E_celdas DC) ──────────────────────
    ratio_kwh_naoh = E_celdas_kWh / tn_naoh_total if tn_naoh_total > 0 else 0
    ratio_kwh_cl2  = E_celdas_kWh / tn_cl2_total  if tn_cl2_total  > 0 else 0
 
    # ── Costo (E_total CA) ────────────────────────────────────
    costo_usd     = E_total_MWh * tarifa
    costo_tn_naoh = costo_usd / tn_naoh_total if tn_naoh_total > 0 else 0
    costo_tn_cl2  = costo_usd / tn_cl2_total  if tn_cl2_total  > 0 else 0
 
    # ── Margen transformador ──────────────────────────────────
    V_TRAFO = 148.5
    margen_V = V_TRAFO - V_total_sin
    uso_trafo_pct = V_total_sin / V_TRAFO * 100
 
    return {
        "t_total":          round(t_total, 2),
        "I_prom":           round(I_prom, 3),
        "V_celda_sin":      round(V_celda_sin, 4),
        "V_total_sin":      round(V_total_sin, 3),
        "V_celda_mod":      round(V_celda_mod, 4),
        "V_total_mod":      round(V_total_mod, 3),
        "P_celdas_sin":     round(P_celdas_sin, 3),
        "P_total_sin":      round(P_total_sin, 3),
        "P_celdas_mod":     round(P_celdas_mod, 3),
        "P_total_mod":      round(P_total_mod, 3),
        "E_celdas_MWh":     round(E_celdas_MWh, 2),
        "E_total_MWh":      round(E_total_MWh, 2),
        "tn_naoh_celda":    round(tn_naoh_celda, 3),
        "tn_naoh_total":    round(tn_naoh_total, 2),
        "tn_cl2_total":     round(tn_cl2_total, 2),
        "ratio_kwh_naoh":   round(ratio_kwh_naoh, 1),
        "ratio_kwh_cl2":    round(ratio_kwh_cl2, 1),
        "costo_usd":        round(costo_usd, 2),
        "costo_tn_naoh":    round(costo_tn_naoh, 2),
        "costo_tn_cl2":     round(costo_tn_cl2, 2),
        "margen_V":         round(margen_V, 2),
        "uso_trafo_pct":    round(uso_trafo_pct, 1),
        "alerta_trafo":     margen_V < 0,
    }
