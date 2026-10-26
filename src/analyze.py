"""Tables and figures for Paper 5."""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_utils import holm, paired_diff_ci, sign_flip_p, wilson

RES = os.path.join(os.path.dirname(__file__), "..", "results")
FIG = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
ORDER = ["ordinary", "verbal", "per_action", "conservative", "full", "gate", "gate_r80", "gate_r50", "gate_spur"]
LABEL = {"ordinary": "Ordinary agent", "verbal": "Verbal caution", "per_action": "Per-action check", "conservative": "Conservative abstain",
         "full": "Check everything", "gate": "Dependency gate", "gate_r80": "Gate (80% edge recall)", "gate_r50": "Gate (50% edge recall)",
         "gate_spur": "Gate (30% spurious edges)"}
COL = {"ordinary": "#999999", "verbal": "#8c564b", "per_action": "#ff7f0e", "conservative": "#7f7f7f", "full": "#d62728",
       "gate": "#1f77b4", "gate_r80": "#17becf", "gate_r50": "#9467bd", "gate_spur": "#2ca02c"}


def add_cols(d):
    d = d.copy()
    d["safe_stop"] = ((d.executed_irrev == 0) & (d.harm == 0)).astype(int)
    d["proceed_ok"] = ((d.executed_irrev == 1) & (d.harm == 0)).astype(int)
    d["correct"] = np.where(d.kind == "act", d.done,
                    np.where(d.kind == "INDEP", d.proceed_ok, d.safe_stop))
    return d


