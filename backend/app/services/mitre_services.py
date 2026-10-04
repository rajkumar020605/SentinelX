MITRE_MAPPINGS = {
    "BRUTE_FORCE_LOGIN": {
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "tactic": "Credential Access",
        "description": (
            "Adversaries may use brute force techniques "
            "to gain access to accounts."
        ),
        "url": "https://attack.mitre.org/techniques/T1110/"
    },

    "SUSPICIOUS_LOGIN": {
        "technique_id": "T1078",
        "technique_name": "Valid Accounts",
        "tactic": "Initial Access",
        "additional_tactics": [
            "Persistence",
            "Privilege Escalation",
            "Defense Evasion"
        ],
        "description": (
            "Adversaries may obtain and abuse legitimate "
            "accounts to gain or maintain access."
        ),
        "url": "https://attack.mitre.org/techniques/T1078/"
    }
}


def get_mitre_mapping(detection_rule: str | None):
    if not detection_rule:
        return None

    return MITRE_MAPPINGS.get(detection_rule)


def get_all_mitre_mappings():
    return MITRE_MAPPINGS