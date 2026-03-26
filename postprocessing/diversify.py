import math
import pandas as pd


def diversify(df: pd.DataFrame, per_family: int = 2, top_n: int = 10) -> pd.DataFrame:
    """
    Return up to `top_n` instances with two hard guarantees:

    1. At most `per_family` rows per provider+family combination — prevents
       one cloud's many families sweeping all slots.

    2. At least floor(top_n / n_providers) slots reserved per provider —
       prevents one cloud's better absolute scores locking out the others.

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

    def _key(row):
        return f"{row['provider']}:{row['instanceType'].split('.')[0]}"

    # Pass 1 — guaranteed quota per provider
    for provider in providers:
        for idx, row in df[df["provider"] == provider].iterrows():
            if prov_counts[provider] >= per_provider:
                break
            k = _key(row)
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
        k = _key(row)
        fam_counts.setdefault(k, 0)
        if fam_counts[k] < per_family:
            result_idx.append(idx)
            fam_counts[k] += 1

    return df.loc[result_idx]