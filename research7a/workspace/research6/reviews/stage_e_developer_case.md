# Stage E developer case: confirmatory outcome and concession

Author: acquisition developer (`flash`, medium); date: 2026-10-11.
Subject: Post-confirmation assessment of N3_two following frozen confirmation across 571 untouched clusters (140001–140571).

## 1. Summary of confirmatory findings
- **Performance vs G on Stage E**:
  - Across 571 untouched seed clusters (6,852 episodes), `N3_two` achieved a sample mean difference of **+0.003211 MSMI/100** vs G (SE 0.010715, paired SD 0.256047).
  - Primary 99% paired-t confidence interval: **[-0.024483, +0.030904]**.
  - Two-sided p-value: **0.764559**.
  - Nominal 95% paired-t confidence interval: **[-0.017835, +0.024257]**.
- **Trajectory across research stages**:
  - Stage B (screening, n=40): +0.03333 MSMI/100
  - Stage C (replication, n=60): +0.04306 MSMI/100
  - Stage D (selection, n=80): +0.040625 MSMI/100
  - Stage E (confirmation, n=571): **+0.003211 MSMI/100**

## 2. Mechanistic diagnosis of effect attenuation
- The breakdown across scenario families in Stage E reveals the exact structural mechanism:
  - `cold_start`: **+0.03415** (positive impact where upfront query coordination discovers early compatible pairs).
  - `delayed`: **-0.03415** (exact offsetting negative impact where upfront query coordination spends budget ahead of feedback that arrives too late to be acted upon).
  - `development`: **+0.01226**
  - `sparse`: **-0.00263**
  - `shift`: **+0.00525**
  - `drift`: **+0.00438**
- In the balanced six-scenario distribution, the benefits in early-feedback or dense scenarios are perfectly cancelled out by losses in delayed-feedback scenarios.
- Static, unconditional query coordination does not know whether feedback will be timely or delayed, and therefore cannot beat the simple adaptive flow of greedy asking.

## 3. Concession
The developer formally concedes that `N3_two` does not establish confirmatory superiority over `G`. The pre-registered lower bound requirement ($CI_{99\%} \text{ lower} > 0$) was not met. The shipped greedy baseline `G` is retained.
