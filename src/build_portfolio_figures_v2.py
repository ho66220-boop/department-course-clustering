# -*- coding: utf-8 -*-
"""Portfolio v2 figures: readability-only re-rendering of the report figures.

This script does NOT touch any analysis logic. It imports the existing
computation functions (data loading, IDF weighting, linkage, co-occurrence,
consensus clustering) from build_idf_weighted_analysis and
build_card_sorting_analysis and reuses them verbatim, so the linkage matrices,
distance matrices and cluster memberships are byte-for-byte the same as the
committed analysis. Only cosmetic plotting parameters change (figsize, font
sizes, rotation, annotations, cluster-name labels, boundary lines).

Outputs go to reports/final/figures_v2/ so the original
results/figures/keep_for_report/ and reports/latex_progress/ figures are left
untouched (submitted report preserved).

After rendering, each clustering figure's membership is compared against the
committed result CSVs and the verdict is printed.

Run:
    python src/build_portfolio_figures_v2.py
"""
from __future__ import annotations

import sys
import pathlib

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy.cluster.hierarchy import dendrogram, fcluster, leaves_list, linkage
from scipy.spatial.distance import pdist

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_idf_weighted_analysis as bi          # noqa: E402  reuse computation
import build_card_sorting_analysis as bc          # noqa: E402  reuse computation

BASE = pathlib.Path(__file__).resolve().parents[1]
OUT = BASE / "reports" / "final" / "figures_v2"
TABLES = BASE / "results" / "tables" / "keep_for_report"


def setup_style() -> None:
    matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def partition(name_to_label: dict) -> frozenset:
    """A clustering as a label-independent set of member-name groups."""
    groups: dict = {}
    for name, lab in name_to_label.items():
        groups.setdefault(lab, set()).add(name)
    return frozenset(frozenset(g) for g in groups.values())


def cluster_name(members: set) -> str:
    """Human label for a member set, disambiguating the blocks across all 3 figures
    (IDF k=4, IDF core sub-clusters k=3, expert consensus k=4)."""
    m = members
    if "의예과" in m and len(m) > 10:                       # IDF k=4 STEM-보건 대군집
        return f"STEM-보건 ({len(m)})"
    if "기계공학과" in m and "수학과" in m and len(m) >= 12:  # consensus 공학-자연 13개
        return f"공학-자연 ({len(m)})"
    if "경영학과" in m and "경제학과" in m and len(m) <= 3:
        return "경영·경제"
    if "국어국문학과" in m and "디자인학과" in m:            # IDF k=4
        return "국어국문·디자인"
    if "건축학과" in m and "디자인학과" in m:                # consensus 경계 블록
        return "건축·디자인"
    if "심리학과" in m and "사회학과" in m:
        return "사회·인문"
    if "의예과" in m:                                        # 의약-보건 (sub-cluster/consensus)
        return "의약-보건"
    if "산업공학과" in m and "수학과" in m:                  # 코어 하위군집 정량·응용
        return "정량·응용"
    if "기계공학과" in m and "화학과" in m:                  # 코어 하위군집 공학-화학
        return "공학-화학"
    return "/".join(sorted(m))[:18]


