# Ordinary-access fractional evolution

This package gives quantitative extensions of Araújo et al.'s global-phase
obstruction for the uncontrolled-access question of Liu, Wesołowski, Thompson,
Gu and Pira, *Optimal query complexity for fractional quantum evolution*,
arXiv:2610.01940v1, Section V, page 7.

## Mathematics

For every dimension d ≥ 2, 0 < δ < π and 0 < t < 1, the prescribed branch
[δ, 2π) forces unhalved diamond-norm error at least sin(πt) for ordinary-query
algorithms. A circuit retaining its pure full output has the stronger bound
2 sin(π min(t,1−t)/2). The note proves the endpoint order of the best error and
classifies C¹ real phase functions allowing arbitrarily accurate ordinary-access
implementation on this branch: exactly f(θ) = mθ+b for integer m.

These are written proofs. The controlled-access conjectures and the optimal
Haar-average query complexity in the posing source are not covered.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded in `note.tex`; no BibTeX step or external figure
is required. Python 3's standard library suffices for the finite checks:

```sh
python3 verify.py > verification.json
python3 verify_extensions.py > extension-verification.json
```

## Coverage

- `note.tex` and `note.pdf`: complete written arguments and four public references.
- `coverage.json`: source-item mapping and exact mathematical scope.
- `verify.py`, `verification.json`: exact Gaussian-rational square-root identities
  and 93 ordered circuit instances, all sign words of lengths 0–4 and workspace
  dimensions 1–3, for the specified rational gate family.
- `verify_extensions.py`, `extension-verification.json`: finite checks of the
  extended witness, dimensions 2–4, ordered circuits, pure-state projector
  identity, and polynomial finite-difference examples.
- `metadata.json`: creators, license, statement and source locators.
- `LICENSE.txt`: CC BY 4.0 notice.

The pinned Lean declaration
`Trureturing.OpenProblems.FractionalEvolutionPhase.result` states the negation
of the universal ordinary-query upper bound, using d=2, t=δ=1/2, ε=1/4,
all finite nonzero workspaces and the full-output unhalved criterion:

https://github.com/the-omega-institute/trureturing/blob/42aeb4e95344fb1ea9d2042d02ff1a5589faaacb/D5/S3/Quantum/QuantumChannels/FractionalEvolutionPhaseObstruction.lean

The parameterized bounds, gap enlargement and phase-function classification
have written proofs in the note; they are not statements of that declaration.
Finite checks establish only their listed matrix identities and parameter sets.

Creators, in order: Haobo Ma (ChronoAI Pte Ltd, Singapore); Wenlin Zhang
(National University of Singapore; ChronoAI Pte Ltd, Singapore).
License: Creative Commons Attribution 4.0 International (CC BY 4.0).
