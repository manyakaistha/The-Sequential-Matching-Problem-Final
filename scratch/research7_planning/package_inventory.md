# Research 7a/7b handoff package inventory

Read-only inventory by `/root/r7_package_inventory`; reviewer: `/root` and `r7_package_builder`. No project modules were imported or executed. Bulk raw logs and archive contents were excluded. Directory sizes below are `du -sh` for source directories, not a proposed bundle manifest.

## Core harness and P baseline

| Path | Bytes | Imports / role | Handoff note |
|---|---:|---|---|
| `kit.py` | 16,218 | Python standard library only; generator, simulator, eligibility and baseline helpers | Required by `evaluate.py`, root `policy.py`, R6 policy entrypoint and R4/R3 policy code. |
| `evaluate.py` | 8,353 | Standard library plus `kit` | Required evaluation harness. Docker is only used by container mode; local mode uses subprocess. |
| `policy.py` | 1,540 | Standard library plus `kit` | Root P/reference JSON adapter. |

`kit.py` documents Python >=3.10 and standard-library-only. No non-source runtime data is opened by these three modules. `evaluate.py` imports `Simulator`, `generate`, and `VERSION` from `kit`; it dynamically launches the selected policy command and does not require a fit artifact.

## R6 source dependencies

| Path | Bytes | Dependency evidence |
|---|---:|---|
| `research6/policies/policy.py` | 5,562 | Imports `kit` and package-relative `.allocation`; stdlib otherwise. |
| `research6/policies/allocation.py` | 5,112 | Imports `kit`; lazy imports `networkx` for K and `research4.candidates` / `research6.policies.acquisition` for additional paths. |
| `research6/policies/acquisition.py` | 12,420 | Imports `kit`; stdlib otherwise. |
| `research6/policies/__init__.py` | 55 | Include for package imports. |
| `research6/exact/run.py` | 10,178 | Relative imports `solver` and `specifications`; stdlib. Writes new output when run, so source copying does not require execution. |
| `research6/exact/solver.py` | 8,122 | stdlib `fractions`, `functools`, `itertools`; no simulator/data imports. |
| `research6/exact/specifications.py` | 9,812 | stdlib plus relative `solver`. |
| `research6/exact/THEORY.md` | 13,690 | Referenced by the exact runner’s source snapshot/hash inventory. |
| `research6/exact/__init__.py` | 59 | Include for package imports. |

`research6/requirements.lock.txt` pins `numpy==2.5.3`, `scipy==1.18.1`, and `networkx==3.7`; only NetworkX is directly relevant to the shipped R6 K allocation branch. Exact solver dependencies are standard library. A portable handoff should state Python version and whether K is enabled; the lock file also covers broader offline-research code.

## R4 frozen baseline transitive source dependencies

`research4/policy.py` (2,597 bytes) imports `research4.candidates`. That module (10,499 bytes) imports `kit`, `research3.policy.legal_edges`, `research3.model_candidates` functions and `research.terminal_model`. The transitive source-only set needed to import/use these candidate paths is therefore:

| Path | Bytes |
|---|---:|
| `research4/__init__.py` | 0 |
| `research4/policy.py` | 2,597 |
| `research4/candidates.py` | 10,499 |
| `research3/__init__.py` | 73 |
| `research3/policy.py` | 5,908 |
| `research3/model_candidates.py` | 5,868 |
| `research/terminal_model.py` | 11,682 |

`research3/model_candidates.py` defines `OFFLINE_WEIGHTS` as a six-number tuple in source. Its comment identifies it as fitted from already examined seeds 1001–1005, with validation seeds 1006–1008; inference does not read a serialized model. Thus the frozen baseline needs the source file but no separate coefficient file for this candidate. This is a source dependency observation, not an endorsement or new fit.

## Fit assets, omissions, and package size

No path named `fitassets`, `fit_assets`, or `assets` was found under `research3`, `research4`, or `research6`; no `.pkl`, `.joblib`, `.onnx`, `.npy`, `.npz`, `.pt`, or `.pth` files were found there. The only identified frozen coefficient asset is embedded in `research3/model_candidates.py` as `OFFLINE_WEIGHTS`. R6 plan text mentions future L1/L2 fit artifacts, but the reviewed source tree has no `research6/models/` directory or completed training artifact; do not represent those as included or available.

Measured source directory sizes: `research3` 956 KiB, `research4` 812 KiB, `research6` 13 MiB, `research` 2.5 MiB. The three round directories are small enough for source handoff as a practical matter, but `research6` includes reviews, planning revisions, registries, audits and records beyond the runtime dependency closure. A lean package can copy the listed source closure; including the complete directories remains feasible at these observed sizes. This inventory did not enumerate or copy result trees.

## Scope limits

This is a path/import/size inventory only. It does not verify behavior, execute import resolution, inspect every historical manifest, evaluate the scientific validity of coefficients, or attest that no external/private copy exists. The repository’s Google model routing values were read as instructed and left unchanged.
