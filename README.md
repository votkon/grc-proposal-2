# GRC Proposal #2

## Overview

This is the second restitution proposal from the Gonka Restitution Committee (GRC). It is also the largest proposal to date, covering **3 accepted restitution cases** across multiple epochs — compared to a single case in the previous proposal.

GRC has recently refreshed its membership: the committee now includes developers from **Gonka Labs** and **Inc4**, broadening technical expertise and validation capacity.

---

## Cases

### Case 1 — Epoch 247: Inactive Status Mid-Epoch (Rejected)

Nine participants served inferences with low miss rates (≤ 3.1%) but received zero rewards in epoch 247 after their status flipped from ACTIVE to INACTIVE during the epoch. A restitution case was filed based on the traffic they served.

After investigation, validators were unable to establish a clear and reproducible causal link between the claimed mechanism and the observed reward outcomes. The victim list selection logic could not be verified against on-chain data, and similar-looking cases not included in the list raised further questions. The case was **rejected** for insufficient proof of a defined protocol-level issue.

---

### Case 2 — Epochs 249–253: Preserver Weight Double-Scaling Bug

**Status: Accepted** | **30,318.50 GNK** | [Source](https://github.com/gonkalabs/GRC-e247-preserver-audit)

Following the v0.2.12 network upgrade, nodes in the Qwen subgroup that were sampled as preserved nodes had their `MLNodeInfo.PocWeight` stored in pre-scaled units. Post-upgrade code treated these stale values as raw nonces and re-applied the WeightScaleFactor (≈0.36), causing double-scaling. Affected nodes had their consensus weight reduced to approximately 36% of the intended level for every epoch in which they remained "stuck" — until they re-ran a fresh Proof of Compute (PoC) validation.

This resulted in proportionally reduced PoC rewards across multiple epochs. **34 (participant, node) pairs** were identified. The fix (PR #1089) introduced episode-scoped preservation and refined reward logic.

---

### Case 3 — Epochs 248, 249 & 250: Epoch Loss Compensation

**Status: Accepted** | **217,612.83 GNK**

This case consolidates four related restitution packages covering abnormal reward losses across epochs 248, 249, and 250. All packages use [source_overrides.json](https://github.com/huxuxuya/gonka_248_and_250_-epoch_loss/blob/main/docs/source_overrides.json) as the authoritative deduplication layer — amounts already covered by another package are marked `external_proposed` and excluded, so there is no double-counting across sub-packages or with Case 2.

**Epoch 248 — Broad epoch loss (118,204.04 GNK)** | [Source](https://github.com/huxuxuya/gonka_248_and_250_-epoch_loss/tree/main/outputs/epoch_248)
Analysis revealed abnormally high loss rates: 63 of 95 participants (66%) received no or reduced rewards, accounting for 41% of the epoch's total reward pool. Multiple failure categories contributed — failed confirmation PoC, consecutive failures, statistical invalidations, and confirmation weight reductions. Given the scale and statistical significance of the loss, full restitution of all unrecovered losses was approved.

**Epoch 249 — Consecutive failures restriction (63,391.60 GNK)** | [Source](https://github.com/huxuxuya/-consensus_failure_restriction)
Three participants invalidated by the `consecutive_failures` mechanism remained blocked from reward eligibility in epoch 249 beyond the intended scope of the restriction. Their invalidation status persisted when it should have resolved, causing complete reward exclusion for that epoch.

**Epoch 249 — Remaining delta for Case 2 victims (24,597.79 GNK)** | [Source](https://github.com/huxuxuya/gonka_248_and_250_-epoch_loss/tree/main/outputs/grc_e247_preserver_audit_remaining)
Several participants affected by the Case 2 double-scaling bug suffered losses greater than what the 0.35x formula alone covers — where the weight bug compounded with a confirmation failure, resulting in zero reward for the epoch rather than just a reduced one. This package covers the remaining unpaid delta after Case 2 restitution is applied.

**Epoch 250 — Broad epoch loss, net of Case 2 and Case 3a (11,419.41 GNK)** | [Source](https://github.com/huxuxuya/gonka_248_and_250_-epoch_loss/tree/main/outputs/epoch_250)
34 of 71 participants (48%) experienced losses in epoch 250. Amounts already covered by Case 2 or the consecutive failures package are excluded per-address via source_overrides.

---

### Case 4 — Epoch 254: API Startup Blocking Issue

**Status: Accepted** | **58,375.96 GNK** | [Source](https://github.com/votkon/GRC-e254-api-issue)

Version v0.2.12-api-post2 was released between CPoC 1 and CPoC 2 (Confirmation Proof of Compute rounds) of epoch 254. This version introduced a blocking devshard migration on API startup, causing servers to be unavailable for up to 20 minutes after a container restart. Participants who applied the update promptly after CPoC 1 — as expected — had their API offline during CPoC 2, resulting in failed confirmations and zero rewards for the epoch despite passing CPoC 1.

The root fix (parallel devshard loading) shipped in v0.2.12-api-post3 only after the epoch had completed. **14 addresses** qualified for restitution based on demonstrated CPoC 1 passage and confirmed epoch-end failure.

---

## Summary

| Case | Description | Epochs | Status | GNK |
|------|-------------|--------|--------|-----|
| 1 | Inactive status mid-epoch | 247 | Rejected | — |
| 2 | Preserver weight double-scaling | 249–253 | Accepted | 30,318.50 |
| 3 | Epoch loss (broad + consecutive failures + remaining delta) | 248, 249, 250 | Accepted | 217,612.83 |
| 4 | API startup blocking issue | 254 | Accepted | 58,375.96 |
| | | | **Total** | **306,307.29 GNK** |

## Aggregated Payout List

The file [`restitution_aggregated.csv`](restitution_aggregated.csv) contains the consolidated payout list across all accepted cases: one row per address, amounts summed where the same address appears in multiple cases.

Run [`aggregate.py`](aggregate.py) to regenerate it from source:

```
python3 aggregate.py
```

The script fetches all source CSVs and JSON directly from the case repositories at runtime.
