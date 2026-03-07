# recommend_vm/lambda_handler.py
from main import run_recommendation

# Baseline coremark_per_core for a modern CPU
# Used to convert observed vCPU count into required_compute
BASELINE_COREMARK_PER_CORE = 27000


def lambda_handler(event, context):

    vcpu         = event["vcpu"]           # from infer_requirements
    memory_gib   = event["memory_gib"]
    network_mbps = event["network_mbps"]
    max_price    = event.get("max_price", 10.0)

    # Convert vCPU requirement → coremark_total requirement
    # e.g. 2 vCPUs * 27000 = 54000 minimum compute score
    required_compute = vcpu * BASELINE_COREMARK_PER_CORE

    requirements = {
        "required_compute": required_compute,
        "memory_gib":       memory_gib,
        "network_mbps":     network_mbps,
        "max_price":        max_price,
    }

    results = run_recommendation(requirements)

    return {"recommended_instances": results}