import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
from sim import KINDS, Params, evaluate, make_base, variant


def test_variants_have_exactly_one_false_predicate():
    P = Params()
    rng = random.Random(0)
    for _ in range(50):
        b = make_base(rng, P)
        for k in KINDS:
            v = variant(b, k, random.Random(1))
            assert sum(not x for x in v.truth.values()) == (0 if k == "act" else 1)


def test_full_check_with_zero_noise_never_harmed():
    P = Params(nu=0.0)
    df = pd.DataFrame(evaluate(P, 200, 1, ["full"]))
    assert df.harm.sum() == 0


def test_gate_zero_noise_no_harm_on_dependent_failures():
    P = Params(nu=0.0)
    df = pd.DataFrame(evaluate(P, 300, 2, ["gate"]))
    assert df[df.kind.isin(["LOCAL", "DOWN"])].harm.sum() == 0


def test_per_action_misses_downstream_failures():
    P = Params(nu=0.0, q_habit=0.0)
    df = pd.DataFrame(evaluate(P, 400, 3, ["per_action"]))
    assert df[df.kind == "DOWN"].harm.mean() > 0.5


def test_conservative_is_safe_but_never_acts_with_unresolved():
    P = Params(nu=0.0)
    df = pd.DataFrame(evaluate(P, 300, 4, ["conservative"]))
    assert df.harm.sum() == 0
    assert df[df.kind == "act"].stopped.mean() > 0.3
