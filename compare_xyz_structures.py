# Re-run the analysis using only pandas for tabular output and also export CSVs.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------- Helpers --------------------


def parse_xyz(filename):
    atoms = []
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 4:
                elem = parts[0]
                xyz = np.array(
                    [float(parts[1]), float(parts[2]), float(parts[3])], dtype=float
                )
                atoms.append((elem, xyz))
    return atoms


masses = {"H": 1.00784, "C": 12.0107, "N": 14.0067, "O": 15.999}


def to_zero_based(spec):
    idx = []
    for token in spec.replace(" ", "").split(","):
        if not token:
            continue
        if "-" in token:
            a, b = token.split("-")
            a, b = int(a), int(b)
            idx.extend(range(a - 1, b))  # 1-based -> 0-based inclusive
        else:
            idx.append(int(token) - 1)
    return sorted(set(idx))


def centroid(positions):
    return positions.mean(axis=0)


def com(positions, elements):
    w = np.array([masses[e] for e in elements], dtype=float)
    return (w[:, None] * positions).sum(axis=0) / w.sum()


def fit_plane_pca(positions):
    c = centroid(positions)
    X = positions - c
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    a1, a2, n = Vt[0], Vt[1], Vt[2]
    if np.dot(np.cross(a1, a2), n) < 0:
        a2 = -a2
    a1 = a1 / np.linalg.norm(a1)
    a2 = a2 / np.linalg.norm(a2)
    n = n / np.linalg.norm(n)
    return c, n, a1, a2


def angle_between(u, v):
    u = u / np.linalg.norm(u)
    v = v / np.linalg.norm(v)
    c = np.clip(np.dot(u, v), -1.0, 1.0)
    return np.degrees(np.arccos(c))


def signed_angle_in_plane(u, v, n_ref):
    n_ref = n_ref / np.linalg.norm(n_ref)
    u = u - np.dot(u, n_ref) * n_ref
    v = v - np.dot(v, n_ref) * n_ref
    if np.linalg.norm(u) < 1e-12 or np.linalg.norm(v) < 1e-12:
        return 0.0
    u = u / np.linalg.norm(u)
    v = v / np.linalg.norm(v)
    x = np.cross(u, v)
    s = np.clip(np.dot(x, n_ref), -1.0, 1.0)
    c = np.clip(np.dot(u, v), -1.0, 1.0)
    return np.degrees(np.arctan2(s, c))


def perp_and_slip(r_other, r_mid, n_mid, a1_mid, a2_mid):
    d = r_other - r_mid
    d_perp_signed = np.dot(d, n_mid)
    d_perp_abs = abs(d_perp_signed)
    s_vec = d - d_perp_signed * n_mid
    sx = np.dot(s_vec, a1_mid)
    sy = np.dot(s_vec, a2_mid)
    s_mag = np.sqrt(sx**2 + sy**2)
    return d_perp_signed, d_perp_abs, s_mag, sx, sy


def split_ep(struct):
    E = np.array([e for e, _ in struct], dtype=object)
    P = np.vstack([p for _, p in struct])
    return E, P


# -------------------- Load files --------------------

unattached = parse_xyz("./Trimer_Starting_Materials_optd.xyz")
sandwich = parse_xyz("./Trimer_Tethered_gs_optd.xyz")
zigzag = parse_xyz("./Trimer_Tethered_Linear_optd.xyz")

E_un, P_un = split_ep(unattached)
E_sa, P_sa = split_ep(sandwich)
E_zi, P_zi = split_ep(zigzag)

# -------------------- User-specified indices --------------------
UA_top_spec = "86-127,130-131,133-135,154-183"
UA_middle_spec = "43-85,129,136-153,184-201"
UA_bottom_spec = "1-42,128,132,202-237"

SA_top_spec = "86-129,133-146,153,222-236"
SA_middle_spec = "43-85,131,147-149,260-292"
SA_bottom_spec = "1-42,130,132,150-152,170-184,201-212"

ZI_top_spec = "85-127,130,198-200,202,215-225,257-259,263,276-289"
ZI_middle_spec = "43-84,129,131,148-162,195-197,201,203-205,249-256"
ZI_bottom_spec = "1-42,128,132-147,260-262,264-275,290-292"

IDX = {
    "unattached": {
        "E": E_un,
        "P": P_un,
        "top": to_zero_based(UA_top_spec),
        "middle": to_zero_based(UA_middle_spec),
        "bottom": to_zero_based(UA_bottom_spec),
    },
    "sandwich": {
        "E": E_sa,
        "P": P_sa,
        "top": to_zero_based(SA_top_spec),
        "middle": to_zero_based(SA_middle_spec),
        "bottom": to_zero_based(SA_bottom_spec),
    },
    "zigzag": {
        "E": E_zi,
        "P": P_zi,
        "top": to_zero_based(ZI_top_spec),
        "middle": to_zero_based(ZI_middle_spec),
        "bottom": to_zero_based(ZI_bottom_spec),
    },
}

# -------------------- Analysis --------------------


