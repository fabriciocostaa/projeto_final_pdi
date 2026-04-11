from __future__ import annotations

# vetor [pele, sobrancelhas e olhos]
# peso = [30, 20, 5]
def is_warm(lab_b: list[float], weights: list[float]) -> int:
    # calibração ajustada para ampliar separação entre quente e frio
    warm_b_std = [18.0, 15.0, 8.0]  # Peles douradas/oliva quente
    cool_b_std  = [12.0, 9.0, 5.0]   # pele alta, sobrancelha baixa = frio

    warm_dist = 0.0
    cool_dist = 0.0

    for i in range(3):
        warm_dist += abs(lab_b[i] - warm_b_std[i]) * weights[i]
        cool_dist += abs(lab_b[i] - cool_b_std[i]) * weights[i]

    return 1 if warm_dist <= cool_dist else 0


def is_spr(hsv_s: list[float], weights: list[float]) -> int:
    # primavera mais saturada/viva que outono
    spr_s_std = [45.0, 50.0, 40.0] 
    fal_s_std = [32.0, 38.0, 30.0] 

    spr_dist = 0.0
    fal_dist = 0.0

    for i in range(3):
        spr_dist += abs(hsv_s[i] - spr_s_std[i]) * weights[i]
        fal_dist += abs(hsv_s[i] - fal_s_std[i]) * weights[i]

    return 1 if spr_dist <= fal_dist else 0


def is_smr(hsv_s: list[float], weights: list[float]) -> int:
    # verão menos saturado que inverno
    smr_s_std = [18.0, 22.0, 20.0]
    wnt_s_std = [55.0, 65.0, 50.0]

    adjusted_weights = list(weights)
    adjusted_weights[1] = 0.5

    smr_dist = 0.0
    wnt_dist = 0.0

    for i in range(3):
        smr_dist += abs(hsv_s[i] - smr_s_std[i]) * adjusted_weights[i]
        wnt_dist += abs(hsv_s[i] - wnt_s_std[i]) * adjusted_weights[i]

    return 1 if smr_dist <= wnt_dist else 0
