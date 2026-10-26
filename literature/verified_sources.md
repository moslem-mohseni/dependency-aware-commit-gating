# Primary-record verification receipt
Date: 2026-10-26. Supersedes the original abstract-only ledger. All ten manuscript references are verified below; three full-text notes are in notes_fulltext.md. Local reading caches are excluded from packaging.

| Reference | Primary source and comparison |
| --- | --- |
| Akewar and Ranjan, 2026 | https://arxiv.org/abs/2608.04289 and full HTML v1; SafeCommit: Certifying When Memory-Grounded Agents May Safely Act; both authors, 2026 preprint. Full main text and appendices read. |
| Alshiekh et al., 2018 | https://ojs.aaai.org/index.php/AAAI/article/view/11797 ; Safe Reinforcement Learning via Shielding; six authors, Proceedings of AAAI 32(1), 2018, DOI 10.1609/aaai.v32i1.11797. Primary record/abstract opened. |
| Blum and Furst, 1997 | Publisher indexed page https://www.sciencedirect.com/science/article/pii/S0004370296000471 and live Crossref API https://api.crossref.org/works/10.1016/S0004-3702(96)00047-1 ; title, two authors, Artificial Intelligence 90(1-2), 281-300. Direct publisher endpoint 403; live DOI registration metadata fetched and saved. |
| Efron, 1979 | https://api.crossref.org/works/10.1214/aos/1176344552 ; P1-P4 primary verification reused: author/title, Annals of Statistics 7(1), 1-26. |
| Fikes and Nilsson, 1971 | Publisher indexed record https://www.sciencedirect.com/science/article/pii/0004370271900105 plus live Crossref filter query https://api.crossref.org/works?filter=doi:10.1016/0004-3702(71)90010-5 ; title, authors, Artificial Intelligence 2(3-4), 189-208. Direct publisher 403; live registration metadata fetched. Author publication page/PDF indexed metadata corroborates. |
| Garcia-Molina and Salem, 1987 | https://api.crossref.org/works/10.1145/38714.38742 fetched live: Sagas, both authors, ACM SIGMOD Record 16(3), 249-259, DOI confirmed. ACM endpoint 403; not claimed as a new full-text reading. |
| Holm, 1979 | https://www.jstor.org/stable/i412579 and https://www.jstor.org/stable/4615733 ; P1-P4 verified primary issue/record reused: author/title, Scandinavian Journal of Statistics 6(2), 65-70. |
| Liu et al., 2026 | https://arxiv.org/abs/2607.10059 and full HTML v1; AgentAbstain: Do LLM Agents Know When Not to Act?; eight authors including Yi Evie Zhang, 2026 preprint. Main/formal text checked; exact model headline rates not repeated in our paper. |
| Ruan et al., 2024 | https://arxiv.org/abs/2309.15817 and full HTML v2; title, nine authors, 2024 revision. Official ICLR PDF indexed header confirms conference, but manuscript cites the pinned arXiv version actually read. Live OpenReview endpoint showed a browser challenge. |
| Wilson, 1927 | Publisher https://www.tandfonline.com/doi/permissions/10.1080/01621459.1927.10502953 and original authored https://jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf ; P3-P4 verification reused: author/title, JASA 22(158), 209-212, original year. |

## Positioning and additions
Four further references strengthen the original thin planning/control discussion: STRIPS, Graphplan, shielding and Sagas. They establish prior precondition/graph reasoning, external action mediation and the distinct role of compensation. No new novelty is claimed for those ideas. SafeCommit can include downstream constraints in its safety map, so our local check cannot stand in for it. AgentAbstain already has execution DAGs and commit-level checks. Known-format parsing is not natural-language dependency extraction, and shared predicates need not imply data dependence. Pinned preprints may later change.
