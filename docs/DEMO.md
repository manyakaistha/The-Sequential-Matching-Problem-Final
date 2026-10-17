# Public demo deployment

The public presentation branch is
[`cleanup/repository-presentation`](https://github.com/manyakaistha/The-Sequential-Matching-Problem-Final/tree/cleanup/repository-presentation).
The service definition lives in [`render.yaml`](../render.yaml) and targets one
free Python Web Service named `sequential-matching-demo`.

## Render settings

Connect the final repository, select the cleanup branch, and apply the Blueprint
in the repository root. The native commands are:

```text
Build:  python -m pip install -r demo/requirements.txt
Start:  python -m uvicorn demo.app:app --host 0.0.0.0 --port $PORT --workers 1
Health: /healthz
```

`runtime.txt` selects Python 3.13.5. The app needs no secret, database,
persistent disk, model download or external API. The root policy `Dockerfile`
is deliberately unchanged; it remains the assessed CLI image rather than an
HTTP server.

Render's free service may sleep after inactivity, so the first visit can show a
cold-start delay. Run state is intentionally in memory and expires after about
20 minutes of inactivity (or after the absolute lifetime); a redeploy or sleep
can therefore require a fresh run.

## Reviewer journey

1. Open the HTTPS service and choose **Start the public preset**.
2. In **Available members**, select a row with missing hard fields and read the translated kit reason codes in the inspector.
3. Use **Next phase** to apply Greedy's clarification requests, then inspect the refreshed public state and selected batch.
4. Advance a few days to see introductions, released responses and dates appear on the timeline. **Finish episode** runs bounded requests through the 40-day follow-up.
5. Read the funnel and coverage with their provisional/final labels, download the allowlisted public export, or open the corrected final report.

The **Compare controls** tab runs Greedy, No clarification and Random feasible
on three isolated copies of the same documented seed-101 development preset.
Those numbers describe one illustrative realization; they are separate from the
historical aggregate evidence in `final_report/data/`.

## Operational limits

The run store is process-local, capped at eight active runs by default and
guarded by one transition slot. Requests use an optimistic revision and an
idempotency key so double clicks and retry races cannot advance a day twice.
The service exposes fixed presets only; visitors cannot submit seeds, arbitrary
population sizes, code, paths or budgets. Export files contain settings,
released events and metrics only.

No live URL is recorded here until a Render account actually provisions the
service. The source branch and Blueprint are the reproducible deployment
record.
