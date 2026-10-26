"""Dependency-aware commit gating before irreversible actions (Paper 5).

A plan is a list of steps with preconditions (predicates shared across steps), a dependency
DAG between steps, and per-step reversibility. Some predicates are *unresolved*: their truth is
hidden until a (cost-1) read-only check. Variants of one base plan are paired:
  act   : every predicate holds
  LOCAL : an unresolved predicate of the first irreversible step fails
  DOWN  : an unresolved predicate used only by a later step that depends on the irreversible one fails
  INDEP : an unresolved predicate used only by a later step independent of the irreversible one fails
Harm = an irreversible step executed and a step depending on it then cannot complete
(for LOCAL: the tool silently executes with probability p_local_exec).
"""
from __future__ import annotations

import random
import re
import zlib
from dataclasses import dataclass, field

KINDS = ("act", "LOCAL", "DOWN", "INDEP")


@dataclass
class Params:
    n_steps: tuple = (4, 5, 6)
    p_irrev: float = 0.35         # a step (other than step 0) is irreversible
    p_edge: float = 0.45          # dependency edge between ordered step pairs
    r_unres: float = 0.5          # predicate is unresolved
    pool_extra: int = 2           # predicate pool size = n_steps + pool_extra
    nu: float = 0.03              # check noise (wrong reading)
    q_habit: float = 0.25         # chance the agent checks an unresolved predicate of its current step anyway
    q_verbal: float = 0.60        # same, after a verbal caution reminder
    p_verbal_abstain: float = 0.05
    p_local_exec: float = 0.5     # tool silently executes irreversible step with unmet precondition
    dep_recall: float = 1.0       # fraction of true dependency edges the gate knows
    dep_spurious: float = 0.0     # fraction of non-edges wrongly believed (inflates checking scope)


@dataclass
class Plan:
    n: int
    irrev: list
    edges: set
    pre: list
    unres: set
    truth: dict
    kind: str
    istar: int
    fail_pred: int | None = None
    base_id: int = 0


def descendants(n, edges, root):
    out, stack = set(), [root]
    while stack:
        u = stack.pop()
        for (a, b) in edges:
            if a == u and b not in out:
                out.add(b)
                stack.append(b)
    return out


