# Clone or update this development repository

Large evidence JSON files use Git LFS. Install Git and Git LFS before cloning, then run:

```bash
git lfs install
git clone https://github.com/manyakaistha/the-sequential-matching-problem-dev-repo-final.git
cd the-sequential-matching-problem-dev-repo-final
git lfs pull
```

For an existing checkout:

```bash
git pull --ff-only origin main
git lfs pull
```

To use the cleanup branch rather than `main`:

```bash
git fetch origin
git switch cleanup/repository-presentation
git pull --ff-only origin cleanup/repository-presentation
git lfs pull
```

Open [the final report](../final_report/REPORT.md). Its adjacent `assets/` directory contains the plots, and `final_report/data/` contains the derived analysis tables. See [the report README](../final_report/README.md) for rebuilding figures from the saved evidence.

The research source, registrations, saved analyses, reviews and nonignored artifacts are versioned. Existing ignore rules continue to exclude virtual environments, caches, temporary files, raw attempt/commit directories and large raw campaign archives. Those excluded artifacts remain on the original results drive; a clone does not restore them. Historical archive-aware audits may require that separate drive. Git LFS tracks the large JSON files listed in `.gitattributes` without changing their checked-out content.

Research is complete. The commands above retrieve the repository; they do not run experiments.
