"""Build the extension report and figures from completed recorded artifacts."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results/extended'


def load(name):
    path=RESULTS/name
    summary=path.with_name(path.stem+'.summary.json')
    return json.loads((summary if summary.exists() else path).read_text())
def exists(name):
    path=RESULTS/name
    return path.exists() or path.with_name(path.stem+'.summary.json').exists()
def fmt(x,d=3):return '—' if x is None else f'{x:.{d}f}'
def ci(row):return '['+', '.join(fmt(x) for x in row['ci95'])+']' if row.get('ci95') else '—'
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,row))+' |' for row in rows])


def main():
    dev,sel,confirm=map(load,('development_statistics.json','selection_statistics.json','confirmation_statistics.json'))
    frozen=load('frozen_candidate.json');candidate=frozen['policy'];cfg=frozen['configuration']
    rawdev,rawsel,rawconfirm=map(load,('development.json','selection.json','confirmation.json'))
    assert all(d['complete'] for d in (rawdev,rawsel,rawconfirm))
    assert all(r['valid'] for d in (rawdev,rawsel,rawconfirm) for r in d['episodes'])
    assert rawconfirm['code_hashes']==frozen['code_hashes']
    comp=next(r for r in confirm['comparisons'] if r['policy']==candidate)
    proven=comp['difference']['ci95'][0]>0 and comp['paired_t_p'] is not None and comp['paired_t_p']<.05
    verdict=('The frozen candidate improved the primary score with a positive paired 95% confidence interval on the registered public confirmation families.'
             if proven else 'The registered confirmation does not establish that the frozen candidate improves the primary score over shipped greedy.')
    production=load('production.json');audit=load('audit.json');theory=load('theory.json')
    figs=RESULTS/'figures';figs.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,3,figsize=(14,4.8))
    for ax,data,title in zip(axes,(dev,sel,confirm),('Development: 8 clusters','Selection: 12 clusters','Confirmation: 40 clusters')):
        policies=data['policies']
        names=list(policies) if data is confirm else sorted(policies,key=lambda n:policies[n]['primary']['mean'],reverse=True)[:8]
        if 'greedy' not in names: names[-1]='greedy'
        ys=[policies[n]['primary']['mean'] for n in names]
        errs=[ys[i]-policies[n]['primary']['ci95'][0] for i,n in enumerate(names)]
        ax.barh(names,ys,xerr=errs,color=['#cf753a' if n==candidate else '#407fa3' for n in names],capsize=2)
        ax.invert_yaxis();ax.set_xlabel('Qualified MSMI / 100 arrived');ax.set_title(title)
    fig.suptitle('Policy means with seed-cluster 95% t intervals; development/selection are exploratory')
    fig.tight_layout();fig.savefig(figs/'policy_scores.png',dpi=160);plt.close(fig)
    report=['# Sequential reciprocal matching under uncertainty: audited extension',
            '\n8 October 2026. Synthetic public simulator research. The earlier report is preserved in [research/REPORT_2026-10-07.md](research/REPORT_2026-10-07.md). Its artifacts remain unchanged.']
    report+=['## Result and scope',f'\n{verdict} The selected configuration is `{candidate}`: `{json.dumps(cfg,sort_keys=True)}`. '
             f'Its scenario-balanced score is {fmt(confirm["policies"][candidate]["primary"]["mean"])} MSMI/100, versus '
             f'{fmt(confirm["policies"]["greedy"]["primary"]["mean"])} for greedy. The paired effect is '
             f'{fmt(comp["difference"]["mean"])} MSMI/100, 95% CI {ci(comp["difference"])}, two-sided p={fmt(comp["paired_t_p"],4)}. '
             'This conclusion concerns equal weighting of the six shipped public families, not private engines or real relationships.']
    report+=['The registered interval excludes the targeted +.10 MSMI/100 improvement under its approximate coverage assumptions. Small positive effects remain possible; inferiority and equivalence are not established. No substantially better policy was established. Retain shipped greedy as the supported default rather than adopting this candidate on its development point estimate.']
    report+=['\nThe package replaces arbitrary terminal ranking multipliers with multistage probability estimates, integrates missing soft equality states, shared dyadic effects and actor uncertainty, and tests simpler controls. '
             'It also evaluates querying, general-graph allocation, continuation penalties and component waiting. Posterior approximations require calibration evidence; architecture complexity is not treated as evidence of improvement.']
    counts={k:len(v['episodes']) for k,v in [('development',rawdev),('selection',rawsel),('confirmation',rawconfirm)]}
    report+=['\n'+table(['Experiment','Policies','Seed clusters','Episodes'],[(k,len({r['policy'] for r in v['episodes']}),len({r['seed'] for r in v['episodes']}),len(v['episodes'])) for k,v in [('Development',rawdev),('Selection',rawsel),('Confirmation',rawconfirm)]]),
             '\nReproductions, smoke debugging, calibration replays and production comparisons are additional executions, not additional independent confirmation clusters. Raw episode rows include failures, action digests, request/memory sizes and latency measurements. All registered development, selection and confirmation episodes were valid.']
    report+=['## Audited starting point and simulator agreement',
             f'\nAll {len(audit["reproduction"])} existing reproduction episodes matched previous outcomes and action hashes. '
             'The prior full architecture underperformed greedy on exploratory seeds; prior product improved the fresh-seed point estimate but did not establish superiority. Those seeds remain development evidence and were not reused as untouched confirmation data. '
             'Harmonic fusion is a ranking function rather than a joint success probability. Feasible-edge revelation can be complementary rather than submodular. Global algebraic connectivity can remain zero after useful improvements in disconnected components. Runnable proofs and counterexamples are in [research/EXTENDED_THEORY.md](research/EXTENDED_THEORY.md).',
             '\nActions occur on days 0–59, with 40 observation days. Twelve percent receive an exit day, rather than a daily 12% exit hazard. Hard feasibility requires eleven fields; declines remain permanently unavailable. Endpoint reuse is legal after busy periods, but dyad reuse is forbidden. Availability does not expose future busy-release times or exit days. Qualification requires date within 30 days of assignment and each positive feedback within three days of date. Two positive answers pause members even when these deadlines fail.',
             '\n'+table(['Type','Model use'],[
                 ('Observed','JSON fields/statuses, available flag, assignments, received feedback, query log, day and budget'),
                 ('Latent','Unanswered truth, actor biases/response propensities, shared effects, exits, future arrivals and scheduled outcomes'),
                 ('Public mechanisms','Generator priors, delay supports/distributions, budget/eligibility rules, possible preference regimes'),
                 ('Estimated','Actor posterior moments, regime weights, date rate/delay regime, terminal and pause probabilities'),
                 ('Offline audit only','Fixed-truth oracle probabilities and synthetic controlled interventions; never passed to policy')])]
    report+=['## Probability models and their limits',
             '\nThe integrated scorer computes response, reciprocal acceptance, actual date, both-positive second feedback, pause and qualified terminal probabilities. For fixed true actors and attributes it uses '
             '`q = .78 × .36 × P(date delay≤30) × (r_u r_v)^2 × E_S[σ(a_u+S)σ(a_v+S)σ(s_u+S)σ(s_v+S)]`. '
             'Unknown response propensities use posterior second moments because the same propensity is reused at both stages. Shared S is integrated across all four logits. Actor effects use shrinkage Gaussian approximations; regime updates use a tempered likelihood. These are approximate beliefs, not exact posterior inference.',
             '\nMissing equality patterns are enumerated over at most 16 states. The scorer does not substitute sigmoid of mean soft features. A proved absolute error bound is Var(Z)/(12√3), with no global Jensen direction; tested mean-substitution errors and five-node quadrature convergence are recorded separately in theory/audit artifacts. Five-node Gaussian integration is a numerical approximation. Conditional second-stage prediction accounts for selection by mutual acceptance when updating actor logits.',
             '\nThe simple control uses smoothed complete-funnel frequencies and only trains the terminal funnel on assignments old enough (38 days) to resolve every supported delay. The independent comparator preserves marginal shared-effect variance while removing its common dependence conditional on features/regime. No-learning freezes updates. Pending events never count as observed failures; explicit no-response, rejection, date cancellation, positive feedback and deadline failure have separate labels. Prospective predictions snapshot assignment-time fields.',
             '\nFor the selected simple configuration, the terminal score is the same positive aggregate estimate for every dyad. Normal allocation is greedy in canonical member-ID edge order; updating the common rate cannot change that ranking. This is a control against visible-soft-feature ranking, not a successful learned terminal discriminator. Its executable still computes integrated auxiliary diagnostics and updates actor memory, so simpler scoring does not imply a stripped runtime. Its conditional directional diagnostic probabilities are not factors of its direct empirical joint predictions. Response updates omit pending-event survival likelihood, and missing-feature enumeration uses public priors rather than an exact history-conditioned posterior.',
             '\nAcquisition comparators are FIFO, potential-degree, exact public-generator hard-field entropy, sampled expected maximum matching-value change, two-query lookahead and randomized bundles. The value methods use restricted candidate sets and Monte Carlo outcomes; they are not exact full-belief VoI. Entropy is a comparator, not a presumed reward gain. Permanent-decline pruning applies to every candidate. Introductions always require actual verified eligibility.',
             '\nGeneral-graph blossom maximizes current modeled adjusted weight with an interruptible deadline and legal greedy fallback. Opportunity penalties estimate busy/retirement/alternative losses and are explicitly heuristic. Component batching waits only in specified early components. Uncertainty penalties are sensitivity controls, not calibrated confidence bounds. Full objectives, learning rules, complexity and fallbacks appear in [research/EXTENDED_ALGORITHM.md](research/EXTENDED_ALGORITHM.md).']
    report+=['## Registered statistical design',
             '\n[research/EXPERIMENT_REGISTRY.md](research/EXPERIMENT_REGISTRY.md) records the experiment before new evaluation. Development seeds are 1001–1008; selection seeds 2001–2012; untouched confirmation seeds 3001–3040. The selected code/config hashes were frozen in `results/extended/frozen_candidate.json` before confirmation. No code, parameter or sample-size retuning occurred after selection.',
             '\nSelection used the top four development candidates plus fixed integrated/simple/independent/no-learning controls. Among selection candidates within .05 MSMI/100 of the highest mean, the amended registered rule prefers lower model/query/allocation/waiting complexity. This is an engineering simplicity preference, not evidence of statistical equivalence. The confirmatory comparison is only frozen candidate versus greedy, two-sided alpha=.05; exploratory comparisons use Holm correction.',
             '\nPrior paired seed-cluster SD .204–.208 implies about 34 independent clusters for 80% power to detect +.10 MSMI/100 by normal planning; 40 were fixed in advance. This does not ensure power for smaller effects. Six scenario families sharing a seed are averaged within that seed. The cluster t interval/test is predefined; a 10,000-resample paired seed bootstrap is sensitivity analysis. Rare rewards and public family representativeness limit inference.']
    report+=['\n![Policy scores](results/extended/figures/policy_scores.png)',
             '\n'+table(['Development configuration','Score','Paired difference vs greedy','95% CI','Holm p'],
                        [(name,fmt(dev['policies'][name]['primary']['mean']),fmt(r['difference']['mean']),ci(r['difference']),fmt(r.get('exploratory_holm_p'),4))
                         for r in sorted(dev['comparisons'],key=lambda r:dev['policies'][r['policy']]['primary']['mean'],reverse=True) for name in [r['policy']]]),
             '\n'+table(['Selection configuration','Score','95% cluster CI'],[(n,fmt(r['primary']['mean']),ci(r['primary'])) for n,r in sorted(sel['policies'].items(),key=lambda kv:kv[1]['primary']['mean'],reverse=True)])]
    report+=['## Frozen confirmation',
             '\n'+table(['Policy','Score','Coverage','Mutual acceptance / assigned','Dates / mutual acceptance','Ask cost'],
                         [(n,fmt(r['primary']['mean']),fmt(r['metrics']['coverage']['mean']),fmt(r['metrics']['mutual_acceptance_rate']['mean']),fmt(r['metrics']['date_completion_rate']['mean']),fmt(r['metrics']['ask_cost']['mean'],1)) for n,r in confirm['policies'].items()]),
             f'\nPaired bootstrap sensitivity interval: {comp["paired_seed_bootstrap_ci95"]}. Standardized paired effect: {fmt(comp["standardized_paired_effect"])}. '
             'Rates are means of episode ratios; zero denominators yield zero and raw denominators are retained. Secondary metrics have no separate confirmatory superiority claim.',
             '\n'+table(['Family',candidate,'Greedy','Difference'],[(f,fmt(confirm['policies'][candidate]['scenario_metrics'][f]['msmi_per_100_arrived_members']['mean']),fmt(confirm['policies']['greedy']['scenario_metrics'][f]['msmi_per_100_arrived_members']['mean']),fmt(confirm['policies'][candidate]['scenario_metrics'][f]['msmi_per_100_arrived_members']['mean']-confirm['policies']['greedy']['scenario_metrics'][f]['msmi_per_100_arrived_members']['mean'])) for f in ('development','sparse','cold_start','delayed','shift','drift')])]
    if exists('audit_confirmation_calibration.json'):
        ca=load('audit_confirmation_calibration.json');cal=ca['calibration_by_policy'][candidate]
        report+=['## Calibration, mechanisms and failures',
                 '\nConfirmation calibration uses assignment-time predictions and fully resolved follow-up. Reliability uncertainty resamples seed clusters; per-family and missingness slices are in the raw audit. This is evaluation after freezing, not recalibration. Oracle curves are offline reference integrals, not evaluated oracle policies.',
                 '\n'+table(['Stage','Assignments','Mean prediction','Observed','Log loss','Brier','AUC'],[(stage,r.get('n'),fmt(r.get('predicted_mean')),fmt(r.get('observed_mean')),fmt(r.get('log_loss')),fmt(r.get('brier')),fmt(r.get('roc_auc'))) for stage,r in cal.items()]),
                 f'\nTerminal prediction is {100*cal["terminal"]["predicted_mean"]:.3f}% versus {100*cal["terminal"]["observed_mean"]:.3f}% observed. Seed-balanced observed-minus-predicted error is {fmt(cal["terminal"]["signed_observed_minus_predicted_by_seed"]["mean"],6)}, 95% CI {ci(cal["terminal"]["signed_observed_minus_predicted_by_seed"])}: the selected cohort shows overforecasting. AUC near .5 does not demonstrate useful discrimination. Cold start is the only family with observed terminal rate above its forecast. With fewer than 20 prior feedback observations the forecast is constant .0117 and AUC .5; the richer-history slice has forecast .011431, observed .008127 and AUC .505, providing no demonstrated adaptation benefit. Missingness bin "4" means at least four missing soft fields. Small and zero-event bins do not establish robustness.',
                 '\nConfirmation totals are 18,133 introductions, 2,434 mutual accepts, 1,912 dates and 159 qualified outcomes for simple, versus 17,954, 2,428, 1,849 and 179 for greedy. More dates did not produce more terminal reward. Of 489 simple both-positive outcomes, 330 fail date or feedback qualification; the audit key `late_feedback_both_yes` combines these deadline failures and cannot attribute all to feedback alone.',
                 f'\n![Terminal and funnel reliability](results/extended/audit_confirmation_calibration_{candidate}.png)']
    if exists('audit_development_calibration.json'):
        dc=load('audit_development_calibration.json')
        report+=['\nDevelopment terminal calibration (each policy selects its own assignment population):',
                 '\n'+table(['Policy','Assignments','Predicted rate','Observed rate','Log loss','Brier','AUC'],
                            [(n,r['terminal']['n'],fmt(r['terminal']['predicted_mean'],4),fmt(r['terminal']['observed_mean'],4),fmt(r['terminal']['log_loss'],5),fmt(r['terminal']['brier'],5),fmt(r['terminal']['roc_auc'])) for n,r in dc['calibration_by_policy'].items()]),
                 '\nThese proper-score differences are not model comparisons on identical examples. The common-cohort audit below replays greedy assignments and snapshots each model on the same observed histories. Terminal events remain rare; all-zero or all-one reliability bins do not receive spuriously certain bootstrap intervals.']
    if exists('audit_common_cohort_calibration.json'):
        cc=load('audit_common_cohort_calibration.json')
        report+=['\nThe matched-cohort model audit replays 48 greedy development episodes and scores 3,567 identical prospective assignments. Terminal loss differences are small and all paired seed-cluster intervals include zero; no terminal-calibration superiority is established. The integrated response-stage control improves on the aggregate simple response predictor in an exploratory comparison adjusted over 30 stage/metric/model tests. This does not establish terminal or sequential-reward improvement.',
                 '\n'+table(['Model','Family-balanced terminal log loss','Family-balanced terminal Brier','Pooled terminal AUC'],
                            [(n,fmt(r['terminal']['log_loss']['mean'],6),fmt(r['terminal']['brier']['mean'],6),fmt(cc['calibration_by_model'][n]['terminal']['roc_auc'])) for n,r in cc['family_balanced_cluster_loss_summaries'].items()]),
                 '\nPaired proper-loss estimates, 95% cluster intervals and Holm adjustments are in `results/extended/audit_common_cohort_calibration.json`. Model assessment uses the same examples; this is not a causal or confirmatory policy-reward claim.']
    if (RESULTS/'mechanisms.json').exists():
        me=load('mechanisms.json')
        report+=['\nMechanism analysis, representative trajectories and descriptive synthetic demographic coverage are recorded in `results/extended/mechanisms.json` and [research/EXTENDED_EMPIRICAL.md](research/EXTENDED_EMPIRICAL.md). '
                 'Conditional oracle-probability sums along realized assignments measure descriptive quality with less outcome noise; adaptation/retirement means they are not a causal policy effect or an oracle-policy score. Controlled toy acquisition and dynamic interventions establish only their explicitly specified mechanisms.']
        report+=['Across all 48 development worlds, simple and greedy have identical FIFO queries and mean ask cost 200.375. Simple averages 75.479 introductions versus 74.313, repeat endpoint assignments 85.938 versus 83.667, busy duration 9.436 versus 9.732 days, and served members 65.021 versus 64.958. Oracle conditional terminal-probability sums are .713944 versus .714302 per episode, with slightly lower per-assignment quality for simple. These descriptive changes provide no evidence of better clarification or underlying conditional quality.',
                 'The development point gain is 45 versus 40 qualified outcomes despite 87 versus 92 both-positive pauses. Feedback deadline failures are 42 versus 52; greedy also has one overlapping late-date failure. Favorable deadline draws are a plausible contributor to the gain, not evidence of improved delay prediction. Seed 1001 favors simple by .25 MSMI/100: a day-12 dyad ending 8c7752/6a5af1 qualifies in both development and drift, sharing a draw. Seed 1006 favors greedy by .25: its additional day-44 dyad ending 627689/a459b1 qualifies in both families. Complete events, dyads and graph replays are retained in the mechanism artifact.',
                 '![Descriptive mechanism comparisons](results/extended/mechanisms.png)',
                 'Confirmation synthetic coverage is 33.69% for men, 33.96% for women and 36.38% for nonbinary members; ages 21–29, 30–39 and 40–46 have 32.94%, 35.16% and 33.83% coverage. These correlated synthetic episode-member counts are descriptive associations, without a demographic causal intervention or a confirmed coverage improvement.']
    interactions=load('interactions.json')
    report+=['\n'+table(['Exploratory interaction','Difference in differences','95% CI','Holm p'],[(r['contrast'],fmt(r['estimate']['mean']),ci(r['estimate']),fmt(r.get('holm_p'),4)) for r in interactions['contrasts']]),
             '\nThese contrasts compare the new architecture with its own scoring, querying, allocation and waiting controls. Eight development clusters do not establish absence of interactions.']
    report+=['## Exact small-instance results and mathematical classification',
             '\n'+table(['Instance','Exact DP','Greedy','Blossom','Batching','Reservation'],
                         [[r['instance']['name']]+[fmt(r['policies'][p]['expected_reward']) for p in ('exact_dp','greedy','blossom','batching','reservation')] for r in theory['exact_dynamic_benchmarks']]),
             '\nThe toy MDPs enumerate all legal matchings and use rational Bellman recursion with specified arrival/exit schedules, busy times and retirement probabilities. They do not solve the full partially observed simulator. One instance shows immediate blossom losing to waiting; another shows independently summed continuation penalties double-counting a future edge. General-graph LP duals require odd-set multipliers. No universal monotonicity, separability or indexability is claimed.',
             '\nUnder fresh independent simulator draws, adapted legal actions and complete follow-up, expected qualified reward equals .36 times expected positive-pause dyads in standard families, or .36×671/686 in delayed. Pause endpoints are disjoint, so expected reward is also that factor times half the expected positive-pause members. This is not a realized fixed-seed ratio or a conditional binomial theorem; an adaptive exact counterexample distinguishes these claims. Pure FIFO bundle queries have identical schedules across legal matching policies sharing the same world, budget and observation order, provided no soft asks or alternative priorities intervene. This explains query equality, not reward equality.',
             '\n'+table(['Evidence class','Established scope'],[
                 ('Proven mathematical results','Joint probability bounds; absolute missing-feature approximation bound; scoped expected reward/pause identity and FIFO invariance; complementarity, connectivity and nonseparable continuation counterexamples'),
                 ('Exact simulator calculations','Delay enumeration, .36 feedback deadline factor, delayed date tail 15/686, maximum follow-up timing'),
                 ('Exact simplified solutions','Five rational finite toy MDPs and exhaustive allocation benchmarks'),
                 ('Empirical findings','Registered raw episode comparisons, calibration, latency, resource enforcement, descriptive coverage'),
                 ('Approximation assumptions','Independent posterior actor effects, Gaussian shrinkage, tempered regime likelihood, quadrature, restricted sampled VoI and continuation proxies'),
                 ('Unvalidated hypotheses','Optimal full-belief planning, robust private-engine transfer, reliable tiny-episode regime identification, causal demographic mechanisms')])]
    pr=production['replay'];lim=production['limits']
    report+=['## Production and reproducibility',
             '\nThe original frozen development code failed one actual Docker dense-history timeout test and exposed division by zero on malformed memory. Both failures are preserved. A guard-only amendment catches arithmetic errors and interrupts optimized decision execution after seven seconds, then uses observation-only FIFO or first-fit legal actions with reset memory. It changes no model, update or decision objective. All 132 ordinary first-seed development episodes retain exactly the same actions/outcomes after the guard patch; selection and confirmation use the guarded version. All twelve final host stress cases and all four proposal container stress cases return valid protocol responses. Parsing, output and fallback are outside the alarm; tested 200-member compliance is not a universal ten-second bound for arbitrary markets or machines.',
             f'\nThe selected executable was compared over 60 action days plus follow-up in process, subprocess and offline Docker. Semantic action differences: {len(pr["semantic_differences"])}; ordering-only differences: {len(pr["ordering_only_differences"])}. '
             'Outcome metrics agree. Byte digest agreement is recorded separately and is not inferred from semantic equality.',
             f'\nEffective container limits: `{lim["cpu.max"]}` CPU quota/period; `{lim["memory.max"]}` memory bytes; `{lim["pids.max"]}` PIDs; read-only root write blocked; uid {lim["uid"]}; only loopback up. '
             f'Image size {lim["image_size_bytes"]:,} bytes, below 2 GiB. Maximum compared invocation seconds: {pr["max_call_seconds"]}. '
             'The resource limits are enforced by the evaluator container flags, not inferred from host timings.',
             '\n'+table(['Policy','Mean call ms','Mean episode p95 ms','Mean episode p99 ms','Maximum call ms','Peak memory bytes','Peak request bytes'],
                         [(n,fmt(r['metrics']['mean_inference_ms']['mean'],2),fmt(1000*r['metrics']['latency_p95_seconds']['mean'],2),fmt(1000*r['metrics']['latency_p99_seconds']['mean'],2),fmt(1000*r['maxima']['peak_latency_seconds'],2),r['maxima']['peak_memory_bytes'],r['maxima']['peak_request_bytes']) for n,r in confirm['policies'].items()]),
             '\nIn-process latency includes strict JSON roundtrips but excludes process startup; `results/extended/subprocess.json` and production comparisons record actual startup latency. Memory is strictly below one MiB. Tests cover empty/no-edge pools, declines, exhausted budgets, malformed/nonfinite/oversized requests, pending feedback, solver failures and actual timed interruption. Original suite: 22 passed; extended policy and guard suites: 28 passed; public checksums verified. Deadline/error fallback can sacrifice reward and resets learned memory.',
             '\nReproduce with the exact configs/seeds in the registry and frozen artifact:',
             '\n```bash\npython3 -m venv .venv\n.venv/bin/python -m pip install -r requirements-research.txt\n.venv/bin/python -m unittest -v\nEXTENDED_SAFETY_TEST_TARGET=actual .venv/bin/python -m unittest -v research.test_extended_policy research.test_extended_safety\n.venv/bin/python -m research.extended_theory\n.venv/bin/python -m research.extended_audit\n# Full exact commands/configs are in results/extended/experiment_commands.json\n.venv/bin/python -m research.extended_analysis results/extended/confirmation.json --confirmatory '+candidate+'\ndocker build -f Dockerfile.extended -t sequential-extended:1.0 .\n.venv/bin/python -m research.extended_production --config '+repr(json.dumps(cfg))+'\n.venv/bin/python -m research.extended_report\n.venv/bin/python -m research.extended_manifest\n```',
             '\nRaw trace archives restore the original `results/extended/*_traces` paths. The provenance manifest records source/artifact hashes, experiment partitions/configurations, package versions, original git head and working-tree status; the existing uncommitted research is preserved. Verified primary literature and applicability caveats are in [docs/REFERENCES.md](docs/REFERENCES.md).']
    report+=['The selected host executable is `.venv/bin/python extended_policy.py --config \'{"model":"simple"}\'`. The selected offline container invocation is `docker run --rm -i --network none --cpus 2 --memory 1g --pids-limit 64 --read-only sequential-extended:1.0 --config \'{"model":"simple"}\' < request.json`. The bare executable/image uses the integrated default and is a different candidate.',
             'Detailed source-version-aware instructions, archive restoration and analysis commands are in [research/EXTENDED_REPRODUCTION.md](research/EXTENDED_REPRODUCTION.md). Development used the archived original executable; selection and confirmation used the frozen guarded source. Do not rerun the completed orchestration over original results. Exact environment pins are in `requirements-research.lock.txt`; Docker uses Python 3.12.7 and NetworkX 3.7. Independent final [statistical](research/FINAL_STATISTICAL_REVIEW.md), [mathematical](research/FINAL_THEORY_REVIEW.md) and [package](research/FINAL_PACKAGE_REVIEW.md) reviews found no blocking numerical or scoped mathematical error. Packaging fixes requested by those reviews are recorded in the reproduction guide. The previous verified bibliography was recovered and hash-checked as `research/REFERENCES_2026-10-07.md`.']
    (ROOT/'REPORT.md').write_text('\n\n'.join(item.strip() for item in report)+'\n')
    print('Report built:',candidate,'confirmatory superiority=',proven)


if __name__=='__main__':main()