def make_base(rng: random.Random, P: Params):
    """Generate a base plan eligible for all four variants."""
    for _ in range(1000):
        n = rng.choice(P.n_steps)
        irrev = [False] + [rng.random() < P.p_irrev for _ in range(n - 1)]
        if not any(irrev):
            irrev[rng.randrange(1, n)] = True
        istar = irrev.index(True)
        edges = {(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < P.p_edge}
        pool = n + P.pool_extra
        pre = [rng.sample(range(pool), rng.choice([1, 2])) for _ in range(n)]
        unres = {p for p in range(pool) if rng.random() < P.r_unres}
        D = descendants(n, edges, istar)
        later = [j for j in range(istar + 1, n)]
        indep = [j for j in later if j not in D]
        if not D or not indep:
            continue
        def excl(steps, forbid):
            used_forbid = {p for s in forbid for p in pre[s]}
            return sorted({p for s in steps for p in pre[s]} - used_forbid)
        local_c = [p for p in pre[istar] if True]
        down_c = excl(sorted(D), [s for s in range(n) if s not in D])  # used only by dependent steps
        down_c = [p for p in down_c if p not in pre[istar] and not any(p in pre[s] for s in range(istar + 1))]
        indep_c = excl(indep, [s for s in range(n) if s in D or s <= istar])
        if not local_c or not down_c or not indep_c:
            continue
        return dict(n=n, irrev=irrev, edges=edges, pre=pre, unres=unres, istar=istar, pool=pool,
                    cands=dict(LOCAL=local_c, DOWN=down_c, INDEP=indep_c))
    raise RuntimeError("could not build eligible plan")


def variant(base, kind, rng: random.Random, base_id=0):
    truth = {p: True for p in range(base["pool"])}
    unres = set(base["unres"])
    fail = None
    if kind != "act":
        fail = rng.choice(base["cands"][kind])
        truth[fail] = False
        unres.add(fail)  # the failing predicate is unresolved by construction
    return Plan(base["n"], base["irrev"], base["edges"], base["pre"], unres, truth, kind, base["istar"], fail, base_id)


# ----------------------------------------------------------------------------- policies

def _read(plan, p, P, rng):
    """Noisy read-only check: returns observed truth value."""
    v = plan.truth[p]
    return (not v) if rng.random() < P.nu else v


def believed_edges(plan, P, rng):
    edges = set()
    for (a, b) in sorted(plan.edges):
        if rng.random() < P.dep_recall:
            edges.add((a, b))
    if P.dep_spurious > 0:
        for i in range(plan.n):
            for j in range(i + 1, plan.n):
                if (i, j) not in plan.edges and rng.random() < P.dep_spurious:
                    edges.add((i, j))
    return edges


def _finalize(plan, executed_irrev, stopped, done, checks, fic):
    """Harm: an executed irreversible step whose own step or dependents cannot complete."""
    bad_steps = {s for s in range(plan.n) if any(not plan.truth[p] for p in plan.pre[s])}
    harm = 0
    for i in executed_irrev:
        if ({i} | descendants(plan.n, plan.edges, i)) & bad_steps:
            harm = 1
    return dict(stopped=int(stopped), executed_irrev=int(bool(executed_irrev)), harm=harm, done=int(done),
                checks=checks, checks_before_first=fic if fic is not None else (0 if not executed_irrev else checks))


def public_plan_text(plan):
    """Publish ordered step contracts, including explicit producer references, never truth."""
    lines=[]
    for step in range(plan.n):
        parents=sorted(a for a,b in plan.edges if b==step)
        lines.append(f'Step {step}: consumes ['+', '.join('result_'+str(a) for a in parents)+']; preconditions ['+', '.join('p'+str(p) for p in sorted(plan.pre[step]))+']; irreversible='+str(plan.irrev[step])+'.')
    return '\n'.join(lines)


def extract_dependencies(text,mode='explicit'):
    """Two fixed non-oracle parsers; neither receives a Plan or hidden predicate truth."""
    contracts={}
    for line in text.splitlines():
        match=re.fullmatch(r'Step (\d+): consumes \[([^]]*)\]; preconditions \[([^]]*)\]; irreversible=(True|False)\.',line)
        if not match:raise ValueError('Unsupported step-contract grammar')
        step=int(match[1])
        if step in contracts:raise ValueError('Repeated step')
        contracts[step]=(set(map(int,re.findall(r'result_(\d+)',match[2]))),set(map(int,re.findall(r'p(\d+)',match[3]))))
    if sorted(contracts)!=list(range(len(contracts))):raise ValueError('Steps must be contiguous')
    if mode=='explicit':
        edges={(a,b) for b,(parents,_) in contracts.items() for a in parents}
        if any(a>=b or a not in contracts for a,b in edges):raise ValueError('Invalid forward reference')
        return edges
    if mode=='shared':
        return {(a,b) for a in contracts for b in contracts if a<b and contracts[a][1]&contracts[b][1]}
    raise ValueError('Unknown extractor')


def run_policy(plan: Plan, policy: str, P: Params, rng: random.Random, dependency_edges=None):
    """Returns dict(stopped, executed_irrev, harm, done, checks, checks_before_first)."""
    n, checks = plan.n, 0
    checked = {}
    first_irrev_checks = None
    stopped = False

    def check(p):
        nonlocal checks
        if p not in checked:
            checks += 1
            checked[p] = _read(plan, p, P, rng)
        return checked[p]

    habit = {"ordinary": P.q_habit, "verbal": P.q_verbal}.get(policy, P.q_habit)
    if policy == "verbal" and rng.random() < P.p_verbal_abstain:
        return _finalize(plan, [], True, False, 0, 0)
    if policy == "conservative":
        if any(p in plan.unres for s in range(n) for p in plan.pre[s]):
            return _finalize(plan, [], True, False, 0, 0)
    be = (believed_edges(plan, P, rng) if dependency_edges is None else set(dependency_edges)) if policy.startswith("gate") else plan.edges

    executed_irrev = []
    for s in range(n):
        if plan.irrev[s]:
            scope = []
            if policy == "per_action":
                scope = [s]
            elif policy == "full":
                scope = list(range(n))
            elif policy.startswith("gate"):
                scope = [s] + sorted(descendants(n, be, s))
            for t in scope:
                for p in plan.pre[t]:
                    if p in plan.unres and not check(p):
                        stopped = True
                        break
                if stopped:
                    break
            if first_irrev_checks is None:
                first_irrev_checks = checks
            if stopped:
                break
        for p in plan.pre[s]:
            if p in plan.unres and rng.random() < habit:
                if not check(p):
                    stopped = True
                    break
        if stopped:
            break
        fails = [p for p in plan.pre[s] if not plan.truth[p]]
        if fails:
            if plan.irrev[s] and rng.random() < P.p_local_exec:
                executed_irrev.append(s)       # tool silently executed an irreversible step
            break                              # execution halts at the failing step
        if plan.irrev[s]:
            executed_irrev.append(s)
    done = (not stopped) and all(plan.truth[p] for s in range(n) for p in plan.pre[s])
    return _finalize(plan, executed_irrev, stopped, done, checks, first_irrev_checks)


POLICIES = ["ordinary", "verbal", "per_action", "conservative", "full", "gate"]


def evaluate(P: Params, n_plans: int, seed: int, policies=POLICIES):
    rows = []
    rng0 = random.Random(seed)
    for b in range(n_plans):
        base = make_base(rng0, P)
        for kind in KINDS:
            vrng = random.Random(seed * 100003 + b * 17 + KINDS.index(kind))
            plan = variant(base, kind, vrng, b)
            for pi, pol in enumerate(policies):
                prng = random.Random(seed * 999983 + b * 131 + KINDS.index(kind) * 7 + zlib.crc32(pol.encode('utf8')))
                extracted=None
                if pol in ('gate_text','gate_shared'):
                    extracted=extract_dependencies(public_plan_text(plan),'explicit' if pol=='gate_text' else 'shared')
                r = run_policy(plan, pol, P, prng,dependency_edges=extracted)
                if extracted is not None:
                    true_reach=descendants(plan.n,plan.edges,plan.istar)
                    inferred_reach=descendants(plan.n,extracted,plan.istar)
                    r.update(edge_tp=len(extracted&plan.edges),edge_pred=len(extracted),edge_true=len(plan.edges),reach_tp=len(true_reach&inferred_reach),reach_true=len(true_reach),reach_pred=len(inferred_reach))
                r.update(policy=pol, kind=kind, base=b, seed=seed)
                rows.append(r)
    return rows
