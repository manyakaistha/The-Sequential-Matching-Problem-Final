# Prospective snapshot and calibration contract

Each raw trajectory stores assignment-time `member_a`, `member_b`, assigned day,
dyad IDs, public prior-feedback count and an auxiliary `prediction`. Member fields
and timestamps are captured before assignment/outcomes. Completed public events
are stored separately for retrospective label resolution after day100. No hidden
actors, features, scheduled outcomes, exit/release times or scenario labels enter
candidate features.

The stored `prediction` is **not the candidate's forecast or ranking score**.
The frozen runner calls inherited `predict_funnel` with empty memory and
`learning=False`. That auxiliary model mixes three regimes equally (1/3 each),
uses its prior date/delay values and inherited approximation. It is distinct from
the new population scorer's six-family prior mixture (4/6 normal,1/6 shift,1/6
drift) with coupled delayed-family qualification. The auxiliary diagnostic is
computed only by offline recorder after actions; it never reaches policy inputs,
returned memory or score selection. Its recording cost affects episode wall
time, but is outside measured inference-call timing.

Independent prediction audits reconstruct labels and **recompute** each named
model forecast from the identical prospective observed examples and prior public
events. They do not treat stored diagnostic values as forecasts for every policy.
Public response histories are filtered by observed day at assignment, and fields
disclosed later never replace the snapshot. Fixed offline coefficients use only
the registered old training partition; calibration evaluation fits no model.

Qualified labels require actual date within assignment+30 and both yes seconds
within date+3. Pending is not a negative; full100day follow-up resolves every
supported event. Stage-conditional scores use only appropriate eligible examples;
assignment weighting, within-seed weighting and family weighting are explicitly
identified. Entire seeds, not individual assignments, form uncertainty clusters.

Oracle audits may reconstruct privileged worlds in separate scripts. Their
information boundaries and probabilities are explicitly labeled, cannot be
imported by candidate inference, and are not permissible training observations.
