"""Regenerate P5 findings and self-contained reproduction instructions."""
from pathlib import Path
import pandas as pd
root=Path(__file__).resolve().parents[1]
t=pd.read_csv(root/'results/table1_main.csv').set_index('policy')
ex=pd.read_csv(root/'results/extraction_summary.csv')
g=t.loc['gate'];f=t.loc['full'];local=t.loc['per_action']
h=ex[(ex.policy=='gate_shared')&(ex.kind=='DOWN')].iloc[0]
(root/'docs/RESEARCH.md').write_text(f'''# Dependency-Aware Commit Gating

## Findings and scope
Parametric simulation only: gate paired act-and-DOWN accuracy {g.paired_act_down:.3f}; DOWN structural harm {g.DOWN_harm:.4f} versus {local.DOWN_harm:.3f} for local checks. The large contrast is partly constructed by placing an exclusive failure beyond the local scope. Gate mean checks {g.checks_all:.3f} versus check-all {f.checks_all:.3f}, a {100*(1-g.checks_all/f.checks_all):.1f}% reduction in unit checks. INDEP first-commit withholding is {g.overstop_indep:.4f} versus {f.overstop_indep:.4f}; it is not full-task success. INDEP can still implicate another irreversible effect.

Fresh shared-predicate extraction has edge precision {h.edge_precision:.3f}, recall {h.edge_recall:.3f}, descendant recall {h.reach_recall:.3f} and DOWN harm {h.harm:.3f}. Explicit-reference parsing is perfect only because the public grammar encodes gold edges. Parsing/graph-building cost is not charged. The graph itself is a declaration, not verified causal semantics. No security or real-agent guarantee follows.

Corrected policy-order-dependent noise and a spurious-edge parameter that was labelled 30% but implemented as 15%. Each non-edge now uses the declared probability. No external benchmark, SafeCommit implementation or real model was run. The local check is not a SafeCommit surrogate; its general safety map can include downstream constraints. AgentAbstain already defines execution graphs and commit checks. Ten verified references and three full-text notes document this positioning.

## Reproduce
Use Python 3.12 and pinned requirements:

```bash
pip install -r requirements.txt
bash run_all.sh
docker build -t p5_commit_gating .
docker run --name p5_reproduction p5_commit_gating
docker cp p5_reproduction:/work/results ./container_results
docker cp p5_reproduction:/work/paper/supplementary_p5.zip ./
```

```powershell
./run_all.ps1
./run_all.ps1 -SkipPdf
```

The complete pipeline runs tests, main and sensitivity experiments, measured extraction, Holm/interval analysis, figures, labelled model mock, manuscript, numeric/citation/template audits, README and supplementary packaging. Docker creates DOCX and scientific results. Windows PDF export uses Microsoft Word. Compare CSVs with pandas.assert_frame_equal(check_exact=True), ignoring only line endings.

## Seeds, pairing and inference
Main: 3000 base plans at seed 7, four variants, nine policies. The inherited main design had already been explored. Sweeps: seed 11; long plans: 13; fresh extraction: 23 with 1500 bases and five policies. The primary revision outcome requires both feasible act completion and no irreversible effect on paired DOWN. Seven contrasts use Holm correction, 1000 base-plan bootstrap resamples and 2000 sign-flips at statistical seed 71. Forty-two component contrasts are secondary. All intervals are nominal, and extraction/sweeps are exploratory.

Rejection sampling conditions on eligibility for all four variants. Failure predicates are forced unresolved, potentially changing the visible mask. Harm is a binary structural proxy, truth is static, observations are independently noisy but cached, and costs are assumed unit reads. Worlds are shared; policy noise is independently keyed by name, not coupled choice by choice.

## Separate model execution protocol
No credentials or ready local model were discovered; the documented official acquisition attempt timed out. See results/llm/status.json and src/llm_study/availability_attempt.json. The 200 variant episodes comprise 50 paired bases across ordinary prompt, verbal caution, local check and gates with given/model-extracted graphs. Code owns reads and effects. The mock is labelled and excluded from scientific estimates. If real execution becomes possible, six primary contrasts are Holm corrected and secondary rate/cost intervals are computed.

The cached provider-agnostic client uses temperature zero and a persistent USD 5 cap. Paid invocation requires actual model/version and verified conservative prices:

```bash
python src/llm_study/run.py --backend openai --model ACTUAL_MODEL --input-price-per-million ACTUAL_PRICE --output-price-per-million ACTUAL_PRICE
```

## Files and metadata
src/sim.py defines predicates, declared graphs, parsers and immutable effects. src/run_experiments.py and analysis scripts generate results and 300-dpi figures. paper contains the original template, author.json, builder, audits and supplementary_p5.zip. The archive includes runnable sources/results/template and a SHA-256 manifest. Reading caches and mutable execution logs are excluded.

Edit paper/author.json and rebuild with `python paper/build_manuscript.py`, or `python build_manuscript.py` from paper/. Re-export the PDF after editing metadata. Original files are retained in the root backup.
''',encoding='utf8')
print('P5 README updated')
