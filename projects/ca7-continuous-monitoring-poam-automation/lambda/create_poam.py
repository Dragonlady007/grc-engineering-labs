import os
import json
import hashlib
from datetime import datetime, timezone, timedelta

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["POAM_TABLE"])

RISK_MAP = {
    "encrypted-volumes": {
        "risk_id": "RISK-CLD-003",
        "risk_scenario": "Sensitive data exposure due to unencrypted cloud storage",
        "severity": "High",
        "likelihood": "Low",
        "impact": "High",
        "inherent_risk": "High",
        "residual_risk": "Medium",
        "risk_response": "Mitigate",
        "owner": "Infrastructure",
        "remediation_plan": "Enable encryption on affected EBS volumes or migrate data to encrypted volumes."
    }
}

DEFAULT_RISK = {
    "risk_id": "RISK-CLD-999",
    "risk_scenario": "Unmapped cloud configuration noncompliance",
    "severity": "Medium",
    "likelihood": "Medium",
    "impact": "Medium",
    "inherent_risk": "Medium",
    "residual_risk": "Medium",
    "risk_response": "Review",
    "owner": "Unassigned",
    "remediation_plan": "Review AWS Config finding and assign remediation owner."
}

def get_risk_metadata(config_rule_name):
    for rule_suffix, metadata in RISK_MAP.items():
        if config_rule_name.endswith(rule_suffix):
            return metadata
    return DEFAULT_RISK

def lambda_handler(event, context):
    detail = event.get("detail", {})
    result = detail.get("newEvaluationResult", {})

    config_rule_name = detail.get("configRuleName", "unknown-config-rule")
    compliance_type = result.get("complianceType", "UNKNOWN")

    qualifier = (
        result
        .get("evaluationResultIdentifier", {})
        .get("evaluationResultQualifier", {})
    )

    resource_id = qualifier.get("resourceId", "unknown-resource")
    resource_type = qualifier.get("resourceType", "unknown-resource-type")

    detected_date = datetime.now(timezone.utc)
    due_date = detected_date + timedelta(days=30)

    raw_finding_key = f"{config_rule_name}|{resource_type}|{resource_id}"
    finding_id = hashlib.sha256(raw_finding_key.encode()).hexdigest()[:16]

    risk_metadata = get_risk_metadata(config_rule_name)

    table.update_item(
        Key={"finding_id": finding_id},
        UpdateExpression="""
            SET
                control_id = :control_id,
                risk_id = :risk_id,
                risk_scenario = :risk_scenario,
                #source = :source,
                config_rule_name = :config_rule_name,
                resource_id = :resource_id,
                resource_type = :resource_type,
                compliance_type = :compliance_type,
                severity = :severity,
                likelihood = :likelihood,
                impact = :impact,
                inherent_risk = :inherent_risk,
                residual_risk = :residual_risk,
                risk_response = :risk_response,
                #owner = :owner,
                remediation_plan = :remediation_plan,
                #status = if_not_exists(#status, :default_status),
                poam_status = if_not_exists(poam_status, :default_poam_status),
                detected_date = if_not_exists(detected_date, :detected_date),
                due_date = if_not_exists(due_date, :due_date),
                last_updated = :last_updated
        """,
        ExpressionAttributeNames={
            "#status": "status",
            "#owner": "owner",
            "#source": "source"
        },
        ExpressionAttributeValues={
            ":control_id": "CA-7",
            ":risk_id": risk_metadata["risk_id"],
            ":risk_scenario": risk_metadata["risk_scenario"],
            ":source": "AWS Config",
            ":config_rule_name": config_rule_name,
            ":resource_id": resource_id,
            ":resource_type": resource_type,
            ":compliance_type": compliance_type,
            ":severity": risk_metadata["severity"],
            ":likelihood": risk_metadata["likelihood"],
            ":impact": risk_metadata["impact"],
            ":inherent_risk": risk_metadata["inherent_risk"],
            ":residual_risk": risk_metadata["residual_risk"],
            ":risk_response": risk_metadata["risk_response"],
            ":owner": risk_metadata["owner"],
            ":remediation_plan": risk_metadata["remediation_plan"],
            ":default_status": "Open",
            ":default_poam_status": "Open",
            ":detected_date": detected_date.isoformat(),
            ":due_date": due_date.date().isoformat(),
            ":last_updated": detected_date.isoformat()
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "CA-7 POA&M record created or updated",
            "finding_id": finding_id,
            "control_id": "CA-7",
            "risk_id": risk_metadata["risk_id"],
            "resource_id": resource_id,
            "resource_type": resource_type,
            "status": "Open"
        })
    }
