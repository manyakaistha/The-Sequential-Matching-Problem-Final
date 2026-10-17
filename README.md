# Sequential Reciprocal Matching

Research and implementation for the One Introduction Problem: deciding which information to request and which feasible pairs to introduce when people arrive over time and feedback is delayed.

The final implementation retains the supplied Greedy policy. Our tested alternatives did not establish confirmatory superiority. All populations and outcomes are synthetic.

## Report and implementation

- [Final Round 2 report](final_report/REPORT.md): methodology, results, limitations and responses to the Round 1 feedback.
- [Report assets and reproduction](final_report/README.md): 12 figures, source tables and plotting code.
- [Research index](docs/RESEARCH_INDEX.md): experiments, earlier reports and evidence locations.
- [Problem statement](PROBLEM_STATEMENT.md): the original task and evaluation rules.
- [Policy implementation](policy.py), [simulator](kit.py) and [evaluator](evaluate.py).

## Clone

Install Git LFS before cloning; some saved result files are stored through LFS.

```bash
git lfs install
git clone https://github.com/manyakaistha/the-sequential-matching-problem-dev-repo-final.git
cd the-sequential-matching-problem-dev-repo-final
git lfs pull
```

See [cloning and updating](docs/CLONING.md) for existing checkouts and the limits of the versioned evidence. This presentation cleanup is on `cleanup/repository-presentation`; `main` retains the previous layout.

## Run the baseline

The baseline uses the Python standard library. The public kit supports Python 3.10 or later.

```bash
python -m unittest test_kit test_runner test_release -v
python verify_data.py
python evaluate.py --baseline greedy --seeds 101 --output results/local_greedy.json
```

The evaluator runs 60 decision days followed by 40 follow-up days. Its main outcome is qualified mutual second-meeting intention per 100 arrived members. An introduction must satisfy both members' hard constraints; missing information is not assumed compatible.

The other supplied controls are `--baseline no_asks` and `--baseline random`. Research policies and historical results are documented in the [research index](docs/RESEARCH_INDEX.md). Running the evaluator creates new simulation output; reading or rebuilding the report does not require it.

For container execution:

```bash
docker build -t sequential-policy:submission .
python evaluate.py --image sequential-policy:submission --seeds 101 --output results/local_container_check.json
```

The assessment container runs offline. See the [policy interface](docs/POLICY_INTERFACE.md) for JSON schemas and resource limits. Historical validation and outstanding checks are listed in the final report, Section 13.

## Repository layout

| Location | Contents |
|---|---|
| `policy.py`, `kit.py`, `evaluate.py` | Baseline, reference simulator and evaluation interface |
| `data/` | Supplied synthetic data and observable histories |
| `docs/` | Rules, data contract, setup and research navigation |
| `final_report/` | Final report, figures, derived tables and independent reviews |
| `research/`, `research2/`–`research9/` | Historical implementations, plans, registrations, reports and reviews |
| `research7a/`, `research7b/` | Separate research workspaces and preserved handoff snapshots |
| `results/` | Versioned summaries and local results; large raw archives are excluded |
| `scratch/` | Historical exploratory work; not the submitted policy |

Historical research paths are retained because imports, reports and provenance records depend on them. The [cleanup notes](docs/REPOSITORY_CLEANUP.md) describe removed documentation and how to recover the original snapshot.

## Rules and licences

The [original starter README](docs/STARTER_README.md), [submission guide](docs/SUBMISSION.md), [data contract](docs/DATA_CONTRACT.md) and [FAQ](docs/FAQ.md) preserve the competition instructions. Historical schedules and announcements in those documents are part of the original release.

The supplied kit and data retain their [code](LICENSE) and [synthetic-data](DATA_LICENSE.md) permissions. Scientific claims should be read with their cohort, evidence status and limitations; a result in this simulator is not evidence of real relationship prediction.
