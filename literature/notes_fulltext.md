# Full-text positioning notes
Read on 2026-10-26. Three closest main texts were read from their pinned official arXiv HTML. Additional formal appendices were read where needed. No external benchmark was executed.

## AgentAbstain - Liu et al. (2026), v1
- Read all main sections through Conclusion and limitations, plus Appendix B.1-B.6 on execution graphs, critical actions, policies and metrics: https://arxiv.org/html/2607.10059v1.
- Paired tasks perturb one instruction, environment or tool dimension and assess whether the agent acts or abstains appropriately.
- The paper already formalizes execution DAGs, lookup/verify/commit tools and critical action sets; graph-based commitment framing is direct overlap.
- Operational success combines deterministic commit membership with a separate verbal judge; informational tasks use the verbal signal alone.
- Post-hoc abstention includes an irreversible effect followed by a false verbal assurance; our simulation measures effects and has no comparable semantic response judge.
- Their headline paired accuracy requires both variants to pass, motivating our base-plan act-and-DOWN primary outcome.
- Deterministic generated environments, one run per model and judge uncertainty limit transfer; our single grammar is narrower still.
- P5 adds a conditional check-scope comparison and measured parser/heuristic sensitivity, not an abstention framework or reproduction of their tasks.

## SafeCommit - Akewar and Ranjan (2026), v1
- Read the entire main text and appendices A-E: https://arxiv.org/html/2608.04289v1.
- A calibrated plausible-world set supports action certification; if no action is safe in every retained world, targeted probes or fallback are used.
- The guarantee assumes world coverage at commitment and a correct domain safety map; missing worlds add representation error.
- The safety map can encode arbitrary domain constraints, including downstream feasibility. It is not restricted to local action preconditions.
- Its controlled evaluation uses explicit worlds, deterministic probes and hand-coded safety maps; it is not a real-model deployment study.
- Sequential commitments require additional mission-level calibration or risk budgeting; per-action guarantees do not automatically compose.
- Our per-action baseline is only a local predicate check, not a reproduction, approximation or lower bound for SafeCommit.
- P5 compares structural scope/cost under a fixed safety proxy and does not supply a conformal guarantee or establish orthogonality to a general safety map.

## ToolEmu - Ruan et al. (2024), arXiv v2
- Read all main sections through Limitations and Future Directions: https://arxiv.org/html/2309.15817v2.
- Language models emulate tool state/transitions and separately evaluate helpfulness and risk; a standard and adversarial emulator vary scenario difficulty.
- The threat model is benign but underspecified instructions; both safety and useful achievement matter, so always refusing is not a successful solution.
- Human annotation validates emulator consistency and failure realism; evaluator agreement and recall are imperfect.
- Prompted caution can help some models but does not remove failures; such measured prompt behavior is absent from our parametric verbal baseline.
- Tool breadth and long-tail scenario generation trade off against model-emulation and model-judge errors.
- P5 has exact symbolic truth and effects but much weaker semantic realism; neither evaluation approach subsumes the other.
- No ToolEmu tools, test cases, language-model trajectories or published rates are imported as our experimental results.