def annotate_clusters(ax, z, labels, names, leaf_order, thr) -> None:
    """Place cluster-name text above each colored block, using leaf x-positions."""
    pos = {orig: i for i, orig in enumerate(leaf_order)}      # orig idx -> display slot
    ymax = z[:, 2].max()
    for lab in sorted(set(labels)):
        members_idx = [i for i in range(len(names)) if labels[i] == lab]
        xs = [5 + 10 * pos[i] for i in members_idx]
        xc = float(np.mean(xs))
        nm = cluster_name({names[i] for i in members_idx})
        ax.text(xc, thr + 0.02 * ymax, nm, ha="center", va="bottom",
                fontsize=12, fontweight="bold", color="#222222",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#888888", alpha=0.85))


# --------------------------------------------------------------------------- Fig.1
def fig1_idf_dendrogram() -> frozenset:
    matrix, course_columns, name_col = bi.load()
    x = matrix[course_columns].to_numpy(dtype=float)
    idf = bi.idf_weights(x)
    xf = bi.weighted_matrix(x, idf, bi.PRIMARY_ALPHA)
    labels, _sil, z = bi.cluster(xf, bi.LINKAGE_METHOD, bi.N_CLUSTERS)
    names = list(matrix[name_col])
    lab_disp = [f"{i} {n}" for i, n in zip(matrix["department_id"], names)]
    thr = (z[-3, 2] + z[-4, 2]) / 2.0                         # height giving k=4 clusters

    fig, ax = plt.subplots(figsize=(15, 8))
    dd = dendrogram(z, labels=lab_disp, leaf_rotation=70, leaf_font_size=12,
                    color_threshold=thr, above_threshold_color="#9e9e9e", ax=ax)
    ax.axhline(thr, ls="--", lw=1.0, color="#666666", alpha=0.7)
    ax.text(ax.get_xlim()[1], thr, "  k=4 cut", va="center", fontsize=10, color="#666666")
    annotate_clusters(ax, z, labels, names, dd["leaves"], thr)
    ax.set_title(f"IDF 가중 hierarchical 군집화 ({bi.LINKAGE_METHOD} linkage, cosine), k=4",
                 fontsize=15, pad=12)
    ax.set_ylabel("Cosine distance", fontsize=13)
    ax.tick_params(axis="y", labelsize=11)
    plt.tight_layout()
    plt.savefig(OUT / "idf_dendrogram.png", dpi=200)
    plt.close()
    return partition(dict(zip(names, labels)))


# --------------------------------------------------------------------------- Fig.2
def fig2_core_subdendrogram() -> frozenset:
    matrix, course_columns, name_col = bi.load()
    x = matrix[course_columns].to_numpy(dtype=float)
    idf = bi.idf_weights(x)
    xf = bi.weighted_matrix(x, idf, bi.PRIMARY_ALPHA)
    labels, _sil, _z = bi.cluster(xf, bi.LINKAGE_METHOD, bi.N_CLUSTERS)

    core_id = pd.Series(labels).value_counts().idxmax()       # identical to subcluster_core
    mask = labels == core_id
    core_names = matrix[name_col].to_numpy()[mask]
    core_ids = matrix["department_id"].to_numpy()[mask]
    xc = matrix[course_columns].to_numpy(dtype=float)[mask]
    present = xc.sum(axis=0) > 0
    xc = xc[:, present]
    local_idf = np.log(xc.shape[0] / xc.sum(axis=0))
    weighted = xc * local_idf
    z = linkage(pdist(weighted, metric="cosine"), method=bi.SUB_LINKAGE)
    sub_labels = fcluster(z, t=bi.CORE_SUBCLUSTERS_K, criterion="maxclust")
    thr = (z[-2, 2] + z[-3, 2]) / 2.0                         # height giving k=3 sub-clusters

    lab_disp = [f"{i} {n}" for i, n in zip(core_ids, core_names)]
    fig, ax = plt.subplots(figsize=(13, 7))
    dd = dendrogram(z, labels=lab_disp, leaf_rotation=65, leaf_font_size=12,
                    color_threshold=thr, above_threshold_color="#9e9e9e", ax=ax)
    annotate_clusters(ax, z, sub_labels, list(core_names), dd["leaves"], thr)
    ax.set_title("STEM-보건 코어의 하위 군집화 (코어 내 IDF 재가중, complete linkage), k=3",
                 fontsize=15, pad=12)
    ax.set_ylabel("Cosine distance", fontsize=13)
    ax.tick_params(axis="y", labelsize=11)
    plt.tight_layout()
    plt.savefig(OUT / "idf_core_subdendrogram.png", dpi=200)
    plt.close()
    return partition(dict(zip(core_names, sub_labels)))


# --------------------------------------------------------------------------- Fig.3
def fig3_cooccurrence_heatmap() -> tuple[frozenset, np.ndarray, list]:
    path = bc.find_input()
    responses = bc.read_responses(path)
    names = list(responses.index)
    co = bc.co_occurrence(responses)
    z = bc.consensus_linkage(co)
    order = list(leaves_list(z))
    clusters_k4 = fcluster(z, t=bc.K_PRIMARY, criterion="maxclust")

    ordered = co[np.ix_(order, order)]
    labels = [names[i] for i in order]
    ordered_clusters = [clusters_k4[i] for i in order]

    fig, ax = plt.subplots(figsize=(12.5, 11))
    im = ax.imshow(ordered, cmap="magma", vmin=0, vmax=1)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("동시분류율 (co-classification rate)", fontsize=12)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=75, fontsize=10, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    boundaries = [i for i in range(1, len(order)) if ordered_clusters[i] != ordered_clusters[i - 1]]
    for b in boundaries:
        ax.axhline(b - 0.5, color="#00e5ff", lw=2.0)
        ax.axvline(b - 0.5, color="#00e5ff", lw=2.0)
    # cluster-name labels centered above each diagonal block, staggered to avoid overlap
    bounds = [0] + boundaries + [len(order)]
    for bi_, (s, e) in enumerate(zip(bounds[:-1], bounds[1:])):
        nm = cluster_name({labels[i] for i in range(s, e)})
        y = -0.9 if bi_ % 2 == 0 else -2.1
        ax.text((s + e - 1) / 2, y, nm, ha="center", va="bottom",
                fontsize=11, fontweight="bold", color="#222222")
    ax.set_ylim(len(order) - 0.5, -3.0)                       # headroom for staggered labels
    ax.set_title("전문가 동시분류 행렬 (14명, consensus 군집 순서)", fontsize=15, pad=30)
    plt.tight_layout()
    plt.savefig(OUT / "cardsort_cooccurrence_heatmap.png", dpi=200)
    plt.close()
    return partition(dict(zip(names, clusters_k4))), co, names


# --------------------------------------------------------------------------- Fig.4
def fig4_ambiguity_bars() -> None:
    df = pd.read_csv(TABLES / "cardsort_department_ambiguity.csv", encoding="utf-8-sig")
    df = df.sort_values("max_co_classification", ascending=True).reset_index(drop=True)
    departments = df["department"].tolist()
    values = df["max_co_classification"].tolist()
    partners = df["closest_partner"].tolist()
    colors = ["#b2182b" if v < 0.5 else "#9e9e9e" for v in values]

    fig, ax = plt.subplots(figsize=(9.5, 10))
    positions = range(len(df))
    ax.barh(positions, values, color=colors)
    ax.set_yticks(positions)
    ax.set_yticklabels(departments, fontsize=10.5)
    ax.invert_yaxis()
    for i, (value, partner) in enumerate(zip(values, partners)):
        ax.text(value + 0.012, i, f"{partner} ({value:.2f})", va="center", fontsize=9)
    ax.axvline(0.5, ls=":", color="gray", lw=1.0, alpha=0.8)
    ax.set_xlim(0, 1.3)
    ax.set_xlabel("최대 동시분류율 (전문가 합의 강도)", fontsize=12)
    ax.set_title("학과별 모호성: 어떤 군집에도 합의되지 않는 경계 사례", fontsize=14, pad=10)
    ax.legend(handles=[Patch(color="#b2182b", label="합의 모호 (< 0.5)"),
                       Patch(color="#9e9e9e", label="견고하게 묶임 (≥ 0.5)")],
              loc="lower right", fontsize=10)
    plt.tight_layout()
    plt.savefig(OUT / "cardsort_department_ambiguity_bars.png", dpi=200)
    plt.close()


# --------------------------------------------------------------------------- Fig.5
def fig5_agreement_bars() -> None:
    agr = pd.read_csv(TABLES / "cardsort_agreement.csv", encoding="utf-8-sig")
    ci = pd.read_csv(TABLES / "cardsort_agreement_ci.csv", encoding="utf-8-sig").set_index("k")
    ks = agr["k"].tolist()
    c = ci.loc[ks]
    xpos = np.arange(len(ks))
    w = 0.38
    yerr_idf = np.vstack([agr["ari_vs_idf"].to_numpy() - c["ari_idf_low"].to_numpy(),
                          c["ari_idf_high"].to_numpy() - agr["ari_vs_idf"].to_numpy()])
    yerr_bin = np.vstack([agr["ari_vs_binary"].to_numpy() - c["ari_binary_low"].to_numpy(),
                          c["ari_binary_high"].to_numpy() - agr["ari_vs_binary"].to_numpy()])
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.bar(xpos - w / 2, agr["ari_vs_idf"], w, label="vs IDF (main)", color="#2c7fb8",
           yerr=yerr_idf, capsize=4, ecolor="#08519c")
    ax.bar(xpos + w / 2, agr["ari_vs_binary"], w, label="vs binary (baseline)", color="#bdbdbd",
           yerr=yerr_bin, capsize=4, ecolor="#636363")
    for xi, (vi, vb) in enumerate(zip(agr["ari_vs_idf"], agr["ari_vs_binary"])):
        ax.text(xi - w / 2, vi + 0.015, f"{vi:.2f}", ha="center", fontsize=10)
        ax.text(xi + w / 2, vb + 0.015, f"{vb:.2f}", ha="center", fontsize=10)
    ax.set_xticks(xpos)
    ax.set_xticklabels([f"k={k}" for k in ks], fontsize=12)
    ax.set_ylabel("Adjusted Rand Index (전문가 합의와의 일치도)", fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_title("알고리즘 군집 vs 전문가 합의 ARI (오차막대: rater 부트스트랩 95% CI, B=1000)",
                 fontsize=13, pad=10)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(OUT / "cardsort_agreement_bars.png", dpi=200)
    plt.close()


# --------------------------------------------------------------------------- Fig.6
def fig6_scatter(co: np.ndarray, names: list) -> None:
    cos = bc.aligned_idf_cosine(names)
    iu = np.triu_indices(len(names), 1)
    xs, ys = cos[iu], co[iu]
    r = np.corrcoef(xs, ys)[0, 1]

    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.scatter(xs, ys, s=26, alpha=0.5, color="#2c7fb8")
    ax.plot([0, 1], [0, 1], "--", color="gray", lw=1)
    # annotate the representative disagreement pairs from report Table III (1 Type 1 + 2 Type 2).
    # Pairs are matched by name (order-agnostic); coordinates come from the committed CSV.
    dis = pd.read_csv(TABLES / "cardsort_disagreement_pairs.csv", encoding="utf-8-sig")
    table3 = [
        (("신소재공학과", "생명과학과"), (10, -14)),    # Type 1: 내부 O / 외부 X
        (("조선해양공학과", "자동차공학과"), (8, 8)),    # Type 2: 내부 X / 외부 O
        (("국어국문학과", "사학과"), (-12, 10)),         # Type 2
    ]
    for (a, b), off in table3:
        match = dis[((dis.A == a) & (dis.B == b)) | ((dis.A == b) & (dis.B == a))]
        if match.empty:
            raise ValueError(f"Table III pair not found in CSV: {a}-{b}")
        pr = match.iloc[0]
        xa, ya = float(pr["idf_cosine"]), float(pr["co_classification"])
        ax.annotate(f"{pr['A']}-{pr['B']}", (xa, ya), fontsize=9,
                    xytext=off, textcoords="offset points", color="#b2182b",
                    arrowprops=dict(arrowstyle="-", color="#b2182b", lw=0.6))
    ax.set_xlabel("IDF cosine similarity (알고리즘)", fontsize=12)
    ax.set_ylabel("전문가 동시분류율", fontsize=12)
    ax.set_title(f"학과 쌍(n=300): 알고리즘 vs 전문가  (r = {r:.2f})", fontsize=14, pad=10)
    plt.tight_layout()
    plt.savefig(OUT / "cardsort_cooccur_vs_idf_scatter.png", dpi=200)
    plt.close()


# --------------------------------------------------------------------------- verify
def csv_partition_idf() -> frozenset:
    df = pd.read_csv(TABLES / "idf_cluster_assignments.csv", encoding="utf-8-sig")
    return partition(dict(zip(df["department_name"], df["cluster_id"])))


def csv_partition_subclusters() -> frozenset:
    df = pd.read_csv(TABLES / "core_subclusters.csv", encoding="utf-8-sig")
    groups = []
    for _, row in df.iterrows():
        groups.append(frozenset(d.strip() for d in str(row["departments"]).split(";")))
    return frozenset(groups)


def csv_partition_consensus() -> frozenset:
    df = pd.read_csv(TABLES / "cardsort_consensus_assignments.csv", encoding="utf-8-sig")
    return partition(dict(zip(df["department"], df["consensus_k4"])))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    setup_style()

    p1 = fig1_idf_dendrogram()
    p2 = fig2_core_subdendrogram()
    p3, co, names = fig3_cooccurrence_heatmap()
    fig4_ambiguity_bars()
    fig5_agreement_bars()
    fig6_scatter(co, names)

    checks = [
        ("Fig.1 IDF k=4 군집",      p1, csv_partition_idf()),
        ("Fig.2 코어 하위군집 k=3", p2, csv_partition_subclusters()),
        ("Fig.3 consensus k=4",     p3, csv_partition_consensus()),
    ]
    print("=== 군집 멤버십 원본 동일성 검증 (재생성 partition vs committed CSV) ===")
    all_ok = True
    for label, recomputed, reference in checks:
        ok = recomputed == reference
        all_ok &= ok
        print(f"  [{'OK' if ok else 'MISMATCH'}] {label}: groups={len(recomputed)} "
              f"sizes={sorted(len(g) for g in recomputed)}")
        if not ok:
            print(f"        recomputed: {sorted(sorted(g) for g in recomputed)}")
            print(f"        reference : {sorted(sorted(g) for g in reference)}")
    print(f"\nfigures -> {OUT.relative_to(BASE)}/  (6 files)")
    print("ALL MEMBERSHIPS IDENTICAL" if all_ok else "!! MEMBERSHIP CHANGED — STOP AND INVESTIGATE")


if __name__ == "__main__":
    main()
