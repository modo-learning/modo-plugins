---
type: llm
weight: 3
---

Rubric ground truth for Verification: level 1 takes answers as given; level 2 reacts only to obvious errors or asks "are you sure?" without checking anything; level 3 checks some claims against own knowledge or a source (spot-checks a figure, asks where a fact comes from, points out a specific discrepancy); level 4 checks deliberately and more than once (asks for sources or the working, recomputes or runs the result themselves, compares with a second source, has errors fixed and re-checked); level 5 builds checking into the work (acceptance checks before starting, edge cases, an independent method, stating what has and has not been verified).

PASS if the response gives concrete techniques for getting better at Verification that are recognisably the rubric's next-level behaviours (such as spot-checking a figure or asking for the source, asking for the working and recomputing it, comparing with a second source, setting acceptance checks first or stating what was and was not verified), AND includes at least one "try this next time" prompt the user can copy and paste as it stands. It must not require an earlier assessment or ask the user to paste a chat first.
FAIL if the advice is generic ("double-check everything"), has no copy-ready prompt, refuses or demands a prior assessment, or covers a capability other than Verification.
