def diversify(df, per_family: int = 2, top_n: int = 10):
    """
    Pick up to `top_n` instances, allowing at most `per_family` rows per
    provider+family combination.

    Keying on provider+family (e.g. "aws:m7i", "azure:Standard_D4as",
    "gcp:n2") instead of family alone prevents a single cloud with many
    instance families from sweeping all recommendation slots.
    """
    result = []
    counts = {}

    for _, row in df.iterrows():
        family = row["instanceType"].split(".")[0]
        key    = f"{row['provider']}:{family}"
        counts.setdefault(key, 0)
        if counts[key] < per_family:
            result.append(row)
            counts[key] += 1
        if len(result) >= top_n:
            break

    return df.loc[[r.name for r in result]]