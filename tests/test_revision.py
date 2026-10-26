import random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pytest
from sim import Params,make_base,variant,public_plan_text,extract_dependencies,run_policy,evaluate,believed_edges

def test_explicit_parser_uses_public_text_only():
    for seed in range(30):
        plan=variant(make_base(random.Random(seed),Params()),'DOWN',random.Random(1))
        text=public_plan_text(plan)
        assert extract_dependencies(text)==plan.edges
        plan.truth={p:not value for p,value in plan.truth.items()}
        assert text==public_plan_text(plan)

def test_spurious_probability_one_includes_all_forward_pairs():
    plan=variant(make_base(random.Random(2),Params()),'act',random.Random(1))
    got=believed_edges(plan,Params(dep_recall=0,dep_spurious=1),random.Random(1))
    assert got=={(a,b) for a in range(plan.n) for b in range(a+1,plan.n) if (a,b) not in plan.edges}

def test_policy_subset_has_identical_noise_stream():
    all_rows=evaluate(Params(),10,71)
    sub=evaluate(Params(),10,71,['gate'])
    assert sub==[r for r in all_rows if r['policy']=='gate']

def test_parser_rejects_unsupported_or_invalid_references():
    with pytest.raises(ValueError):extract_dependencies('Free form prose')
    with pytest.raises(ValueError):extract_dependencies('Step 0: consumes [result_2]; preconditions [p0]; irreversible=False.')

def test_exact_extraction_matches_given_gate_under_perfect_checks():
    frame=evaluate(Params(nu=0,q_habit=0),50,31,['gate_text'])
    assert not any(r['harm'] for r in frame if r['kind'] in ('LOCAL','DOWN'))
