"""DOC-2-009 R4 frozen analysis (PROTOCOL.md lock-1). Run once."""
import json, numpy as np, pandas as pd
rng = np.random.default_rng(12345)
a = pd.read_csv("per_assay.csv"); e = pd.read_csv("exposures.tsv", sep="\t").drop(columns=["seq_len"])
ref = pd.read_csv("DMS_substitutions.csv")[["DMS_id", "coarse_selection_type", "MSA_Neff_L", "MSA_perc_cov"]]
d = a.merge(e, on="DMS_id").merge(ref, on="DMS_id"); d = d[d.rho.notna() & (d.n_scored >= 50)].reset_index(drop=True)
d["tsub"] = d.DMS_id.str.contains("Tsuboyama_2023").astype(float); d["lneff"] = np.log1p(d.MSA_Neff_L)
SEL = ["Binding", "Expression", "OrganismalFitness", "Stability"]
ov = set(d[d.year <= 2021].UniProt_ID) & set(d[d.year >= 2022].UniProt_ID)
disc = d[d.year <= 2021].reset_index(drop=True); ext = d[(d.year >= 2022) & (~d.UniProt_ID.isin(ov))].reset_index(drop=True)
TX = ["Eukaryote", "Prokaryote", "Virus"]
def X(df, k):
    c = [(df.taxon == t).astype(float).values for t in TX]
    if k == "B1": c.append(df.tsub.values)
    if k in ("S", "SM"): c += [(df.coarse_selection_type == s).astype(float).values for s in SEL]
    if k == "SM": c += [df.lneff.values, df.MSA_perc_cov.values]
    return np.column_stack(c)
def fp(Xtr, ytr, Xte, lam=1.0):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9; A = (Xtr - mu) / sd; B = (Xte - mu) / sd
    w = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ (ytr - ytr.mean())); return B @ w + ytr.mean()
def lopo(df, k):
    Xa = X(df, k); y = df.rho.values; pred = np.zeros(len(df)); ref_ = np.zeros(len(df))
    for p in df.UniProt_ID.unique():
        te = (df.UniProt_ID == p).values; tr = ~te; pred[te] = fp(Xa[tr], y[tr], Xa[te]); ref_[te] = y[tr].mean()
    return 1 - ((y - pred) ** 2).sum() / ((y - ref_) ** 2).sum()
def ext_r2(tr, te, k, Xtr=None):
    Xt = X(tr, k) if Xtr is None else Xtr; p = fp(Xt, tr.rho.values, X(te, k)); y = te.rho.values
    return 1 - ((y - p) ** 2).sum() / ((y - tr.rho.mean()) ** 2).sum()
res = {"n_disc": len(disc), "n_ext": len(ext), "overlap_removed": sorted(ov)}
r = {k: lopo(disc, k) for k in ["B1", "S", "SM"]}
res["G1"] = dict(lopo_r2=r, delta_SM_minus_B1=r["SM"] - r["B1"], delta_S_minus_B1=r["S"] - r["B1"], pass_=bool(r["SM"] - r["B1"] >= 0.05))
e1, es, em = (ext_r2(disc, ext, k) for k in ["B1", "S", "SM"]); delta = em - e1
def prots_blocks(df): return {p: df[df.UniProt_ID == p] for p in df.UniProt_ID.unique()}
gd, ge = prots_blocks(disc), prots_blocks(ext); pd_, pe = list(gd), list(ge); bs = []
for _ in range(10000):
    sd = pd.concat([gd[p] for p in rng.choice(pd_, len(pd_))]).reset_index(drop=True)
    se = pd.concat([ge[p] for p in rng.choice(pe, len(pe))]).reset_index(drop=True)
    if ((se.rho - sd.rho.mean()) ** 2).sum() > 0: bs.append(ext_r2(sd, se, "SM") - ext_r2(sd, se, "B1"))
ci = list(np.percentile(bs, [2.5, 97.5]))
res["G2"] = dict(ext_r2=dict(B1=e1, S=es, SM=em), delta_SM_minus_B1=delta, delta_S_minus_B1=es - e1, ci_joint=ci, pass_=bool(em > 0 and delta >= 0.05 and ci[0] > 0))
cols = ["coarse_selection_type", "lneff", "MSA_perc_cov"]; perm = []
for _ in range(2000):
    dd = disc.copy(); idx = rng.permutation(len(dd))
    for c in cols: dd[c] = disc[c].values[idx]
    perm.append(ext_r2(dd, ext, "SM") - e1)
pv = (1 + sum(x >= delta for x in perm)) / (1 + len(perm)); res["G3"] = dict(perm_p=pv, pass_=bool(pv < 0.05))
res["LABEL"] = "POSITIVE" if all(res[g]["pass_"] for g in ["G1", "G2", "G3"]) else "HONEST NEGATIVE"
print("RESULT_JSON", json.dumps(res, default=float)); open("results.json", "w").write(json.dumps(res, default=float, indent=1))
