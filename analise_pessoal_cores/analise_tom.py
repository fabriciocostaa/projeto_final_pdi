from __future__ import annotations

#vetor[pele, sombrancelhas e olhos]
#peso = [30, 20, 5]
def is_warm(lab_b: list[float], weights: list[float]) -> int:
    warm_b_std = [11.6518, 11.71445, 3.6484]
    cool_b_std = [4.64255, 4.86635, 0.18735]

    warm_dist = 0.0
    cool_dist = 0.0

    for i in range(3):
        warm_dist += abs(lab_b[i] - warm_b_std[i]) * weights[i]
        cool_dist += abs(lab_b[i] - cool_b_std[i]) * weights[i]

    return 1 if warm_dist <= cool_dist else 0


def is_spr(hsv_s: list[float], weights: list[float]) -> int:
    spr_s_std = [18.59296, 30.30303, 25.80645]
    fal_s_std = [27.13987, 39.75155, 37.5]

    spr_dist = 0.0
    fal_dist = 0.0

    for i in range(3):
        spr_dist += abs(hsv_s[i] - spr_s_std[i]) * weights[i]
        fal_dist += abs(hsv_s[i] - fal_s_std[i]) * weights[i]

    return 1 if spr_dist <= fal_dist else 0


def is_smr(hsv_s: list[float], weights: list[float]) -> int:
    smr_s_std = [12.5, 21.7195, 24.77064]
    wnt_s_std = [16.73913, 24.8276, 31.3726]

    adjusted_weights = list(weights)
    adjusted_weights[1] = 0.5

    smr_dist = 0.0
    wnt_dist = 0.0

    for i in range(3):
        smr_dist += abs(hsv_s[i] - smr_s_std[i]) * adjusted_weights[i]
        wnt_dist += abs(hsv_s[i] - wnt_s_std[i]) * adjusted_weights[i]

    return 1 if smr_dist <= wnt_dist else 0

#sugestao de calibração !!!!
""" # is_warm — separação mais ampla entre quente e frio
warm_b_std = [14.0, 13.5, 5.0]   # quente: b mais positivo
cool_b_std  = [2.0,  2.5, -1.0]  # frio: b próximo de zero ou negativo

# is_spr — primavera tem saturação MAIS alta que outono (cores vivas)
# seus vetores estão invertidos em relação à teoria da colorimetria
spr_s_std = [28.0, 38.0, 35.0]   # primavera: saturado e vivo
fal_s_std = [18.0, 25.0, 22.0]   # outono: terroso, menos saturado

# is_smr — verão menos saturado que inverno
smr_s_std = [10.0, 18.0, 20.0]
wnt_s_std = [18.0, 28.0, 34.0] """