from main import run_recommendation

def lambda_handler(event, context):

    requirements = {
        "vcpu": event["vcpu"],
        "memory_gib": event["memory_gib"],
        "network_mbps": event["network_mbps"],
        "max_price": event.get("max_price", 10.0)
    }

    results = run_recommendation(requirements)

    return {
        "recommended_instances": results
    }