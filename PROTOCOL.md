# DOC-2-009 R4: do assay-level descriptors (selection type, MSA depth) predict ESM-2 reliability? (frozen protocol, lock-1)

Written 2026-10-09 IST and committed BEFORE any model using these descriptors has been fit or opened.

## Connection to the prior negatives (why this question)
- DOC-2-073 (annotation depth vs rho): HONEST NEGATIVE.
- DOC-2-077 (sequence length vs rho): HONEST NEGATIVE; raw Spearman(log length, rho) = -0.232, near zero once taxon, assay class and WTLL were adjusted.
- DOC-2-009 R3 (cheap protein features): HONEST NEGATIVE. Taxon + a Tsuboyama indicator explained 0.155 of out-of-fold variance in discovery but R2 -0.002 on the external cohort; length, WTLL and annotation depth added nothing.
Reading: the protein-level features tested so far carry no transferable signal, while a crude assay-class term carried discovery signal that did not transfer. R3 listed MSA depth as "not run". R4 tests the next, finer level: the assay's measured phenotype (selection type) and MSA depth, which are ProteinGym reference fields.

## Question
Beyond taxon and the crude Tsuboyama indicator, do coarse_selection_type (Activity, Binding, Expression, OrganismalFitness, Stability) and MSA depth (log MSA_Neff_L, MSA_perc_cov) predict per-assay ESM-2 650M rho on held-out proteins and on the external year >= 2022 cohort?

## Data (frozen; md5 in INPUT_HASHES.md5)
- per_assay.csv and exposures.tsv from DOC-2-073 (rho, taxon, year, UniProt_ID); DMS_substitutions.csv (ProteinGym v1 reference, md5 c4346317..., same file as DATA_HASHES of 073; fields coarse_selection_type, MSA_Neff_L, MSA_perc_cov). No NaNs in those fields.
- Blind-spot disclosure: rho values and the R3 results exist; R3's taxon+Tsuboyama signal was seen. Selection type and MSA depth were NOT used or opened against rho before this lock. Selection type overlaps the Tsuboyama indicator (Tsuboyama assays are Stability), so G1 compares against R3's baseline, not against nothing.
- Drop assays with n_scored < 50. Discovery = year <= 2021. External = year >= 2022 with the 2 overlap proteins (DYR_ECOLI, SRC_HUMAN) removed, as in R3.

## Models (ridge lambda = 1, standardized features, numpy)
- B1 (R3 baseline): taxon dummies + Tsuboyama indicator.
- S: taxon dummies + coarse_selection_type dummies (reference Activity).
- SM: S + log(1+MSA_Neff_L) + MSA_perc_cov.
- Evaluation 1: discovery leave-one-protein-out out-of-fold R2 (reference = training-fold mean).
- Evaluation 2: fit on all discovery, predict external once; R2 reference = discovery mean.
- CI: joint protein-cluster bootstrap of the external delta R2 (SM - B1): resample discovery proteins AND external proteins, refit, 10,000 resamples, seed 12345. This includes discovery-training variance (the R3 review asked for this).
- Permutation: rows of the added features (selection-type dummies, MSA features) shuffled across discovery assays, 2000 permutations, seed 12345; statistic = external delta R2 (SM - B1).

## Gates (gate = SM vs B1)
- G1: discovery LOPO delta R2 (SM - B1) >= +0.05.
- G2: external R2(SM) > 0 and delta (SM - B1) >= +0.05 with joint bootstrap CI lower bound > 0.
- G3: permutation p < 0.05.
Labels: POSITIVE only if G1, G2 and G3 all pass; otherwise HONEST NEGATIVE. S vs B1 and per-feature numbers are reported descriptively and cannot change the label.

## Rules
No simulated data, no stubs. Synthetic smoke test only. analysis.py is run once, with a run log (command, UTC times, versions, input md5 check). Protein-level groups; wild-type-marginal scoring; CPU fp32; n about 200 assays (low power). Not run: second model, causal claims, ClinVar. Deviation budget: one tolerance line; amendments are new dated AMENDMENT-N.md files committed before outcomes exist.
