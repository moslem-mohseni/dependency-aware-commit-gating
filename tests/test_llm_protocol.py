from pathlib import Path
import importlib.util,random,sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'src/llm_study'))
spec=importlib.util.spec_from_file_location('p5_protocol',ROOT/'src/llm_study/run.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from sim import Params,make_base,variant

def test_given_gate_reads_downstream_before_any_effect():
    plan=variant(make_base(random.Random(3),Params()),'DOWN',random.Random(1))
    world=module.Workspace(plan,1);world.params=Params(nu=0)
    for step in range(plan.n):
        if world.halted:break
        world.execute(step,'gate_given',plan.edges)
    assert world.stopped and not world.effects

def test_model_edges_cannot_reference_future_steps():
    assert module.parse_edges('{"edges":[[0,1]]}',3)=={(0,1)}
    with pytest.raises(ValueError):module.parse_edges('{"edges":[[2,1]]}',3)
    with pytest.raises(ValueError):module.parse_edges('{"edges":[[true,2]]}',3)

def test_mock_does_not_count_as_task_completion(tmp_path):
    from client import LLMClient
    plan=variant(make_base(random.Random(3),Params()),'act',random.Random(1))
    result=module.execute(plan,LLMClient('mock','mock',tmp_path),1,'ordinary')
    assert result['done']==0 and result['executed_irrev']==0

def test_effect_ledger_survives_later_failure():
    from sim import Plan
    plan=Plan(3,[False,True,False],{(1,2)},[[0],[0],[1]],{1},{0:True,1:False},'DOWN',1,1)
    world=module.Workspace(plan,2)
    for step in range(3):world.execute(step,'ordinary',plan.edges)
    assert world.effects==[1] and world.score()['harm']==1
