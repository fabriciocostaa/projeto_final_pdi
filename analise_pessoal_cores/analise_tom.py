from __future__ import annotations

# vetor [pele, sobrancelhas e olhos]
# peso = [30, 20, 5]
def is_warm(lab_b: list[float], weights: list[float]) -> int:
    # calibração ajustada para ampliar separação entre quente e frio
    warm_b_std = [14.0, 13.5, 5.0]
    cool_b_std = [2.0, 2.5, -1.0]

    warm_dist = 0.0
    cool_dist = 0.0

    for i in range(3):
        warm_dist += abs(lab_b[i] - warm_b_std[i]) * weights[i]
        cool_dist += abs(lab_b[i] - cool_b_std[i]) * weights[i]

    return 1 if warm_dist <= cool_dist else 0


def is_spr(hsv_s: list[float], weights: list[float]) -> int:
    # primavera mais saturada/viva que outono
    spr_s_std = [28.0, 38.0, 35.0]
    fal_s_std = [18.0, 25.0, 22.0]

    spr_dist = 0.0
    fal_dist = 0.0

    for i in range(3):
        spr_dist += abs(hsv_s[i] - spr_s_std[i]) * weights[i]
        fal_dist += abs(hsv_s[i] - fal_s_std[i]) * weights[i]

    return 1 if spr_dist <= fal_dist else 0


def is_smr(hsv_s: list[float], weights: list[float]) -> int:
    # verão menos saturado que inverno
    smr_s_std = [10.0, 18.0, 20.0]
    wnt_s_std = [18.0, 28.0, 34.0]

    adjusted_weights = list(weights)
    adjusted_weights[1] = 0.5

    smr_dist = 0.0
    wnt_dist = 0.0

    for i in range(3):
        smr_dist += abs(hsv_s[i] - smr_s_std[i]) * adjusted_weights[i]
        wnt_dist += abs(hsv_s[i] - wnt_s_std[i]) * adjusted_weights[i]

    return 1 if smr_dist <= wnt_dist else 0
