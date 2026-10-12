# Stage B developer's strongest case: N3 collision-aware hard batch acquisition

Author: acquisition developer (`flash`, medium); date: 2026-10-11.
Candidate: `N3` (Collision-aware joint hard acquisition).

## 1. Strongest case for N3
In the Stage B diverse screen across 40 fresh seed clusters (110001–110040) and all 6 scenario families (240 paired comparisons):
- N3 achieved a paired mean difference of **+0.03333 MSMI/100** against shipped greedy (`G`), exceeding the registered promotion threshold of +0.025.
- Paired cluster differences: 19 positive clusters, 12 zero clusters, 9 negative clusters.
- Scenario-specific differences:
  - `development`: +0.0500 MSMI/100
  - `sparse`: +0.0250 MSMI/100
  - `cold_start`: +0.0750 MSMI/100
  - `delayed`: +0.0250 MSMI/100
  - `shift`: +0.0000 MSMI/100
  - `drift`: +0.0250 MSMI/100
- Mean effect is positive or non-negative in all six scenario families, with the strongest gain in `cold_start` (+0.0750) where initial missingness is highest and query efficiency matters most.
- N3 operates purely on public information without reading hidden world truth, latent exit days, or outcome draws.
- Execution was robust: 0 fallbacks across all 240 episodes, strict adherence to memory limit (<1 MiB, returning `{}`), and mean invocation time well below the 10-second limit (~3.8s per episode).

## 2. Mechanism justification
N3 evaluates up to 4 constraint bundles jointly across 32 coherent particles to maximize the expected matching cardinality and soft score of newly revealed opportunities, rather than asking members in naive FIFO order. This directly addresses query collision (where multiple queried members compete for the same partner) and query complementarity (where both endpoints of a potential pair require clarification).

The developer recommends promoting **N3** to Stage C replication and targeted ablations against its controls.
