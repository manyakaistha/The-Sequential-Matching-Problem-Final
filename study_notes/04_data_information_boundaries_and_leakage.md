# 04. Data Contracts, Information Boundaries & Preventing Leakage

This document establishes the structural anatomy of the development dataset, delineates the strict information boundaries between public observations and hidden generative state, exposes four distinct categories of data leakage, and analyzes the semantics of synthetic conversation records.

---

## 1. Disambiguation: "PS" in Information Boundaries

* **PS (Problem Statement)**: Section 4 and 9 of [`PROBLEM_STATEMENT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/PROBLEM_STATEMENT.md#L45-L80) governing data provenance, non-leakage rules, and offline evaluation constraints.
* **PS (Parametric Scorer)**: The scoring policy models (`PS_sim`, `PS_emp`, `PS_flat`) evaluated in [`final_report/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md).

---

## 2. Anatomy of the Development Dataset

The participant dataset contains **2,000 synthetic adults** organized across **ten independent pools** of 200 people each. All data represents a static snapshot frozen at **Simulation Day 30**.

```
data/
├── data_manifest.json          <-- Pool manifest, seeds & split definitions
├── data_checksums.json         <-- SHA-256 integrity hashes for all files
└── data/
    ├── public_01/ ... public_10/
        ├── state.json          <-- Complete observable JSON snapshot at Day 30
        ├── members.jsonl       <-- Member records, field statuses & observed days
        ├── questionnaires.jsonl<-- Human-readable questionnaire representation
        ├── conversations.jsonl <-- Short authored conversation fragments
        ├── introductions.jsonl <-- Introductions assigned between Day 0 and 30
        ├── feedback.jsonl      <-- Feedback events observed on or before Day 30
        └── members_flat.csv    <-- Flattened exploration view (omits timing/status!)
```

