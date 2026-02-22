import pandas as pd
import boto3
from io import StringIO

from preprocessing.feature_engineering import add_features
from preprocessing.hard_filter import hard_filter
from scoring.fit_score import add_fit_score
from optimization.bayesian_ranker import optimize_weights
from scoring.final_scorer import rank_instances
from postprocessing.diversify import diversify


def load_dataset():
    s3 = boto3.client("s3")
    obj = s3.get_object(
        Bucket="vm-recommendation-data",
        Key="aws_ec2_full_dataset.csv"
    )
    return pd.read_csv(obj["Body"])


def run_recommendation(requirements):

    df = load_dataset()
    df = df[df["price_per_hr"] > 0]

    df = add_features(df)

    # Stage 1
    df = hard_filter(df, requirements)
    if df.empty:
        return {"error": "No instances satisfy constraints"}

    # Stage 2
    df = add_fit_score(df, requirements)

    # Stage 3
    weights = optimize_weights(df)

    # Stage 4
    ranked = rank_instances(df, weights)

    final = diversify(ranked, per_family=2, top_n=10)

    return final[
        ["instanceType", "vcpu", "memory_gib",
         "network_mbps", "price_per_hr", "final_score"]
    ].to_dict(orient="records")