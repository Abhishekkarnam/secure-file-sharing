ATTACK_SCENARIOS = {
    "Unauthorized Access": {
        "severity": "HIGH",
        "message": "Unauthorized access attempt detected and blocked before file retrieval.",
        "status": "BLOCKED",
    },
    "MITM Interception": {
        "severity": "CRITICAL",
        "message": "Potential man-in-the-middle behavior detected. Encrypted payload integrity preserved.",
        "status": "BLOCKED",
    },
    "Brute Force": {
        "severity": "HIGH",
        "message": "Repeated credential attempt pattern detected. Login protection response triggered.",
        "status": "BLOCKED",
    },
}

ALIASES = {
    "MITM Simulation": "MITM Interception",
    "MITM Intersection": "MITM Interception",
}


def run_simulation(attack_type):
    normalized_type = ALIASES.get(attack_type, attack_type)
    scenario = ATTACK_SCENARIOS.get(normalized_type)

    if not scenario:
        return {
            "attack_type": attack_type or "Unknown",
            "severity": "LOW",
            "message": "Unknown simulation type rejected.",
            "status": "REJECTED",
        }

    return {
        "attack_type": normalized_type,
        "severity": scenario["severity"],
        "message": scenario["message"],
        "status": scenario["status"],
    }