### 2.1 Independent Disjoint Pool Splits
As specified in [`data_manifest.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/data_manifest.json):
* **Training Pools (6)**: `public_01` through `public_06` (1,200 members).
* **Validation Pools (2)**: `public_07` and `public_08` (400 members).
* **Development-Test Pools (2)**: `public_09` and `public_10` (400 members).

```
   ┌────────────────────────────────────────────────────────────────────────┐
   │                       Dataset Split Structure                          │
   ├───────────────────────────────┬────────────────────────┬───────────────┤
   │          TRAINING             │       VALIDATION       │   DEV-TEST    │
   │  public_01 ... public_06      │  public_07, public_08  │  09, 10       │
   │     (1,200 members)           │     (400 members)      │ (400 members) │
   └───────────────────────────────┴────────────────────────┴───────────────┘
```

**Rule of Disjoint Splitting**: Model training and evaluation must **always** be split by entire pools. Randomly partitioning rows across `members.jsonl` or `introductions.jsonl` constitutes catastrophic leakage, as members and historical interactions within a pool are interconnected.

---

## 3. Four Categories of Data Leakage & Information Boundaries

### Layer 1: The Question
What constitutes illegitimate information leakage in sequential matching, and how can an offline policy inadvertently exploit future or privileged simulation state?

### Layer 2: Intuition
A sequential decision system operating in real time only observes events that have occurred in the past. When historical logs or static datasets are used for offline training, future information easily bleeds backward into earlier decision points unless strict temporal and structural firewalls are maintained.

```
       SIMULATION TIMELINE:
       Day 0           Day 8             Day 20             Day 30 (Snapshot)
         ├───────────────┼─────────────────┼──────────────────┤
         │               ▲                 ▲                  │
                         │                 │
                   Introduction        Clarification
                     Assigned            Revealed
                         │                 │
                         └─────────────────┘
                   TEMPORAL LEAKAGE: Training on Day 30 profile
                   to predict Day 8 introduction response!
```

---

### Category 1: Temporal Leakage (Snapshot vs. Rollout)
* **The Vulnerability**: In the Day 30 snapshot files (`members.jsonl`), a member's `fields` dictionary contains all answers observed up to Day 30. However, an introduction recorded in `introductions.jsonl` may have been assigned on **Day 8**. On Day 8, the member may have had multiple unobserved fields that were only clarified on Day 20.
* **The Violation**: Attaching Day 30 profile features to Day 8 introduction rows during model training creates **temporal leakage**. The model learns to predict compatibility using information that the policy could not have observed when the decision was made.
* **The Correction**: Training datasets must be constructed by executing step-by-step simulator rollouts, saving pre-decision feature snapshots at the exact moment of assignment ($t = \text{assigned\_day}$).

---

### Category 2: Availability & Exit Leakage
* **The Vulnerability**: In the simulator generator, each member has a latent departure time:
  ```python
  'exit_day': r.randint(22, 60) if r.random() < 0.12 else 10000
  ```
* **The Violation**: If an offline model inspects whether a member was available on Day 40 to decide whether to match them on Day 10, it exploits unobserved future churn.
* **The Invariant**: A policy can only query `m['available']` from the current day's `state.json`. Future departure is completely unobservable.

---

### Category 3: Hidden Generative State Leakage
* **The Vulnerability**: When inspecting `kit.py` source code, participants discover internal generator variables:
  * `m['truth']`: The ground truth answers before missingness masking.
  * `m['bias']`: The latent individual acceptance propensity $\alpha_i \sim \mathcal{N}(0, 0.7^2)$.
  * `m['second_bias']`: Latent second-meeting propensity $\sim \mathcal{N}(0, 0.5^2)$.
  * `m['response_rate']`: Latent responsiveness $\rho_i \in [0.55, 0.98]$.
* **The Violation**: Directly reading `m['truth']`, accessing private attributes through Python introspection, or using generator PRNG seeds to reverse-engineer latent variables is an explicit violation of [`PROBLEM_STATEMENT.md` §11](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/PROBLEM_STATEMENT.md#L210-L225) and results in immediate disqualification.
* **The Invariant**: Only fields present in public `state.json` may enter decision policies.

---

### Category 4: Target & Propensity Confounding (Selection Bias)
* **The Vulnerability**: Historical introductions in `introductions.jsonl` were generated by an unknown logging policy (the baseline rollout).
* **The Invariant in Data Contract**: As explicitly stated in [`docs/DATA_CONTRACT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/docs/DATA_CONTRACT.md#L45-L55):
  ```json
  "logging_policy": "baseline_or_submitted_policy",
  "propensity": null
  ```
* **The Fallacy**: Historical introductions are **not a randomized control trial (RCT)**. The pairs present in the log were selected because they were feasible and had matching soft attributes. Unobserved pairs were systematically excluded. Because `propensity` is `null`, policies cannot perform unbiased Inverse Propensity Scoring (IPS).

---

## 4. Synthetic Conversation Fragments & NLP Boundaries

### Layer 1: The Question
Can the text records in `conversations.jsonl` be used to train Large Language Models (LLMs) or sentiment classifiers to predict genuine human romantic compatibility?

### Layer 2: Intuition
In natural language processing, practitioners frequently assume that conversational transcripts contain subtle psychological markers, emotional nuances, and conversational chemistry. However, in this benchmark, the conversation fragments are **synthetic rule-based template reflections** of categorical questionnaire choices. They contain zero linguistic signal beyond the categorical field values already present in `fields`.

### Layer 3: Minimal Concrete Example: Template Mapping
Inspecting [`build_public_data.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/build_public_data.py#L22-L37) reveals the exact template generator:

```python
# From build_public_data.py: conversation()
def conversation(m):
    f = m['fields']
    msgs = []
    prompts = {
        'relationship_goal': 'What are you hoping to find?', 
        'relationship_pace': 'What pace feels comfortable?',
        'lifestyle': 'How do you tend to spend free time?',
        'conversations': 'What kinds of conversation do you enjoy?'
    }
    answers = {
        'long_term': 'I would like to build a lasting relationship.',
        'exploring': 'I am still working out what I want.',
        'slow': 'I prefer to get to know someone gradually.',
        'steady': 'A steady pace suits me.',
        'quick': 'I am comfortable meeting fairly soon.',
        'quiet': 'I usually prefer a quiet evening.',
        'mixed': 'I like a mixture of quiet time and seeing people.',
        'social': 'I enjoy having plans with people.',
        'ideas': 'I enjoy talking about ideas.',
        'stories': 'I like hearing the stories behind things.',
        'practical': 'I enjoy working through practical questions.',
        'playful': 'I like a playful conversation.'
    }
    for k, p in prompts.items():
        if f[k] is not None:
            msgs += [
                {'role': 'assistant', 'content': p},
                {'role': 'user', 'content': answers[f[k]]}
            ]
    return {
        'member_id': m['member_id'], 
        'synthetic': True, 
        'style': 'authored_templates_not_real_transcripts',
        'observed_day': 30, 
        'messages': msgs
    }
```

### Layer 4: Formal Proof of Information Equivalence
Let $T(m)$ be the generated conversation transcript for member $m$, and let $f_{\text{soft}}(m) \in \prod_{k \in \mathcal{K}_{\text{soft}}} (\Omega_k \cup \{\emptyset\})$ be the vector of observed soft attributes.
Because the mapping $\psi: \Omega_k \to \text{String}$ is an injection, there exists a deterministic inverse $\psi^{-1}$ such that:

$$H(f_{\text{soft}}(m) \mid T(m)) = 0 \quad \text{and} \quad H(T(m) \mid f_{\text{soft}}(m)) = 0.$$

Where $H(\cdot \mid \cdot)$ is conditional Shannon entropy.
* **Theorem**: The conversation transcript $T(m)$ carries **strictly zero additional mutual information** about member preferences, mutual acceptance, or date outcomes beyond the discrete categorical fields:
  $$I(T(m); Y \mid f_{\text{soft}}(m)) = 0.$$

### Layer 5: Operational & Scientific Implications
1. **No Psychological Inference**: Training an LLM, BERT transformer, or embedding model on `conversations.jsonl` does not benchmark psychological understanding or conversational rapport. It merely constructs an inefficient, computationally expensive lookup table for discrete categorical fields.
2. **Evaluation Environment Prohibition**: The assessed evaluation environment allows **2 CPU cores and 1 GiB RAM with zero GPU acceleration**. Attempting to run transformer models inside the container will cause immediate process timeout ($> 10.0$s) or memory exhaustion, resulting in total disqualification.
3. **Valid Use Case**: Conversation fragments are provided exclusively to test application input pipelines and schema parsers for real-world interface adapters.

---

## 5. Right-Censoring & Missingness Semantics

### 5.1 Right-Censoring vs. Negative Preference
At any evaluation snapshot $t$, unresolved introductions exist whose observation window has not concluded:

```
Introduction Assigned (Day 25)              Day 30 (Snapshot)            Day 32 (Deadline)
              ├────────────────────────────────────┼─────────────────────────────┤
              ▲                                    ▲                             ▲
         Intro Made                         Snapshot Taken               Response Arrives
                                         (STATUS: PENDING!)              (y = 'yes')
```

* **Right-Censored Introduction**: An introduction assigned on Day 25 with no response recorded by Day 30 is **pending** (`response_deadline_day = 32`).
* **The Misclassification Error**: Labeling a pending introduction as "declined" or "negative" creates severe negative bias in training datasets.
* **Rule**: Introductions must only be labeled after their full response or date observation window has expired.

### 5.2 Field Missingness: `not_asked` vs. `declined`
The data contract distinguishes missingness mechanisms:
* `'not_asked'`: The question has never been posed. A clarification ask can reveal the underlying ground truth if disclosed.
* `'declined'`: The member explicitly refused to provide the information.
  * In [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py#L125-L130), asking about a declined field will **never** reveal truth. The status remains `'declined'` and the value remains `None`.
  * **Critical Planning Invariant**: In [`final_report/REPORT.md` §9](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md#L285-L310), **$100.00\%$ of member-episodes who declined a hard field remained unserved** throughout the entire simulation! A decline on a hard field creates an insurmountable barrier to introduction eligibility under v1.0.0 rules.

See [Figure 9: Demographic and Information Status Access Diagnostics](assets/09_access_subgroups.png).

---

## 6. Synthesis: The Complete Verification Protocol

Before submitting or evaluating any policy implementation, run the official offline verification sequence from the project root:

```bash
# 1. Run unit test suite
python -m unittest -v

# 2. Verify dataset checksums and schema integrity
python verify_data.py

# 3. Test local policy execution across public seeds
python evaluate.py --seeds 101,102,103 --variants all --output results/check.json

# 4. Build and test isolated Docker container
docker build -t sequential-policy:submission .
python evaluate.py --image sequential-policy:submission --seeds 101 --output results/container_check.json
```

---

*This concludes the foundational study notes on The Sequential Matching Problem. For empirical experiment logs, calibration curves, and robustness analyses, refer to [`final_report/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md) and the figures in [`study_notes/assets/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets).*
