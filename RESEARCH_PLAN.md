# Research program: Jev as a stochastic choice mechanism

## Core framing

A Jev-style model maps a state `x` and a menu of alternatives `C` to a probability distribution

\[
P(i \mid x, C), \qquad i \in C.
\]

Rather than treating those probabilities only as classifier confidence, we study them as a **stochastic choice function**.
This gives a hierarchy of increasingly permissive behavioral models:

1. **Luce / multinomial logit (MNL)** — fixed menu-independent utilities plus iid Gumbel noise. Implies IIA.
2. **General menu-independent random utility (RUM)** — a distribution over latent rankings/utilities. May violate IIA, but obeys stronger revealed-stochastic-preference restrictions such as regularity and membership in the RUM polytope.
3. **Contextual choice** — utilities/probabilities depend directly on the menu, order, semantic similarity of alternatives, or omitted latent alternatives.

The calibration question should come *after* identifying which level describes the model.

## Experiment 00 — Menu Geometry

**Goal:** identify the behavioral class of the frozen raw pointer head.

For each state:

- create five named alternatives;
- query every menu with at least two alternatives: `2^5 - 5 - 1 = 26` menus;
- repeat menus under several option orders;
- retain the complete probability vector.

Primary quantities:

- pairwise log-odds variation across menus (IIA diagnostic);
- regularity violations;
- L1 distance to the RUM polytope, computed by a linear program over all `5! = 120` strict rankings;
- probability and argmax sensitivity to option order;
- the same tests after averaging over permutations.

### Hypotheses

**H0 — scalar-noise model.** The raw pointer head is approximately MNL; IIA violations are negligible after numerical/order noise.

**H1 — richer random utility.** IIA fails, but regularity and RUM rationalizability mostly survive. Then nested/mixed/latent-class choice models are a natural calibration family.

**H2 — menu-context model.** Regularity and RUM rationalizability fail systematically. Then the pointer head is not merely producing noisy latent utilities; the menu itself changes the effective valuation of alternatives.

**H3 — order is a major latent variable.** Symmetrizing over option permutations sharply reduces RUM distance. Then permutation aggregation is a principled intervention before adding a richer calibrator.

**H4 — failures concentrate in ambiguity/clone regimes.** Violations are much larger for underspecified or semantically similar alternatives than for explicit deterministic rules. That would motivate heteroskedastic or latent-state calibration.

## Experiment 01 — Choice calibration

Only after Experiment 00 selects the behavioral family, compare post-hoc models on held-out states:

- scalar temperature;
- temperature conditioned on option count/question features;
- heteroskedastic logit;
- nested logit for semantically related alternatives;
- finite-mixture / latent-class logit;
- possibly a small learned choice head constrained by the diagnostics above.

Metrics: NLL, Brier, ECE, selective risk/coverage, OOD transfer, and preservation of revealed-choice consistency.

## Experiment 02 — Latent outside / unknown option

Test whether the observed distribution is better explained by an unobserved alternative `U`:

\[
P(U\mid x,C) + \sum_{i\in C} P(i\mid x,C)=1.
\]

Candidate evidence:

- probability inflation when weak alternatives are removed;
- binary questions that become overconfident when no offered answer is well supported;
- systematic dependence of calibration on entropy, margin, menu size, or semantic coverage.

Compare explicit outside-option models against temperature-only calibration.

## Experiment 03 — Social choice / aggregation

Only after the single-agent choice function is characterized, treat perturbations as voters:

- option orders;
- paraphrases;
- checkpoints/models;
- reasoning samples.

Each voter induces rankings/cardinal probabilities. Compare probability pooling, Borda/Kemeny-style rank aggregation, pairwise methods, and randomized social-choice rules. Arrow-type impossibility results become relevant here because we are genuinely aggregating multiple preference orderings rather than diagnosing one stochastic chooser.

## Decision gate after Experiment 00

- **IIA fails, RUM distance ~0:** prioritize nested/mixed logit.
- **RUM distance >0 but symmetrization fixes it:** prioritize permutation-invariant aggregation/training.
- **RUM distance remains >0 and clusters around clones:** prioritize context-dependent utility / similarity models.
- **RUM distance clusters around underspecified states:** prioritize outside-option/latent-uncertainty modeling.
- **All violations tiny:** the simplest useful contribution may be a principled DCM interpretation of temperature plus heteroskedastic calibration, rather than a new architecture.