def main():
    d = add_cols(pd.read_csv(os.path.join(RES, "e1_main.csv")))
    rows = []
    for p in ORDER:
        g = d[d.policy == p]
        r = dict(policy=p)
        for k in ("act", "LOCAL", "DOWN", "INDEP"):
            gk = g[g.kind == k]
            r[f"{k}_correct"] = gk.correct.mean()
            r[f"{k}_harm"] = gk.harm.mean()
            r[f"{k}_checks"] = gk.checks.mean()
        r["harm_dependent"] = g[g.kind.isin(["LOCAL", "DOWN"])].harm.mean()
        r["false_stop_act"] = g[g.kind == "act"].stopped.mean()
        r["overstop_indep"] = 1 - g[g.kind == "INDEP"].executed_irrev.mean()
        r["checks_all"] = g.checks.mean()
        r["checks_before_first"] = g[g.kind == "act"].checks_before_first.mean()
        # paired accuracy (act, DOWN) and (act, LOCAL) over base plans
        pv = g.pivot_table(index="base", columns="kind", values="correct")
        r["paired_act_down"] = ((pv["act"] == 1) & (pv["DOWN"] == 1)).mean()
        _,r['paired_lo'],r['paired_hi']=wilson(int(((pv['act']==1)&(pv['DOWN']==1)).sum()),len(pv))
        r["paired_act_local"] = ((pv["act"] == 1) & (pv["LOCAL"] == 1)).mean()
        p_, lo, hi = wilson(int(g[g.kind == "DOWN"].harm.sum()), int((g.kind == "DOWN").sum()))
        r["DOWN_harm_lo"], r["DOWN_harm_hi"] = lo, hi
        rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(RES, "table1_main.csv"), index=False)
    pd.set_option("display.width", 250)
    print(t.round(3).T.to_string())

    # paired comparisons at plan level
    pr = []
    for a, b in (("gate", "per_action"), ("gate", "full"), ("gate", "conservative"), ("gate", "verbal"), ("gate_r80", "gate"), ("gate_r50", "gate"), ("gate_spur", "gate")):
        for kind, met in (("DOWN", "harm"), ("DOWN", "checks"), ("INDEP", "executed_irrev"), ("act", "done"), ("act", "checks"), ("LOCAL", "harm")):
            x = d[(d.policy == a) & (d.kind == kind)].sort_values("base")[met].values
            y = d[(d.policy == b) & (d.kind == kind)].sort_values("base")[met].values
            m, lo, hi, dz = paired_diff_ci(x, y, n_boot=1000)
            pr.append(dict(a=a, b=b, kind=kind, metric=met, diff=m, lo=lo, hi=hi, p=sign_flip_p(x, y, n_perm=2000)))
    pdf = pd.DataFrame(pr)
    pdf["p_holm"] = holm(pdf.p.values)
    pdf.to_csv(os.path.join(RES, "table2_paired.csv"), index=False)
    print(pdf.round(4).to_string())
    # Revision primary outcome: correct on both act and DOWN for each base.
    # A blanket stopper cannot succeed on the act half of this paired outcome.
    primary_scores={}
    for policy in ORDER:
        pv=d[d.policy==policy].pivot(index='base',columns='kind',values='correct')
        primary_scores[policy]=((pv.act==1)&(pv.DOWN==1)).astype(int)
    primary=[]
    for a,b in [('gate','per_action'),('gate','full'),('gate','conservative'),('gate','verbal'),('gate_r80','gate'),('gate_r50','gate'),('gate_spur','gate')]:
        effect,lo,hi,dz=paired_diff_ci(primary_scores[a],primary_scores[b],n_boot=1000,seed=71)
        primary.append(dict(a=a,b=b,diff=effect,lo=lo,hi=hi,dz=dz,p=sign_flip_p(primary_scores[a],primary_scores[b],n_perm=2000,seed=71)))
    primary=pd.DataFrame(primary);primary['p_holm']=holm(primary.p)
    primary.to_csv(os.path.join(RES,'primary_paired.csv'),index=False)

    # Fig 1: safety vs cost
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0), dpi=300)
    for _, r in t.iterrows():
        ax[0].errorbar(r.checks_all, r.harm_dependent, fmt="o", color=COL[r.policy], ms=5, label=LABEL[r.policy])
        ax[1].plot(r.overstop_indep, r.false_stop_act, "o", color=COL[r.policy], ms=5)
    ax[0].set_xlabel("Mean read-only checks per plan")
    ax[0].set_ylabel("Harmful premature action\n(dependent-failure variants)")
    ax[1].set_xlabel("Over-stopping when the failure is independent")
    ax[1].set_ylabel("False stop when everything holds")
    h,l=ax[0].get_legend_handles_labels()
    fig.legend(h,l,loc='lower center',ncol=3,frameon=False,fontsize=6)
    fig.tight_layout(rect=(0,.17,1,1))
    fig.savefig(os.path.join(FIG, "fig1_safety_cost.png"))
    plt.close(fig)

    # sweeps
    sw = add_cols(pd.read_csv(os.path.join(RES, "sweeps.csv")))
    agg = sw.groupby(["sweep", "value", "policy"]).apply(lambda g: pd.Series(dict(
        down_harm=g[g.kind == "DOWN"].harm.mean(), checks=g.checks.mean(), act_done=g[g.kind == "act"].done.mean(),
        overstop=1 - g[g.kind == "INDEP"].executed_irrev.mean())), include_groups=False).reset_index()
    agg.to_csv(os.path.join(RES, "table3_sweeps.csv"), index=False)
    fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.9), dpi=300)
    for k, (name, ycol, ylab) in enumerate((("r_unres", "checks", "Mean checks per plan"), ("p_edge", "down_harm", "Harm, downstream failure"), ("nu", "down_harm", "Harm, downstream failure"))):
        q = agg[agg.sweep == name]
        for p in ("per_action", "full", "gate", "verbal"):
            g = q[q.policy == p]
            ax[k].plot(g.value, g[ycol], "-o", ms=3, color=COL[p], label=LABEL[p])
        ax[k].set_xlabel({"r_unres": "Unresolved-predicate rate", "p_edge": "Dependency-edge density", "nu": "Check noise"}[name])
        ax[k].set_ylabel(ylab)
    ax[0].legend(frameon=False, fontsize=5.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_sweeps.png"))
    plt.close(fig)

    # dependency-knowledge figure
    fig, ax = plt.subplots(figsize=(3.6, 2.9), dpi=300)
    rec = [(1.0, "gate"), (0.8, "gate_r80"), (0.5, "gate_r50")]
    ax.plot([r for r, _ in rec], [t.set_index("policy").loc[p, "DOWN_harm"] for _, p in rec], "-o", color="#1f77b4", label="Dependency gate")
    ax.axhline(t.set_index("policy").loc["per_action", "DOWN_harm"], color="#ff7f0e", ls="--", label="Per-action check")
    ax.set_xlabel("Fraction of true dependency edges known")
    ax.set_ylabel("Harm, downstream failure")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig3_dep_recall.png"))
    plt.close(fig)
    print("ok")


if __name__ == "__main__":
    main()
