"""Paper 5 experiments."""
from __future__ import annotations

import argparse
import dataclasses
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from sim import POLICIES, Params, evaluate

RES = os.path.join(os.path.dirname(__file__), "..", "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    base = Params()
    pols = POLICIES + ["gate_r80", "gate_r50", "gate_spur"]

    def ev(P, n, seed, name_map=True):
        rows = []
        # policies with imperfect dependency knowledge are run with modified params
        rows += evaluate(P, n, seed, POLICIES)
        for tag, pp in (("gate_r80", dataclasses.replace(P, dep_recall=0.8)),
                        ("gate_r50", dataclasses.replace(P, dep_recall=0.5)),
                        ("gate_spur", dataclasses.replace(P, dep_spurious=0.3))):
            rr = evaluate(pp, n, seed, ["gate"])
            for r in rr:
                r["policy"] = tag
            rows += rr
        return rows

    pd.DataFrame(ev(base, a.n, 7)).to_csv(os.path.join(RES, "e1_main.csv"), index=False)
    print('Main complete',flush=True)
    extracted=evaluate(base,max(a.n//2,600),23,['gate','per_action','full','gate_text','gate_shared'])
    pd.DataFrame(extracted).to_csv(os.path.join(RES,'dependency_extraction.csv'),index=False)
    print('Fresh dependency extraction complete',flush=True)

    sweeps = {"r_unres": (0.25, 0.5, 0.75, 1.0), "p_edge": (0.15, 0.3, 0.45, 0.7), "nu": (0.0, 0.03, 0.1, 0.2),
              "p_irrev": (0.2, 0.35, 0.6), "p_local_exec": (0.0, 0.5, 1.0), "q_habit": (0.0, 0.25, 0.5, 0.75)}
    out = []
    for name, vals in sweeps.items():
        for v in vals:
            P = dataclasses.replace(base, **{name: v})
            rows = evaluate(P, max(a.n // 3, 600), 11, POLICIES)
            df = pd.DataFrame(rows)
            df["sweep"], df["value"] = name, v
            out.append(df)
        print('Sweep',name,'complete',flush=True)
    long_plans = dataclasses.replace(base, n_steps=(6, 8, 10), pool_extra=3)
    df = pd.DataFrame(evaluate(long_plans, max(a.n // 3, 600), 13, POLICIES))
    df["sweep"], df["value"] = "long_plans", 1
    out.append(df)
    pd.concat(out).to_csv(os.path.join(RES, "sweeps.csv"), index=False)
    print("done")


if __name__ == "__main__":
    main()
