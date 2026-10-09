# DOC-2-009 R4 results (frozen analysis, PROTOCOL.md lock-1 = 74a4cae; no post-hoc changes to gates)

Label (set mechanically by analysis.py): HONEST NEGATIVE. G1, G2 and G3 all fail. Independent gate review is pending; no claim is made until it clears.

**AMENDMENT-1 (input note, committed pre-outcome):** the repo copy of DMS_substitutions.csv is 208,518 bytes (218 LF, 0 CR); the GitHub web editor changed its line endings relative to the upstream file. The analysis ran on a local copy whose md5 equals the stated upstream md5 c434631737013fceb56efc98056151e0 (builder run_log). The repo copy differs in bytes but parses to the same 217 x 46 frame (gate-verified: results bit-identical on the LF repo copy and an LF->CRLF copy). The upstream bytes are not independently verifiable by the gate. Earlier byte counts written here (208734 -> 208519) were wrong and are withdrawn.

## Results (ESM-2 650M wt-marginal rho, 204 assays; ridge lambda 1)
- Sets: discovery n=98 (year <= 2021); external n=103 (year >= 2022, 2 overlap proteins removed).
- G1 (discovery leave-one-protein-out R2): B1 0.155, S (taxon + selection type) 0.106, SM (S + MSA depth) 0.197. Delta SM-B1 = +0.042 (needed >= +0.05). Fail, close to the threshold. Descriptive: S minus B1 = -0.049, so selection type alone did not help; the +0.042 comes from adding MSA depth.
- G2 (external, fit on discovery once): R2 B1 -0.002, S -1.277, SM -1.722. Delta SM-B1 = -1.720, joint-bootstrap 95% CI [-3.10, +0.20] (resamples discovery and external proteins and refits, 10,000, seed 12345). Fail.
- G3 (permutation of the added features across discovery assays, 2000): p = 0.886. Fail.

## Why G2 is uninformative (a design limit found after the run, not a result change)
Selection type is almost perfectly confounded with the discovery/external split. Assays by coarse_selection_type (discovery / external): Activity 21 / 18, Binding 10 / 2, Expression 11 / 7, OrganismalFitness 55 / 12, Stability 1 / 64 (external counts are the analysed n_ext = 103; 3 overlap-removed assays are excluded). The 64 external Stability assays (63 of them Tsuboyama 2023; Stability total 65 = 63 Tsuboyama + 1 discovery + 1 other external) are extrapolated from a single discovery Stability assay, so the Stability coefficient is essentially unidentified and the external R2 of S and SM collapses. G2 is uninformative about whether selection type predicts reliability; it is not evidence that selection type does not matter. It only reflects that a selection-type model trained on pre-2022 assays does not extrapolate to the 2023 stability compendium. The protocol did not check the split's selection-type balance before lock-1; that is a protocol flaw, disclosed here, and it was not repaired after seeing outcomes. The label stays HONEST NEGATIVE as defined by the gates.

## Disclosures and limits
- The R3 result (taxon + Tsuboyama gave discovery LOPO R2 0.155 but external -0.002) was seen before this lock. Selection type overlaps the Tsuboyama indicator (Tsuboyama assays are Stability).
- Related finding that affects DOC-2-009 R3: Tsuboyama 2023 assays are all in the external set (0 in discovery, 63 in external), so the R3 "Tsuboyama indicator" was constant zero in discovery and could not be learned. R3's B1 R2 of 0.155 was therefore carried by taxon alone, not by "taxon + assay class" as R3's descriptive line said. B1 here is the same R3 baseline.
- Length, WTLL and annotation were examined in 073, 077 and R3 (HONEST NEGATIVES). Low power (n about 200); protein-level groups only; wild-type-marginal scoring; CPU fp32. Second model, causal claims and ClinVar: not run.
- "analysis.py was run once after a synthetic smoke test" is a builder statement, not repo evidence. run_log.txt records the command, UTC start 14:18:10Z and end 14:22:18Z, python 3.10.12, numpy 2.2.6, pandas 2.3.3, input md5 check (all OK) and exit 0. input_check.txt is a post-run re-check (committed after the run): it shows the files match now, not at run time.
- The G2 CI is a joint bootstrap (it includes discovery-training variance), which is why it is much wider than R3's.

- Lock-history oddity (no content issue): commit 8c4e18b, message "Update print statement from Hello to Goodbye", added DMS_substitutions.csv. The message is misleading; the content is the frozen input.