def analyze(name, data):
    E, P = data["E"], data["P"]
    it, im, ib = data["top"], data["middle"], data["bottom"]
    Pt, Et = P[it], E[it]
    Pm, Em = P[im], E[im]
    Pb, Eb = P[ib], E[ib]

    # Plane fit on centroids of core atoms (unweighted)
    ct, nt, a1t, a2t = fit_plane_pca(Pt)
    cm, nm, a1m, a2m = fit_plane_pca(Pm)
    cb, nb, a1b, a2b = fit_plane_pca(Pb)

    # Normal orientation consistency
    if np.dot(nt, nm) < 0:
        nt = -nt
    if np.dot(nb, nm) < 0:
        nb = -nb

    # Tilts and twists
    tilt_top = angle_between(nt, nm)
    tilt_bottom = angle_between(nb, nm)
    twist_top = signed_angle_in_plane(a1m, a1t, nm)
    twist_bottom = signed_angle_in_plane(a1m, a1b, nm)

    # Perpendicular distances + slip (use centroids)
    dtop_s, dtop, stop, sxt, syt = perp_and_slip(ct, cm, nm, a1m, a2m)
    dbot_s, dbot, sbot, sxb, syb = perp_and_slip(cb, cm, nm, a1m, a2m)

    # COM–COM summary (mass-weighted)
    cmt = com(Pt, Et)
    cmm = com(Pm, Em)
    cmb = com(Pb, Eb)
    d_tm = np.linalg.norm(cmt - cmm)
    d_bm = np.linalg.norm(cmb - cmm)
    d_tb = np.linalg.norm(cmt - cmb)
    v_tm = cmt - cmm
    v_bm = cmb - cmm
    central_angle = np.degrees(
        np.arccos(
            np.clip(
                np.dot(v_tm, v_bm) / (np.linalg.norm(v_tm) * np.linalg.norm(v_bm)),
                -1.0,
                1.0,
            )
        )
    )

    return {
        "d_perp_top": dtop,
        "d_perp_bottom": dbot,
        "slip_top": stop,
        "slip_top_x": sxt,
        "slip_top_y": syt,
        "slip_bottom": sbot,
        "slip_bottom_x": sxb,
        "slip_bottom_y": syb,
        "tilt_top": tilt_top,
        "tilt_bottom": tilt_bottom,
        "twist_top": twist_top,
        "twist_bottom": twist_bottom,
        "COMdist_top_middle": d_tm,
        "COMdist_bottom_middle": d_bm,
        "COMdist_top_bottom": d_tb,
        "central_angle_COMs": central_angle,
    }


results = {name: analyze(name, data) for name, data in IDX.items()}

# -------------------- Tables with pandas only --------------------

plane_cols = [
    "d_perp_top",
    "d_perp_bottom",
    "slip_top",
    "slip_bottom",
    "slip_top_x",
    "slip_top_y",
    "slip_bottom_x",
    "slip_bottom_y",
    "tilt_top",
    "tilt_bottom",
    "twist_top",
    "twist_bottom",
]
com_cols = [
    "COMdist_top_middle",
    "COMdist_bottom_middle",
    "COMdist_top_bottom",
    "central_angle_COMs",
]

plane_df = pd.DataFrame(results).T[plane_cols]
com_df = pd.DataFrame(results).T[com_cols]

# Deltas vs unattached
delta_df = plane_df.subtract(plane_df.loc["unattached"], axis="columns").loc[
    ["sandwich", "zigzag"]
]

# Round for readability
plane_df_r = plane_df.copy().round(
    {
        "d_perp_top": 3,
        "d_perp_bottom": 3,
        "slip_top": 3,
        "slip_bottom": 3,
        "slip_top_x": 3,
        "slip_top_y": 3,
        "slip_bottom_x": 3,
        "slip_bottom_y": 3,
        "tilt_top": 1,
        "tilt_bottom": 1,
        "twist_top": 1,
        "twist_bottom": 1,
    }
)
com_df_r = com_df.copy().round(
    {
        "COMdist_top_middle": 3,
        "COMdist_bottom_middle": 3,
        "COMdist_top_bottom": 3,
        "central_angle_COMs": 1,
    }
)
delta_df_r = delta_df.copy().round(
    {
        "d_perp_top": 3,
        "d_perp_bottom": 3,
        "slip_top": 3,
        "slip_bottom": 3,
        "slip_top_x": 3,
        "slip_top_y": 3,
        "slip_bottom_x": 3,
        "slip_bottom_y": 3,
        "tilt_top": 1,
        "tilt_bottom": 1,
        "twist_top": 1,
        "twist_bottom": 1,
    }
)

print("\nPlane-based metrics (centroid planes; middle as reference)\n")
print(plane_df_r.to_string())
print("\nCOM–COM summary (mass-weighted)\n")
print(com_df_r.to_string())
print("\nΔ (Sandwich/Zigzag) relative to Unattached — Plane metrics\n")
print(delta_df_r.to_string())

# -------------------- Export CSVs --------------------
plane_csv = "./plane_metrics.csv"
com_csv = "./com_summary.csv"
delta_csv = "./deltas_vs_unattached.csv"
all_csv = "./all_metrics.csv"

plane_df.to_csv(plane_csv, index=True)
com_df.to_csv(com_csv, index=True)
delta_df.to_csv(delta_csv, index=True)
pd.concat([plane_df, com_df], axis=1).to_csv(all_csv, index=True)

plane_csv, com_csv, delta_csv, all_csv
print(f"\nExported CSVs:\n{plane_csv}\n{com_csv}\n{delta_csv}\n{all_csv}\n")
