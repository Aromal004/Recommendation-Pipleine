import math
import pandas as pd


def _family_key(row) -> str:
    """
    Stable family key that works across all three providers:
      AWS:   m5.xlarge        → aws:m5
      Azure: Standard_D4s_v3  → azure:Standard_D   (first token before digit)
      GCP:   n2-standard-4    → gcp:n2
    """
    provider = row["provider"].lower()
    itype    = row["instanceType"]

    if provider == "aws":
        # AWS format: family.size  (e.g. m5.xlarge, u-6tb1.metal)
        return f"aws:{itype.split('.')[0]}"

    if provider == "azure":
        # Azure format: Standard_Xnnn_vN  — keep prefix up to first digit run
        import re
        m = re.match(r"([A-Za-z_]+)", itype)
        prefix = m.group(1).rstrip("_") if m else itype[:8]
        return f"azure:{prefix}"

    if provider == "gcp":
        # GCP format: n2-standard-4, c3d-highmem-360-lssd — keep first segment
        return f"gcp:{itype.split('-')[0]}"

    return f"{provider}:{itype[:8]}"


def diversify(df: pd.DataFrame, per_family: int = 2, top_n: int = 10) -> pd.DataFrame:
    """
    Return up to `top_n` instances with two hard guarantees:

    1. At most `per_family` rows per provider+family — prevents one cloud
       family sweeping all slots.

    2. At least floor(top_n / n_providers) slots reserved per provider —
       ensures all three clouds appear in the output.

    Strategy
    --------
    Pass 1 — fill each provider's reserved quota from their top-ranked rows.
    Pass 2 — fill remaining slots greedily in score order, respecting the
             per_family cap but no longer constrained by provider quota.
    """
    if df.empty:
        return df

    providers    = df["provider"].unique().tolist()
    n_providers  = len(providers)
    per_provider = max(1, math.floor(top_n / n_providers))

    result_idx  = []
    fam_counts  = {}
    prov_counts = {p: 0 for p in providers}

    # Pass 1 — guaranteed quota per provider
    for provider in providers:
        for idx, row in df[df["provider"] == provider].iterrows():
            if prov_counts[provider] >= per_provider:
                break
            k = _family_key(row)
            fam_counts.setdefault(k, 0)
            if fam_counts[k] < per_family:
                result_idx.append(idx)
                fam_counts[k] += 1
                prov_counts[provider] += 1

    # Pass 2 — fill remaining slots in global score order
    for idx, row in df.iterrows():
        if len(result_idx) >= top_n:
            break
        if idx in result_idx:
            continue
        k = _family_key(row)
        fam_counts.setdefault(k, 0)
        if fam_counts[k] < per_family:
            result_idx.append(idx)
            fam_counts[k] += 1

    return df.loc[result_idx]